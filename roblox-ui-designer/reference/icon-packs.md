# Icon packs: casual/saturated register

The user's rule (2026-09-29): "for like cash grabby games and saturated looking ui, use vector icon packs for icons and
stuff, instead of lucide icons, theres roblox vector icon packs that are great".

- **Casual / simulator / monetized register:** use the **Roblox vector icon packs below**. They're glossy, rendered and
  sticker-like, which is what top simulators use.
- **Immersive, info-dense and competitive registers:** keep Lucide line icons.
- Draw a custom icon only if neither has the item.

## Where they are (on the user's PC)

Root: `C:/Users/notxk/OneDrive/RobloxStuff/RobloxStudioAssets/`
- **`Vector Icon Pack 5.1/`:** 392 PNGs in 59 folders, mostly 512x512 (a few at 3000²). Every icon comes as
  `<Name>.png` (no outline) and `<Name> Outline.png` (a dark outline baked in). Many have colour variants (Blue, Green,
  Orange, Purple, Red, Golden, Rainbow).
- **`IconPack/`** (by Enz0s): 57 PNGs, 512² and 1000². It has Currency (Coin, Robux_Green, Robux_White), General, Ui
  (arrows, check, close, hamburger), Random, and Social Media.
  - **Licence (IconPack/License.txt):** you may use and share them. Don't claim you made them, and **don't sell the
    icons or GUIs** for Robux or money. The README warns that social-media icons get moderated when uploaded, so don't
    name them after the brands.
- **Vector Icon Pack 5.1 has no licence file.** Before commercial release, confirm its source and terms with the user.

## How to use them

1. **Pick by meaning, then variant:**
   - Use the **Outline** variant on saturated or studded surfaces; it matches the ink-outline style.
   - Use the plain variant on light/cream plates or at hero sizes over glows.
   - Colour variants follow the colour roles and rarity: Golden = legendary, Purple = epic, Blue = rare, Green =
     uncommon.
2. **Figma:** upload with `upload_assets` (multipart, so the filename becomes the layer name). Use the returned
   imageHash as an IMAGE fill with `scaleMode: 'FIT'` on a square rectangle named `IconPack_<key>_img`. Park the source
   frames off-canvas as `*_src_ignore`.
3. **Sizing:** these PNGs carry about 8–12% transparent padding, so size the box 1.1–1.3x the glyph size you want.
   - List plates: about 56 px in a 64 px plate.
   - Hero: about 1.3x the focus plate's inner size. Let parts (a cork, sparkles) break the circle for depth.
   - Inline with text: 1.3–1.5x the cap height, centred on the cap band (craft.md §9.9).
4. **Roblox:**
   - Upload through the Studio MCP `upload_image` (or Asset Manager) and record `name -> rbxassetid` in `assets.json`.
   - Use an ImageLabel with `ScaleType.Fit` and a transparent background.
   - Display at 256 px or less. Downscale the 3000² ones to 512 before upload (texture memory).
5. **Never mix** Lucide line icons and pack icons in the same casual screen. The one exception is tiny UI glyphs (X, +,
   arrows), which can be white sticker glyphs or the pack's `IconPack/Ui` set.

## Catalog: Vector Icon Pack 5.1 (folder | icons; each also has an " Outline" version)

| Folder | Icons |
|---|---|
| Backpack | Backpack, Backpack Colorful, Backpack Gold |
| Bag | Bag Clovers, Bag Coins, Bag Eggs, Bag Gems, Bag Potions |
| Banners | Banner Blue, Banner Cyan, Banner Gold, Banner Green, Banner Purple, Banner Red |
| Battery | Battery Blue, Battery Green, Battery Orange, Battery Purple |
| Bell | Bell, Bell Purple |
| Bolt | Bolt, Bolt Blue, Bolt Green, Bolt Purple, Bolt Red |
| Book | Book |
| Borders | Border Blue, Border Cyan, Border Gold, Border Green, Border Purple, Border Red |
| Calculator | Calculator, Golden Calculator |
| Calendar | Calendar |
| Candle | Candle |
| Candy Cane | Candy Cane, Candy Cane Gold |
| Cardboard Box | Cardboard Box, Cardboard Box Eggs, Cardbox Box |
| Cash Stack | Cash Stack |
| Chat | Chat |
| Chest | Chest Clovers, Chest Coins, Chest Eggs, Chest Gems |
| Christmas Tree | Christmas Tree |
| Clover | Clover Blue, Clover Golden, Clover Green, Clover Pink |
| Clover 2 | Clover, Clover Gold, Clover Rainbow |
| Coins | Coin Blue, Coin Green, Coin Orange, Coin Pile Blue, Coin Pile Green, Coin Pile Orange, Coin Pile Purple, Coin Purple |
| Crate | Crate Blue Gems, Crate Clovers, Crate Coins, Crate Eggs, Crate Potions |
| Crown | Crown |
| Crown 2 | Crown2 Icon |
| Drink | Drink, Drink Green, Drink Orange, Drink Pink |
| Egg | Egg, Egg Blue, Egg Golden, Egg Green, Egg Purple, Egg Red |
| Envelope | Envelope, Envelope Green, Envelope Orange, Envelope Purple, Envelope Red |
| Gems | Gem Blue, Gem Green, Gem Orange, Gem Purple, Gem Red |
| Gift | Gift Blue, Gift Gold, Gift Green, Gift Mystery, Gift Red |
| Heart | Golden Heart, Heart |
| Hoverboard | Hoverboard Blue, Hoverboard Gold, Hoverboard Green, Hoverboard Orange, Hoverboard Purple, Hoverboard Red |
| Key | Golden Key, Key, Silver Key |
| Magnet | Golden Magnet, Magnet |
| Magnifying Glass | Magnifying Glass, Magnifying Glass Green, Magnifying Glass Orange, Magnifying Glass Purple |
| Medals | Medal, Medal 2, Medal Blue, Medal Green, Medal Purple, Medal Red |
| Megaphone | Megaphone, Megaphone Green, Megaphone Purple, Megaphone Red, Megaphone Yellow |
| Milk | Milk |
| Notepad | Notepad |
| Paper Bag | Paper Bag |
| Paw | Pet Paw, Pet Paw Brown |
| Pencil | Pencil |
| Penguin | Penguin |
| Plasma | Plasma Blue, Plasma Green, Plasma Orange, Plasma Purple, Plasma Shadow (Special) |
| Potion 2 | Potion 2 Green, Potion 2 Purple, Potion 2 Rainbow, Potion 2 Red |
| Potions | Potion, Potion Blue, Potion Green, Potion Orange, Potion Purple, Potion Rainbow |
| Present | Present Icon |
| Quest | Quest, Quest Gold, Quest Green, Quest Purple, Quest Red |
| Rebirth | Rebirth |
| Santa Hat | Santa Hat |
| Settings | Settings Gray, Settings Purple |
| Shop | Shop Blue Battery, Shop Blue Gems, Shop Clovers, Shop Coins, Shop Empty, Shop Gold Battery, Shop Potions Red, Shop Purple Battery, Shop Red Battery, Shop Red Gems, Shop Trophy |
| Skull | Skull Blue, Skull Cyan, Skull Golden, Skull Green, Skull Purple, Skull Red |
| Snowman | Snowman, Snowman Golden |
| Soda | Soda, Soda Green, Soda Orange, Soda Purple, Soda Red |
| Spoon | Spoon |
| Sword | Crossed Swords, Fire Crossed Swords, Fire Sword, Golden Sword, Sword |
| Teddy | Golden Teddy, Teddy |
| Teleport | Teleport, Teleport Gold, Teleport Green, Teleport Orange, Teleport Purple, Teleport Red |
| Trade | Trade |
| Trophy | Trophy Blue, Trophy Gold, Trophy Gold Sparkled, Trophy Green, Trophy Purple, Trophy Red, Trophy Ultimate Gold |

## Catalog: IconPack (Enz0s)

| Folder | Icons |
|---|---|
| IconPack/Currency | Coin, Robux_Green, Robux_White |
| IconPack/General | Bell, BookMark, Broken_Heart, Call_Answered, Call_Declined, Clock, Crown, Cursor_2, Cursor_2Click, Egg, Energy, Eye, Heart, Noob, Paper_Plane, Paw, Pin, Robux_Gold, Rocket, Script, Settings, Shopping_Cart, Skull, Star, Stats, Thumbs_down, Thumbs_up, Trade, Trade_1, Trade_2, Verified, Volume_Up |
| IconPack/Random | Ban_Hammer, Candy Cane, Info, Partner, Star_Creator, Warning |
| IconPack/Social Media | Discord, Twitch, Twitter, Youtube |
| IconPack/Ui | Check_icon, Close_icon, Down, Hamburger, Retweet_Like, Up, User, Warning |
| IconPack/Ui/Arrows | Arrow_Down, Arrow_Left, Arrow_Right, Arrow_Up |

## First use

The Gear Shop (Figma 67:4, 2026-09-29) uses:
- Soda Orange, Clover Green, Potion Green, Magnet and Golden Magnet (the Outline variants) for items;
- Coin Orange Outline for currency;
- Rebirth Outline for restock;
- Bolt Outline and IconPack Clock for stat chips.
