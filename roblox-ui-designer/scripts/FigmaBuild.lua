--[[ FigmaBuild: builds real Roblox GUI instances from a normalized Figma node tree (see figma_walker.js / figma_normalize.py).

Called by figma_to_luau.py, which appends:  return FigmaBuild(tree, assets, options)
  tree     normalized node (JSON-decoded table): id name type x y w h rotation visible opacity fills strokes strokeWeight
           strokeAlign cornerRadius radii effects layoutMode itemSpacing padding primaryAlign counterAlign wrap sizingH
           sizingV absolute clips constraints text children
  assets   { [nodeId] = "rbxassetid://..." }  for image fills and layers baked to PNG (name ends in _img)
  options  { parent = Instance?, screenGui = bool, name = string, scaleRoot = bool }

Layer-name suffixes (set them in Figma):
  _img     bake: whole layer is one ImageLabel from assets[id] (use for anything Roblox can't draw: blur, blend modes,
           radial gradients, inner shadows, custom lettering, textures)
  _btn     becomes a TextButton/ImageButton (AutoButtonColor off; hover/press animation is added in code, not here)
  _scroll  ScrollingFrame with AutomaticCanvasSize
  _ignore  skipped
Returns root instance, report string (warnings for anything approximated).
]]
local HttpService = game:GetService("HttpService")

local warnings = {}
local function warn_(node, msg)
	table.insert(warnings, string.format("%s (%s): %s", node.name or "?", node.id or "?", msg))
end

local function rgb(c)
	return Color3.new(c.r or 0, c.g or 0, c.b or 0)
end

local function try(node, what, fn)
	local ok, err = pcall(fn)
	if not ok then
		warn_(node, what .. " not applied (" .. tostring(err):sub(1, 80) .. ")")
	end
	return ok
end

-- fonts: Figma family -> Enum.Font name (verified at runtime; unknown families fall back to BuilderSans + warning)
local FAMILY = {
	["Inter"] = "BuilderSans", ["Builder Sans"] = "BuilderSans", ["Gotham"] = "Montserrat", ["Gotham SSm"] = "Montserrat",
	["Montserrat"] = "Montserrat", ["Roboto"] = "Roboto", ["Roboto Condensed"] = "RobotoCondensed",
	["Roboto Mono"] = "RobotoMono", ["Oswald"] = "Oswald", ["Source Sans Pro"] = "SourceSans",
	["Titillium Web"] = "TitilliumWeb", ["Michroma"] = "Michroma", ["Sarpanch"] = "Sarpanch", ["Jura"] = "Jura",
	["Ubuntu"] = "Ubuntu", ["Nunito"] = "Nunito", ["Merriweather"] = "Merriweather", ["Bangers"] = "Bangers",
	["Special Elite"] = "SpecialElite", ["Permanent Marker"] = "PermanentMarker", ["Arimo"] = "Arimo",
	["Josefin Sans"] = "JosefinSans", ["Press Start 2P"] = "Arcade", ["Fredoka One"] = "FredokaOne",
	["Luckiest Guy"] = "LuckiestGuy", ["Kalam"] = "Kalam", ["Patrick Hand"] = "PatrickHand", ["Creepster"] = "Creepster",
}
local WEIGHT = { [100] = "Thin", [200] = "ExtraLight", [300] = "Light", [400] = "Regular", [500] = "Medium",
	[600] = "SemiBold", [700] = "Bold", [800] = "ExtraBold", [900] = "Heavy" }

local function fontFor(node, t)
	local enumName = FAMILY[t.fontFamily or ""] or (t.fontFamily or ""):gsub("%s", "")
	local base
	local ok = pcall(function()
		base = Font.fromEnum(Enum.Font[enumName])
	end)
	if not ok or not base then
		warn_(node, "font '" .. tostring(t.fontFamily) .. "' not in Roblox's library -> BuilderSans (bake hero lettering as _img)")
		base = Font.fromEnum(Enum.Font.BuilderSans)
	end
	local w = math.clamp(math.floor(((t.fontWeight or 400) + 50) / 100) * 100, 100, 900)
	local style = t.italic and Enum.FontStyle.Italic or Enum.FontStyle.Normal
	return Font.new(base.Family, Enum.FontWeight[WEIGHT[w]], style)
end

-- position/size from Figma constraints, relative to the parent's size (pw, ph)
local function placeAxis(c, pos, size, parentSize)
	if c == "RIGHT" or c == "BOTTOM" then
		return UDim.new(1, -(parentSize - pos)), UDim.new(0, size), 0
	elseif c == "CENTER" then
		return UDim.new(0.5, pos - parentSize / 2), UDim.new(0, size), 0
	elseif c == "LEFT_RIGHT" or c == "TOP_BOTTOM" then
		return UDim.new(0, pos), UDim.new(1, -(parentSize - size)), 0
	elseif c == "SCALE" then
		return UDim.new(pos / parentSize, 0), UDim.new(size / parentSize, 0), 0
	end
	return UDim.new(0, pos), UDim.new(0, size), 0
end

local function applyFill(node, inst, isText)
	local fills = {}
	for _, f in node.fills or {} do
		if f.visible ~= false then table.insert(fills, f) end
	end
	if isText then
		inst.BackgroundTransparency = 1
		return
	end
	if #fills == 0 then
		inst.BackgroundTransparency = 1
		return
	end
	if #fills > 1 then
		warn_(node, #fills .. " fills: only the top one is used (stack layers or bake as _img)")
	end
	local f = fills[#fills] -- Figma paints bottom -> top; last is on top
	local alpha = (f.opacity or 1) * ((f.color and f.color.a) or 1)
	if f.type == "SOLID" then
		inst.BackgroundColor3 = rgb(f.color)
		inst.BackgroundTransparency = 1 - alpha
	elseif f.type == "GRADIENT_LINEAR" and f.stops and f.handles then
		inst.BackgroundColor3 = Color3.new(1, 1, 1) -- UIGradient multiplies
		inst.BackgroundTransparency = 0
		local g = Instance.new("UIGradient")
		local stops = f.stops
		if #stops > 20 then
			warn_(node, "gradient has " .. #stops .. " stops; Roblox allows 20, extra dropped")
		end
		local ck, tk = {}, {}
		local n = math.min(#stops, 20)
		for i = 1, n do
			local s = stops[i]
			local p = math.clamp(s.position, 0, 1)
			if i == 1 then p = 0 end
			if i == n then p = 1 end
			if #ck > 0 and p <= ck[#ck].Time then p = math.min(1, ck[#ck].Time + 0.001) end
			table.insert(ck, ColorSequenceKeypoint.new(p, rgb(s.color)))
			table.insert(tk, NumberSequenceKeypoint.new(p, 1 - (s.color.a or 1) * (f.opacity or 1)))
		end
		if n == 1 then
			ck[2] = ColorSequenceKeypoint.new(1, ck[1].Value); tk[2] = NumberSequenceKeypoint.new(1, tk[1].Value)
		end
		g.Color = ColorSequence.new(ck)
		g.Transparency = NumberSequence.new(tk)
		local h0, h1 = f.handles[1], f.handles[2]
		g.Rotation = math.deg(math.atan2((h1.y - h0.y) * node.h, (h1.x - h0.x) * node.w))
		g.Parent = inst
	elseif f.type == "IMAGE" then
		-- handled by the ImageLabel path in build()
	else
		warn_(node, f.type .. " fill can't be drawn natively (radial/angular/diamond) -> name the layer _img to bake it")
		inst.BackgroundTransparency = 1
	end
end

local function applyStroke(node, inst, isText)
	local s
	for _, st in node.strokes or {} do
		if st.visible ~= false then s = st end
	end
	if not s or (node.strokeWeight or 0) <= 0 then return end
	local k = Instance.new("UIStroke")
	k.Color = rgb(s.color or {})
	k.Transparency = 1 - (s.opacity or 1) * ((s.color and s.color.a) or 1)
	k.Thickness = node.strokeWeight
	k.ApplyStrokeMode = isText and Enum.ApplyStrokeMode.Contextual or Enum.ApplyStrokeMode.Border
	k.LineJoinMode = Enum.LineJoinMode.Round
	if not isText and node.strokeAlign then
		-- Figma INSIDE/CENTER/OUTSIDE; Roblox's stroke position property (2026) - enum names verified at runtime
		local want = ({ INSIDE = "Inner", CENTER = "Center", OUTSIDE = "Outer" })[node.strokeAlign]
		if want then
			pcall(function() k.BorderStrokePosition = Enum.BorderStrokePosition[want] end)
		end
	end
	k.Parent = inst
end

local function applyCorners(node, inst)
	local r = node.cornerRadius or 0
	local radii = node.radii
	if r <= 0 and not radii then return end
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, r)
	if radii then -- per-corner (UICorner per-corner radii, 2026)
		local names = { "TopLeftRadius", "TopRightRadius", "BottomRightRadius", "BottomLeftRadius" }
		local okAll = true
		for i, nm in names do
			okAll = pcall(function() c[nm] = UDim.new(0, radii[i]) end) and okAll
		end
		if not okAll then
			c.CornerRadius = UDim.new(0, math.max(radii[1], radii[2], radii[3], radii[4]))
			warn_(node, "per-corner radii unsupported here -> uniform radius")
		end
	end
	c.Parent = inst
end

local function applyEffects(node, inst)
	for _, e in node.effects or {} do
		if e.visible == false then continue end
		if e.type == "DROP_SHADOW" then
			local ok = pcall(function()
				local sh = Instance.new("UIShadow")
				sh.Color = rgb(e.color or {})
				sh.Transparency = 1 - ((e.color and e.color.a) or 0.25)
				-- UIShadow (2026): BlurRadius UDim, Offset UDim2, Spread UDim2, ZIndex negative
				sh.BlurRadius = UDim.new(0, e.radius or 8)
				local off = e.offset or { x = 0, y = 0 }
				sh.Offset = UDim2.fromOffset(off.x, off.y)
				sh.Spread = UDim2.fromOffset(e.spread or 0, e.spread or 0)
				sh.Parent = inst
			end)
			if not ok then warn_(node, "UIShadow unavailable -> drop shadow skipped (use a 9-slice shadow image)") end
		else
			warn_(node, e.type .. " can't be drawn natively -> name the layer _img to bake it")
		end
	end
end

local function applyAutoLayout(node, inst)
	local mode = node.layoutMode
	if not mode or mode == "NONE" then return end
	if mode == "GRID" then
		warn_(node, "grid auto layout -> UIGridLayout needs manual cell sizes; using a wrapping list instead")
	end
	local l = Instance.new("UIListLayout")
	l.FillDirection = mode == "VERTICAL" and Enum.FillDirection.Vertical or Enum.FillDirection.Horizontal
	l.SortOrder = Enum.SortOrder.LayoutOrder
	l.Padding = UDim.new(0, node.itemSpacing or 0)
	local main = ({ MIN = "Left", CENTER = "Center", MAX = "Right" })
	local cross = ({ MIN = "Top", CENTER = "Center", MAX = "Bottom" })
	if mode == "VERTICAL" then
		l.VerticalAlignment = Enum.VerticalAlignment[cross[node.primaryAlign or "MIN"] or "Top"]
		l.HorizontalAlignment = Enum.HorizontalAlignment[main[node.counterAlign or "MIN"] or "Left"]
	else
		l.HorizontalAlignment = Enum.HorizontalAlignment[main[node.primaryAlign or "MIN"] or "Left"]
		l.VerticalAlignment = Enum.VerticalAlignment[cross[node.counterAlign or "MIN"] or "Top"]
	end
	if node.primaryAlign == "SPACE_BETWEEN" then
		try(node, "space-between", function()
			if mode == "VERTICAL" then l.VerticalFlex = Enum.UIFlexAlignment.SpaceBetween
			else l.HorizontalFlex = Enum.UIFlexAlignment.SpaceBetween end
		end)
	end
	if node.wrap or mode == "GRID" then
		try(node, "wrap", function() l.Wraps = true end)
	end
	l.Parent = inst
	local p = node.padding
	if p and ((p.t or 0) + (p.r or 0) + (p.b or 0) + (p.l or 0)) > 0 then
		local pad = Instance.new("UIPadding")
		pad.PaddingTop, pad.PaddingRight = UDim.new(0, p.t or 0), UDim.new(0, p.r or 0)
		pad.PaddingBottom, pad.PaddingLeft = UDim.new(0, p.b or 0), UDim.new(0, p.l or 0)
		pad.Parent = inst
	end
end

local function build(node, parentNode, parentLayout, index)
	if node.visible == false or (node.name or ""):match("_ignore$") then return nil end
	local name = node.name or node.type
	local isText = node.type == "TEXT"
	local bake = name:match("_img$") ~= nil
	local imageFill
	for _, f in node.fills or {} do
		if f.type == "IMAGE" and f.visible ~= false then imageFill = f end
	end
	local hasKids = node.children and #node.children > 0 and not bake

	local class
	if isText then
		class = name:match("_btn$") and "TextButton" or "TextLabel"
	elseif bake or imageFill then
		class = name:match("_btn$") and "ImageButton" or "ImageLabel"
	elseif name:match("_scroll$") then
		class = "ScrollingFrame"
	elseif name:match("_btn$") then
		class = "TextButton"
	elseif hasKids and (node.opacity or 1) < 0.999 then
		class = "CanvasGroup" -- group opacity; costs a texture, keep rare
	else
		class = "Frame"
	end
	local inst = Instance.new(class)
	inst.Name = name
	inst.BorderSizePixel = 0
	inst.ZIndex = index or 1

	-- geometry
	if parentLayout and not node.absolute then
		inst.Size = UDim2.fromOffset(node.w, node.h)
		inst.LayoutOrder = index or 0
		local fillW, fillH = node.sizingH == "FILL", node.sizingV == "FILL"
		if fillW or fillH then
			local horizontal = parentNode.layoutMode ~= "VERTICAL"
			local mainFill = (horizontal and fillW) or (not horizontal and fillH)
			local crossFill = (horizontal and fillH) or (not horizontal and fillW)
			if mainFill then
				try(node, "flex fill", function()
					local fx = Instance.new("UIFlexItem"); fx.FlexMode = Enum.UIFlexMode.Fill; fx.Parent = inst
				end)
			end
			if crossFill then
				inst.Size = horizontal and UDim2.new(inst.Size.X, UDim.new(1, 0)) or UDim2.new(UDim.new(1, 0), inst.Size.Y)
			end
		end
	elseif parentNode then
		local c = node.constraints or {}
		local px, sx = placeAxis(c.horizontal or "LEFT", node.x, node.w, parentNode.w)
		local py, sy = placeAxis(c.vertical or "TOP", node.y, node.h, parentNode.h)
		-- RIGHT/BOTTOM anchor on the far edge
		local ax = (c.horizontal == "RIGHT") and 1 or 0
		local ay = (c.vertical == "BOTTOM") and 1 or 0
		if ax == 1 then px = UDim.new(1, -(parentNode.w - node.x - node.w)) end
		if ay == 1 then py = UDim.new(1, -(parentNode.h - node.y - node.h)) end
		inst.AnchorPoint = Vector2.new(ax, ay)
		inst.Position = UDim2.new(px, py)
		inst.Size = UDim2.new(sx, sy)
		if parentLayout and node.absolute then
			warn_(node, "absolute-positioned child inside auto layout: Roblox layouts position every child; wrap it in its own overlay frame")
		end
	end
	if node.sizingH == "HUG" or node.sizingV == "HUG" then
		local ax = (node.sizingH == "HUG" and node.sizingV == "HUG") and Enum.AutomaticSize.XY
			or (node.sizingH == "HUG" and Enum.AutomaticSize.X or Enum.AutomaticSize.Y)
		if not isText or node.text and node.text.autoResize ~= "NONE" then
			inst.AutomaticSize = ax
		end
	end
	if node.rotation and math.abs(node.rotation) > 0.01 then
		inst.Rotation = -node.rotation -- Figma counter-clockwise, Roblox clockwise
		warn_(node, "rotated layer: Roblox rotates about the centre, check its position")
	end

	-- paint
	if class == "ImageLabel" or class == "ImageButton" then
		inst.BackgroundTransparency = 1
		inst.Image = assets[node.id] or ""
		if inst.Image == "" then warn_(node, "no uploaded asset for this image/_img layer yet") end
		local mode = imageFill and imageFill.scaleMode
		inst.ScaleType = ({ FILL = Enum.ScaleType.Crop, FIT = Enum.ScaleType.Fit, TILE = Enum.ScaleType.Tile })[mode or ""]
			or Enum.ScaleType.Stretch
		if node.slice then -- 9-slice: {l,t,r,b} in source px (export @2x -> SliceScale .5)
			inst.ScaleType = Enum.ScaleType.Slice
			inst.SliceCenter = Rect.new(node.slice[1], node.slice[2], node.slice[3], node.slice[4])
			inst.SliceScale = node.sliceScale or 0.5
		end
		if not bake then applyCorners(node, inst) end
	else
		applyFill(node, inst, isText)
		applyCorners(node, inst)
	end
	if not bake then
		applyStroke(node, inst, isText)
		applyEffects(node, inst)
	end
	if class == "CanvasGroup" then
		inst.GroupTransparency = 1 - node.opacity
	elseif (node.opacity or 1) < 0.999 and not hasKids then
		local o = node.opacity
		if inst:IsA("GuiObject") then
			inst.BackgroundTransparency = 1 - (1 - inst.BackgroundTransparency) * o
		end
		if inst:IsA("ImageLabel") or inst:IsA("ImageButton") then inst.ImageTransparency = 1 - o end
	end
	if node.clips then inst.ClipsDescendants = true end
	if class == "ScrollingFrame" then
		inst.AutomaticCanvasSize = node.layoutMode == "HORIZONTAL" and Enum.AutomaticSize.X or Enum.AutomaticSize.Y
		inst.CanvasSize = UDim2.new()
		inst.ScrollBarThickness = 4
		inst.ScrollingDirection = node.layoutMode == "HORIZONTAL" and Enum.ScrollingDirection.X or Enum.ScrollingDirection.Y
	end
	if inst:IsA("GuiButton") then inst.AutoButtonColor = false end

	-- text
	if isText and node.text then
		local t = node.text
		inst.Text = t.characters or ""
		inst.FontFace = fontFor(node, t)
		inst.TextSize = t.fontSize or 14
		inst.TextWrapped = true
		inst.RichText = t.rich == true
		local fill
		for _, f in node.fills or {} do
			if f.visible ~= false and f.type == "SOLID" then fill = f end
		end
		if fill then
			inst.TextColor3 = rgb(fill.color)
			inst.TextTransparency = 1 - (fill.opacity or 1) * (fill.color.a or 1) * (node.opacity or 1)
		end
		if t.lineHeightPx and t.fontSize then inst.LineHeight = math.clamp(t.lineHeightPx / t.fontSize, 0.5, 3) end
		inst.TextXAlignment = ({ LEFT = Enum.TextXAlignment.Left, CENTER = Enum.TextXAlignment.Center,
			RIGHT = Enum.TextXAlignment.Right, JUSTIFIED = Enum.TextXAlignment.Left })[t.alignH or "LEFT"]
		inst.TextYAlignment = ({ TOP = Enum.TextYAlignment.Top, CENTER = Enum.TextYAlignment.Center,
			BOTTOM = Enum.TextYAlignment.Bottom })[t.alignV or "TOP"]
		if t.letterSpacing and math.abs(t.letterSpacing) > 0.01 then
			warn_(node, "letter spacing isn't supported in Roblox text -> dropped (bake as _img if it matters)")
		end
		if t.textCase == "UPPER" then inst.Text = string.upper(inst.Text) end
	elseif inst:IsA("TextButton") then
		inst.Text = ""
	end

	-- children
	if hasKids and not bake then
		local layout = node.layoutMode and node.layoutMode ~= "NONE"
		applyAutoLayout(node, inst)
		for i, child in node.children do
			local ci = build(child, node, layout, i)
			if ci then ci.Parent = inst end
		end
	end
	return inst
end

function FigmaBuild(tree, assetMap, options)
	options = options or {}
	assets = assetMap or {}
	warnings = {}
	local root = build(tree, nil, false, 1)
	root.Position = UDim2.fromScale(0.5, 0.5)
	root.AnchorPoint = Vector2.new(0.5, 0.5)
	if options.scaleRoot ~= false then
		-- the frame is authored at its Figma size (e.g. 1920x1080); a UIScale keeps every Offset proportional on any
		-- screen. Runtime code updates it: scale = min(viewport.X / designW, viewport.Y / designH)
		root.Size = UDim2.fromOffset(tree.w, tree.h)
		local s = Instance.new("UIScale")
		s.Name = "DesignScale"
		s:SetAttribute("DesignSize", Vector2.new(tree.w, tree.h))
		s.Parent = root
	else
		root.Size = UDim2.fromScale(1, 1)
	end
	root.BackgroundTransparency = options.keepRootBackground and root.BackgroundTransparency or 1
	local out = root
	if options.screenGui then
		local sg = Instance.new("ScreenGui")
		sg.Name = options.name or tree.name
		sg.ResetOnSpawn = false
		sg.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
		sg.IgnoreGuiInset = true
		pcall(function() sg.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets end)
		root.Parent = sg
		out = sg
	end
	if options.parent then out.Parent = options.parent end
	local count = 0
	for _ in out:GetDescendants() do count += 1 end
	return out, string.format("%d instances; %d warnings\n%s", count + 1, #warnings, table.concat(warnings, "\n"))
end
