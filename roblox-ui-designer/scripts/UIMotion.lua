--[[ UIMotion: small, tested motion kit for Roblox ScreenGuis (ModuleScript). Copy into ReplicatedStorage and require it.
Every animation here is interruptible, respects GuiService.ReducedMotionEnabled and cleans up after itself.

  UIMotion.fitDesignScale(root)            keep a Figma-sized frame (with a UIScale "DesignScale") fitted to any screen
  UIMotion.button(btn, opts?)              hover/press/release feel (mouse, touch, gamepad) via UIScale; returns cleanup
  UIMotion.panel(frame, opts?)             open/close state machine (fade + slide/scale); :open() :close() :toggle()
  UIMotion.ghostBar(fill, ghost)           health bar with delayed "chip" drain; returns setFraction(f)
  UIMotion.countUp(label, from, to, t, fmt) number ticker
  UIMotion.typewrite(label, cps)           reveal text without re-layout (MaxVisibleGraphemes)
  UIMotion.shine(overlay, t?)              diagonal shine sweep over an overlay with a UIGradient
  UIMotion.stagger(items, fn, step?, cap?) run fn(item, i) with capped per-item delays (lists appearing)
  UIMotion.damp(current, target, halfLife, dt)  frame-rate independent smoothing for per-frame followers
]]
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")
local Workspace = game:GetService("Workspace")

local UIMotion = {}

UIMotion.T = { -- timing tokens (seconds) - keep every screen on these
	instant = 0.07, hover = 0.14, press = 0.07, release = 0.2, open = 0.26, close = 0.17, toast = 0.25,
}
local function info(t, style, dir)
	return TweenInfo.new(t, style or Enum.EasingStyle.Quint, dir or Enum.EasingDirection.Out)
end
UIMotion.ease = {
	enter = function(t) return info(t, Enum.EasingStyle.Quint, Enum.EasingDirection.Out) end,
	exit = function(t) return info(t, Enum.EasingStyle.Quad, Enum.EasingDirection.In) end,
	pop = function(t) return info(t, Enum.EasingStyle.Back, Enum.EasingDirection.Out) end, -- confirmations only
	move = function(t) return info(t, Enum.EasingStyle.Quint, Enum.EasingDirection.InOut) end,
}

function UIMotion.reduced()
	return GuiService.ReducedMotionEnabled
end

-- one live tween per (instance, channel); a new one cancels the old so nothing fights
local live = setmetatable({}, { __mode = "k" })
function UIMotion.tween(inst, tinfo, props, channel)
	channel = channel or "default"
	live[inst] = live[inst] or {}
	local old = live[inst][channel]
	if old then old:Cancel() end
	if UIMotion.reduced() then
		for k, v in props do inst[k] = v end
		return nil
	end
	local tw = TweenService:Create(inst, tinfo, props)
	live[inst][channel] = tw
	tw:Play()
	return tw
end

local function uiscale(obj)
	local s = obj:FindFirstChild("MotionScale")
	if not s then
		s = Instance.new("UIScale")
		s.Name = "MotionScale"
		s.Parent = obj
	end
	return s
end

function UIMotion.fitDesignScale(root)
	local scale = root:FindFirstChild("DesignScale")
	local design = scale and scale:GetAttribute("DesignSize")
	if not design then return function() end end
	local cam = Workspace.CurrentCamera
	local function fit()
		local vp = cam.ViewportSize
		scale.Scale = math.min(vp.X / design.X, vp.Y / design.Y)
	end
	fit()
	local conn = cam:GetPropertyChangedSignal("ViewportSize"):Connect(fit)
	return function() conn:Disconnect() end
end

-- buttons: put the visual inside the button or animate the button itself; under a UIListLayout wrap it in a holder
-- frame so the layout owns the holder and the UIScale grows from the centre
function UIMotion.button(btn, opts)
	opts = opts or {}
	local s = uiscale(opts.target or btn)
	local hover, press = opts.hoverScale or 1.04, opts.pressScale or 0.95
	local hovered, pressed = false, false
	local function refresh(fromPress)
		if pressed then
			UIMotion.tween(s, info(UIMotion.T.press, Enum.EasingStyle.Quad), { Scale = press }, "scale")
		elseif hovered then
			UIMotion.tween(s, fromPress and UIMotion.ease.pop(UIMotion.T.release) or UIMotion.ease.enter(UIMotion.T.hover),
				{ Scale = hover }, "scale")
		else
			UIMotion.tween(s, UIMotion.ease.enter(UIMotion.T.hover), { Scale = 1 }, "scale")
		end
		if opts.onState then opts.onState(pressed and "press" or hovered and "hover" or "idle") end
	end
	local c = {
		btn.MouseEnter:Connect(function() hovered = true; refresh() end),
		btn.MouseLeave:Connect(function() hovered, pressed = false, false; refresh() end),
		btn.SelectionGained:Connect(function() hovered = true; refresh() end),
		btn.SelectionLost:Connect(function() hovered, pressed = false, false; refresh() end),
		btn.MouseButton1Down:Connect(function() pressed = true; refresh() end),
		btn.MouseButton1Up:Connect(function() pressed = false; refresh(true) end),
	}
	return function() for _, x in c do x:Disconnect() end end
end

-- panels: Closed -> Opening -> Open -> Closing; spamming toggle reverses from wherever it is
function UIMotion.panel(frame, opts)
	opts = opts or {}
	local slide = opts.slide or UDim2.fromOffset(0, 18)
	local home = frame.Position
	local group = frame:IsA("CanvasGroup") and frame or nil -- fade whole panel only if it is a CanvasGroup (costs a texture)
	local s = uiscale(frame)
	local p = { state = frame.Visible and "open" or "closed" }
	function p:open()
		if self.state == "open" or self.state == "opening" then return end
		self.state = "opening"
		frame.Visible = true
		if not UIMotion.reduced() and frame.Position == home then
			frame.Position = home + slide
			s.Scale = opts.fromScale or 0.97
			if group then group.GroupTransparency = 1 end
		end
		local t = UIMotion.ease.enter(opts.openTime or UIMotion.T.open)
		UIMotion.tween(frame, t, { Position = home }, "pos")
		UIMotion.tween(s, t, { Scale = 1 }, "scale")
		local tw = group and UIMotion.tween(group, t, { GroupTransparency = 0 }, "fade")
		task.delay(opts.openTime or UIMotion.T.open, function()
			if self.state == "opening" then self.state = "open" end
		end)
		return tw
	end
	function p:close()
		if self.state == "closed" or self.state == "closing" then return end
		self.state = "closing"
		local tt = opts.closeTime or UIMotion.T.close
		local t = UIMotion.ease.exit(tt)
		UIMotion.tween(frame, t, { Position = home + slide }, "pos")
		UIMotion.tween(s, t, { Scale = opts.fromScale or 0.97 }, "scale")
		if group then UIMotion.tween(group, t, { GroupTransparency = 1 }, "fade") end
		task.delay(UIMotion.reduced() and 0 or tt, function()
			if self.state == "closing" then
				self.state = "closed"
				frame.Visible = false
				frame.Position = home
			end
		end)
	end
	function p:toggle()
		if self.state == "open" or self.state == "opening" then self:close() else self:open() end
	end
	return p
end

-- ghost bar: Fill snaps fast, Ghost (behind, pale) holds then drains; a new hit restarts the hold
function UIMotion.ghostBar(fill, ghost, hold, drain)
	hold, drain = hold or 0.5, drain or 0.4
	local token = 0
	return function(frac)
		frac = math.clamp(frac, 0, 1)
		UIMotion.tween(fill, info(0.08, Enum.EasingStyle.Quad), { Size = UDim2.fromScale(frac, 1) }, "size")
		token += 1
		local my = token
		if frac >= ghost.Size.X.Scale then
			UIMotion.tween(ghost, info(0.08), { Size = UDim2.fromScale(frac, 1) }, "size")
			return
		end
		task.delay(hold, function()
			if my ~= token then return end
			UIMotion.tween(ghost, info(drain, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
				{ Size = UDim2.fromScale(frac, 1) }, "size")
		end)
	end
end

function UIMotion.countUp(label, from, to, t, fmt)
	fmt = fmt or "%d"
	if UIMotion.reduced() or t <= 0 then label.Text = string.format(fmt, to) return end
	local start = os.clock()
	task.spawn(function()
		while true do
			local a = math.clamp((os.clock() - start) / t, 0, 1)
			local e = TweenService:GetValue(a, Enum.EasingStyle.Quint, Enum.EasingDirection.Out)
			label.Text = string.format(fmt, from + (to - from) * e)
			if a >= 1 then break end
			task.wait()
		end
	end)
end

function UIMotion.typewrite(label, cps)
	local n = 0
	for _ in utf8.graphemes(label.ContentText) do n += 1 end
	if UIMotion.reduced() then label.MaxVisibleGraphemes = -1 return end
	label.MaxVisibleGraphemes = 0
	task.spawn(function()
		for i = 1, n do
			label.MaxVisibleGraphemes = i
			task.wait(1 / (cps or 45))
		end
		label.MaxVisibleGraphemes = -1
	end)
end

-- overlay: a white Frame over the card (same size/corners), with a UIGradient; the gradient masks the overlay
function UIMotion.shine(overlay, t)
	local g = overlay:FindFirstChildOfClass("UIGradient")
	if not g then
		g = Instance.new("UIGradient")
		g.Rotation = 20
		g.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.42, 1), NumberSequenceKeypoint.new(0.5, 0.4),
			NumberSequenceKeypoint.new(0.58, 1), NumberSequenceKeypoint.new(1, 1),
		})
		g.Parent = overlay
	end
	if UIMotion.reduced() then return end
	g.Offset = Vector2.new(-1, 0)
	UIMotion.tween(g, info(t or 0.6, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), { Offset = Vector2.new(1, 0) }, "shine")
end

function UIMotion.stagger(items, fn, step, cap)
	step, cap = step or 0.03, cap or 8
	for i, item in items do
		local d = UIMotion.reduced() and 0 or math.min(i - 1, cap) * step
		if d == 0 then fn(item, i) else task.delay(d, fn, item, i) end
	end
end

function UIMotion.damp(current, target, halfLife, dt)
	return target + (current - target) * 2 ^ (-dt / halfLife)
end

return UIMotion
