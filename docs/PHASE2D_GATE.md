# Phase 2d Gate — UI Block v2 re-check (colour pickers, label rotation)

Changes since Phase 2c: colour controls published with `ControlGroup` (v1 pattern, name on the first channel only);
label now rotates with the card's Angle (`UIB_Label.Angle = UIB_Shape.Angle`); inner nodes are named `UIB_*`, Shape uses the frame format
(both from the Phase 2c results). Install: `python scripts/install.py`, restart Resolve (re-add the macro; old instances keep the old inputs).

| # | Check | Pass criteria / report |
|---|---|---|
| V1 | Add `SMK2_UIBlock` fresh (script paste AND, if possible, Effects ▸ Tools ▸ Macros). Inspector "Card" page | Text Color, Fill Color, Fill Color B, Border Color, Shadow Color each show as **one colour picker** (swatch + picker, alpha where applicable), not 4 loose channels. Report exactly what each shows |
| V2 | Angle 30° / -45° / 90° | Label rotates with the card and stays centred |
| V3 | Font Style combo | Report what it shows (was "--"); does changing it change the text? If it cannot work, say which Style values the Text+ accepts |
| V4 | Regression: U3 default look/motion, U5 parity (block vs standalone Shape, max diff 0), U8 two instances, U9 full restart | Same as Phase 2c |
| V5 | Look into the U5 chain finding: three standalone Shapes in one Merge chain, shapes B and C lost their shadow | Find the cause (stacking order? same centre? shadow offset hidden under previous shape? premultiplied handling in Merge?). Report with a minimal comp; do not edit Fuses |
