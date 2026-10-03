# Phase 4 spike S8 results: Text+ StyledTextFollower

Resolve Studio 21.1.0.14, Windows. Project `SMK Phase4 S8` (your `SMK Test` was not touched). Scripting only: no Fuse was changed. One comp per check, named `S8_E*`. Each has a Note above the graph and explicit node positions (Note y −3; Background x 0; Text+ x 4; Merge x 8; MediaOut x 12; one row per Text+). `FlowView.Select()` was called before every tool add or paste. The project was saved with `SaveProject()`.
Comps use 24 fps and 120 frames unless named otherwise. `S8_E5_Rate60` and the `S8_E9_*` comps are 60 fps timelines with `Comp.FrameFormat.Rate` set to 60 explicitly (a timeline set to 60 fps does not change the comp rate). The builder and measuring scripts are in `docs/phase4_evidence/` (`h4.py`, `s8meas.py`, `e9wait.sh`).

## Summary

| # | Comp | Result |
|---|---|---|
| E1 | `S8_E1_Inputs` | `text:AddModifier("StyledText","StyledTextFollower")` works. The follower (modifier name `Follower1`) has **475 inputs**. List below. |
| E2 | `S8_E3_Inputs_Bound` | `SaveSettings` works. Two `.setting` files are committed. The follower is a separate `StyledTextFollower` tool that `TextPlus.StyledText` points at, and each bound modifier is its own `Fuse.SMK2_Motion` tool referenced by `SourceOp`. |
| E3 | `S8_E3_Inputs_Bound`, `S8_E3_Probe` | Number inputs accept the Motion modifier. **Point inputs do not** (`CharacterOffset`, `CharacterPivot`). Letters are visibly staggered by the follower Delay on every bound input I rendered. Vertical position: NOT achieved (E3 table). `[req.Time]` offsets: NOT VERIFIED (logging needs a Fuse change). |
| E4 | `S8_E4_Order`, `S8_E4_Units` | Order values mapped by render (table below). Delay is **per character index**. The unit (letter, word, line) is chosen by which transform input is bound, not by a menu. |
| E5 | `S8_E5_Rate24`, `S8_E5_Rate60` | **Delay is in frames**, independent of the comp rate. An expression on Delay works when set by script. |
| E6 | `S8_E6_Offsets` | Letters start 2.4 frames (0.1 s) apart. **The Out phase is delayed per letter too, so the last letters do not finish their Out before the clip end.** |
| E7 | `S8_E3_Inputs_Bound` | PASS after a full quit and relaunch: connections identical, renders pixel-identical. |
| E8 | `S8_E8_PerLetter` | Tracking (`CharacterSpacing`) and colour (`Red1`) are driven per letter. Blur (`SoftnessX1/Y1`) accepts the modifier but I saw no visible blur. |
| E9 | `S8_E9_*` | Static 5.6, follower alone 5.4, 1 bound 31.5–33.2, 3 bound 107.2–107.5 ms/frame. About 25–30 ms per bound modifier, not 3 ms. |

## E1: follower inputs

The follower has 475 inputs. The table below lists the first 123 (Timing, Text, Transform and the Shading Element 1 block) and the Common inputs. Elements 2–8 repeat the Element 1 block with the number in the ID changed (`Properties2..8`, `Opacity2..8`, `Softness2..8` and so on, 47 inputs each, rows 132–467). The complete 475-row table is in `docs/phase4_evidence/S8_E1_all_inputs.md`.
Defaults are the values of a freshly added modifier. "Page / group" is the Inspector page, then the nest before the input. Min and max are not exposed for these controls (`INPN_MinAllowed/MaxAllowed` read ±1e6).

The inputs you asked for:

| Need | Input IDs |
|---|---|
| Order | `Order` (combo, default 7 = Automatic) |
| Delay | `Delay` (slider, in frames), `DelayType` (combo: 0 None, 1 Between Each Character, 2 Between First and Last Character; default 1), `DelayByCharacterPosition`, `ThisValue` (Delay Value) |
| Range | `Range` (0 All Characters, 1 Character Range), `FirstCharacter`, `LastCharacter` |
| Position | `CharacterOffset`, `WordOffset`, `LineOffset` (Point), `CharacterOffsetZ`, `WordOffsetZ`, `LineOffsetZ` (Number). See E3: X/Y had no visible effect. |
| Size | `CharacterSizeX/Y`, `WordSizeX/Y`, `LineSizeX/Y` (enable nest `TransformSize`, default 0) |
| Rotation | `CharacterAngleX/Y/Z`, `WordAngleX/Y/Z`, `LineAngleX/Y/Z` (enable nest `TransformRotation`, default 1) |
| Opacity | per shading element only: `Opacity1..8` |
| Blur / softness | per shading element only: `SoftnessX1..8`, `SoftnessY1..8`, `SoftnessGlow1..8`, `SoftnessBlend1..8` (nest `Softness1..8`) |
| Spacing / tracking | `CharacterSpacing`, `WordSpacing`, `LineSpacing` (Numbers) |
| Colour | per element: `Red1..8`, `Green1..8`, `Blue1..8`, `Alpha1..8` |
| Enable checkboxes | nests `TransformTransform` (1), `TransformRotation` (1), `TransformPivot` (0), `TransformShear` (0), `TransformSize` (0), `ShadingElements` (1); per element `Enabled1..8` |

There is no whole-text Opacity or Blur input; both exist only per shading element.

| # | ID | Display name | Type | Control | Default (fresh modifier) | Page / group | Menu values (value=label) |
|---|---|---|---|---|---|---|---|
| 1 | `Range` | Range | Number | MultiButtonControl | 0.0 | Timing /  | 0=All Characters; 1=Character Range |
| 2 | `FirstCharacter` | First Character | Number | SliderControl | 0.0 | Timing /  |  |
| 3 | `LastCharacter` | Last Character | Number | SliderControl | 20.0 | Timing /  |  |
| 4 | `Order` | Order | Number | ComboControl | 7.0 | Timing /  | 0=Left to Right; 1=Right to Left; 2=Inside Out; 3=Outside In; 4=Random One by One; 5=Completely Random; 6=Manual Curve; 7=Automatic (verified by render, see E4) |
| 5 | `DelayByCharacterPosition` | Delay by Character Position | Number | ScrewControl | 0.0 | Timing /  |  |
| 6 | `FirstSelectedDelay` | Set First Selected Character Delay | Number | ButtonControl | 0.0 | Timing /  |  |
| 7 | `ThisValue` | Delay Value | Number | ScrewControl | 0.0 | Timing /  |  |
| 8 | `DelayType` | Delay type | Number | ComboControl | 1.0 | Timing /  | 0=None; 1=Between Each Character; 2=Between First and Last Character |
| 9 | `Delay` | Delay | Number | SliderControl | 0.0 | Timing /  |  |
| 10 | `TextText` | Text | Number | NestControl | 1.0 | Text / Text |  |
| 11 | `Text` | Text | Text | TextEditControl | 'SMK TEXT DEMO' | Text / Text |  |
| 12 | `Size` | Size | Number | SliderControl | 0.08 | Text / Text |  |
| 13 | `VerticalTopCenterBottom` | V Anchor | Number | SliderControl | 0.0 | Text / Text |  |
| 14 | `HorizontalLeftCenterRight` | H Anchor | Number | SliderControl | 0.0 | Text / Text |  |
| 15 | `Strikeout` | Strikeout | Number | MultiButtonControl | 0.0 | Text / Text | 0=Strikeout |
| 16 | `Underline` | Underline | Number | MultiButtonControl | 0.0 | Text / Text | 0=Underline |
| 17 | `TransformTransform` | Transform | Number | NestControl | 1.0 | Transform / Transform |  |
| 18 | `SelectTransform` | Select Transform | Number | MultiButtonControl | 0.0 | Transform / Transform | 0=Characters; 1=Words; 2=Lines |
| 19 | `LineSpacing` | Line Spacing | Number | SliderControl | 1.0 | Transform / Transform |  |
| 20 | `LineOffset` | Line Offset | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Transform |  |
| 21 | `LineOffsetZ` | Line Offset Z | Number | SliderControl | 0.0 | Transform / Transform |  |
| 22 | `WordSpacing` | Word Spacing | Number | SliderControl | 1.0 | Transform / Transform |  |
| 23 | `WordOffset` | Word Offset | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Transform |  |
| 24 | `WordOffsetZ` | Word Offset Z | Number | SliderControl | 0.0 | Transform / Transform |  |
| 25 | `CharacterSpacing` | Character Spacing | Number | SliderControl | 1.0 | Transform / Transform |  |
| 26 | `CharacterOffset` | Character Offset | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Transform |  |
| 27 | `CharacterOffsetZ` | Character Offset Z | Number | SliderControl | 0.0 | Transform / Transform |  |
| 28 | `TransformRotation` | Rotation | Number | NestControl | 1.0 | Transform / Rotation |  |
| 29 | `LineRotationOrder` | Line Rotation Order | Number | MultiButtonControl | 0.0 | Transform / Rotation | 0=XYZ; 1=XZY; 2=YXZ; 3=YZX; 4=ZXY; 5=ZYX |
| 30 | `LineAngleX` | Line Angle X | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 31 | `LineAngleY` | Line Angle Y | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 32 | `LineAngleZ` | Line Angle Z | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 33 | `WordRotationOrder` | Word Rotation Order | Number | MultiButtonControl | 0.0 | Transform / Rotation | 0=XYZ; 1=XZY; 2=YXZ; 3=YZX; 4=ZXY; 5=ZYX |
| 34 | `WordAngleX` | Word Angle X | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 35 | `WordAngleY` | Word Angle Y | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 36 | `WordAngleZ` | Word Angle Z | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 37 | `AdaptWordWidthToAngle` | Adapt Word Width to Angle | Number | CheckboxControl | 0.0 | Transform / Rotation |  |
| 38 | `CharacterRotationOrder` | Character Rotation Order | Number | MultiButtonControl | 0.0 | Transform / Rotation | 0=XYZ; 1=XZY; 2=YXZ; 3=YZX; 4=ZXY; 5=ZYX |
| 39 | `CharacterAngleX` | Character Angle X | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 40 | `CharacterAngleY` | Character Angle Y | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 41 | `CharacterAngleZ` | Character Angle Z | Number | ScrewControl | 0.0 | Transform / Rotation |  |
| 42 | `AdaptCharacterWidthToAngle` | Adapt Character Width to Angle | Number | CheckboxControl | 0.0 | Transform / Rotation |  |
| 43 | `TransformPivot` | Pivot | Number | NestControl | 0.0 | Transform / Pivot |  |
| 44 | `LinePivot` | Line Pivot | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Pivot |  |
| 45 | `LinePivotZ` | Line Pivot Z | Number | SliderControl | 0.0 | Transform / Pivot |  |
| 46 | `WordPivot` | Word Pivot | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Pivot |  |
| 47 | `WordPivotZ` | Word Pivot Z | Number | SliderControl | 0.0 | Transform / Pivot |  |
| 48 | `CharacterPivot` | Character Pivot | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Transform / Pivot |  |
| 49 | `CharacterPivotZ` | Character Pivot Z | Number | SliderControl | 0.0 | Transform / Pivot |  |
| 50 | `TransformShear` | Shear | Number | NestControl | 0.0 | Transform / Shear |  |
| 51 | `LineShearX` | Line Shear X | Number | SliderControl | 0.0 | Transform / Shear |  |
| 52 | `LineShearY` | Line Shear Y | Number | SliderControl | 0.0 | Transform / Shear |  |
| 53 | `WordShearX` | Word Shear X | Number | SliderControl | 0.0 | Transform / Shear |  |
| 54 | `WordShearY` | Word Shear Y | Number | SliderControl | 0.0 | Transform / Shear |  |
| 55 | `CharacterShearX` | Character Shear X | Number | SliderControl | 0.0 | Transform / Shear |  |
| 56 | `CharacterShearY` | Character Shear Y | Number | SliderControl | 0.0 | Transform / Shear |  |
| 57 | `TransformSize` | Size | Number | NestControl | 0.0 | Transform / Size |  |
| 58 | `LineSizeX` | Line Size X | Number | SliderControl | 1.0 | Transform / Size |  |
| 59 | `LineSizeY` | Line Size Y | Number | SliderControl | 1.0 | Transform / Size |  |
| 60 | `WordSizeX` | Word Size X | Number | SliderControl | 1.0 | Transform / Size |  |
| 61 | `WordSizeY` | Word Size Y | Number | SliderControl | 1.0 | Transform / Size |  |
| 62 | `CharacterSizeX` | Character Size X | Number | SliderControl | 1.0 | Transform / Size |  |
| 63 | `CharacterSizeY` | Character Size Y | Number | SliderControl | 1.0 | Transform / Size |  |
| 64 | `ShadingElements` | Shading Elements | Number | NestControl | 1.0 | Shading / Shading Elements |  |
| 65 | `SelectElement` | Select Element | Number | MultiButtonControl | 0.0 | Shading / Shading Elements | 0=1; 1=2; 2=3; 3=4; 4=5; 5=6; 6=7; 7=8 |
| 66 | `Select` | Select | Number | MultiButtonControl | 0.0 | Shading / Shading Elements | 0=Fill; 1=Outline; 2=Shadow; 3=Border |
| 67 | `Name1` | Name 1 | Text | TextEditControl | 'White Solid Fill' | Shading / Shading Elements |  |
| 68 | `Enabled1` | Enabled 1 | Number | CheckboxControl | 1.0 | Shading / Shading Elements |  |
| 69 | `Name2` | Name 2 | Text | TextEditControl | 'Red Outline' | Shading / Shading Elements |  |
| 70 | `Enabled2` | Enabled 2 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 71 | `Name3` | Name 3 | Text | TextEditControl | 'Black Shadow' | Shading / Shading Elements |  |
| 72 | `Enabled3` | Enabled 3 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 73 | `Name4` | Name 4 | Text | TextEditControl | 'Blue Border' | Shading / Shading Elements |  |
| 74 | `Enabled4` | Enabled 4 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 75 | `Name5` | Name 5 | Text | TextEditControl | 'Element 5' | Shading / Shading Elements |  |
| 76 | `Enabled5` | Enabled 5 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 77 | `Name6` | Name 6 | Text | TextEditControl | 'Element 6' | Shading / Shading Elements |  |
| 78 | `Enabled6` | Enabled 6 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 79 | `Name7` | Name 7 | Text | TextEditControl | 'Element 7' | Shading / Shading Elements |  |
| 80 | `Enabled7` | Enabled 7 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 81 | `Name8` | Name 8 | Text | TextEditControl | 'Element 8' | Shading / Shading Elements |  |
| 82 | `Enabled8` | Enabled 8 | Number | CheckboxControl | 0.0 | Shading / Shading Elements |  |
| 83 | `SortShadingElements` | Sort Elements By | Number | MultiButtonControl | 0.0 | Shading / Shading Elements | 0=Priority; 1=Distance; 2=Z Position |
| 84 | `Properties1` | Properties 1 | Number | NestControl | 1.0 | Shading / Properties 1 |  |
| 85 | `Opacity1` | Opacity 1 | Number | SliderControl | 1.0 | Shading / Properties 1 |  |
| 86 | `ElementShape1` | Appearance 1 | Number | MultiButtonControl | 0.0 | Shading / Properties 1 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 87 | `Thickness1` | Thickness 1 | Number | SliderControl | 0.02 | Shading / Properties 1 |  |
| 88 | `JoinStyle1` | Join Style 1 | Number | MultiButtonControl | 1.0 | Shading / Properties 1 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 89 | `MiterLimit1` | Miter Limit 1 | Number | SliderControl | 10.0 | Shading / Properties 1 |  |
| 90 | `LineStyle1` | Line Style 1 | Number | ComboControl | 0.0 | Shading / Properties 1 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 91 | `ExtendHorizontal1` | Extend Horizontal 1 | Number | SliderControl | 0.0 | Shading / Properties 1 |  |
| 92 | `ExtendVertical1` | Extend Vertical 1 | Number | SliderControl | 0.0 | Shading / Properties 1 |  |
| 93 | `Round1` | Round 1 | Number | SliderControl | 0.0 | Shading / Properties 1 |  |
| 94 | `ElementSeparator1` |  | Number | SeparatorControl | 0.0 | Shading / Properties 1 |  |
| 95 | `Type1` | Type 1 | Number | MultiButtonControl | 0.0 | Shading / Properties 1 | 0=Solid; 1=Image; 2=Gradient |
| 96 | `OverrideColor1` | Override Color Fonts 1 | Number | CheckboxControl | 0.0 | Shading / Properties 1 |  |
| 97 | `ElementSpacer1` |  | Number | SpacerControl | 0.0 | Shading / Properties 1 |  |
| 98 | `Red1` | Red 1 | Number | ColorControl | 1.0 | Shading / Properties 1 |  |
| 99 | `Green1` | Green 1 | Number | ColorControl | 1.0 | Shading / Properties 1 |  |
| 100 | `Blue1` | Blue 1 | Number | ColorControl | 1.0 | Shading / Properties 1 |  |
| 101 | `Alpha1` | Alpha 1 | Number | ColorControl | 1.0 | Shading / Properties 1 |  |
| 102 | `ImageShadingSampling1` | Image Sampling 1 | Number | MultiButtonControl | 1.0 | Shading / Properties 1 | 0=None; 1=Pixel; 2=Area |
| 103 | `ImageShadingEdges1` | Image Edges 1 | Number | MultiButtonControl | 1.0 | Shading / Properties 1 | 0=Black; 1=Wrap; 2=Duplicate |
| 104 | `ShadingMappingSpacer1` |  | Number | SpacerControl | 0.0 | Shading / Properties 1 |  |
| 105 | `ShadingMapping1` | Shading Mapping 1 | Number | MultiButtonControl | 1.0 | Shading / Properties 1 | 0=Stretch to Fit; 1=Maintain Aspect |
| 106 | `ShadingMappingAngle1` | Shading Mapping Angle 1 | Number | ScrewControl | 0.0 | Shading / Properties 1 |  |
| 107 | `ShadingMappingSize1` | Shading Mapping Size 1 | Number | SliderControl | 1.0 | Shading / Properties 1 |  |
| 108 | `ShadingMappingAspect1` | Shading Mapping Aspect 1 | Number | SliderControl | 1.0 | Shading / Properties 1 |  |
| 109 | `Softness1` | Softness 1 | Number | NestControl | 1.0 | Shading / Softness 1 |  |
| 110 | `SoftnessX1` | Softness X 1 | Number | SliderControl | 0.0 | Shading / Softness 1 |  |
| 111 | `SoftnessY1` | Softness Y 1 | Number | SliderControl | 0.0 | Shading / Softness 1 |  |
| 112 | `SoftnessOnFillColorToo1` | Apply Softness to Fill Color 1 | Number | CheckboxControl | 0.0 | Shading / Softness 1 |  |
| 113 | `SoftnessGlow1` | Softness Glow 1 | Number | SliderControl | 0.0 | Shading / Softness 1 |  |
| 114 | `SoftnessBlend1` | Softness Blend 1 | Number | SliderControl | 1.0 | Shading / Softness 1 |  |
| 115 | `Position1` | Position 1 | Number | NestControl | 1.0 | Shading / Position 1 |  |
| 116 | `PriorityBack1` | Priority 1 | Number | SliderControl | 8.0 | Shading / Position 1 |  |
| 117 | `Offset1` | Offset 1 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 1 |  |
| 118 | `OffsetZ1` | Offset Z 1 | Number | SliderControl | 0.0 | Shading / Position 1 |  |
| 119 | `Rotation1` | Rotation 1 | Number | NestControl | 0.0 | Shading / Rotation 1 |  |
| 120 | `AngleX1` | Angle X 1 | Number | ScrewControl | 0.0 | Shading / Rotation 1 |  |
| 121 | `AngleY1` | Angle Y 1 | Number | ScrewControl | 0.0 | Shading / Rotation 1 |  |
| 122 | `AngleZ1` | Angle Z 1 | Number | ScrewControl | 0.0 | Shading / Rotation 1 |  |
| 123 | `PivotNest1` | Pivot 1 | Number | NestControl | 0.0 | Shading / Pivot 1 |  |
| 468 | `CommentsNest` | Comments | Number | NestControl | 1.0 | Common / Comments |  |
| 469 | `Comments` | Comments | Text | TextEditControl | '' | Common / Comments |  |
| 470 | `FrameRenderScriptNest` | Frame Render Script | Number | NestControl | 1.0 | Common / Frame Render Script |  |
| 471 | `FrameRenderScript` | Frame Render Script | Text | TextEditControl | '' | Common / Frame Render Script |  |
| 472 | `StartRenderScripts` | Start Render Scripts | Number | NestControl | 0.0 | Common / Start Render Scripts |  |
| 473 | `StartRenderScript` | Start Render Script | Text | TextEditControl | '' | Common / Start Render Scripts |  |
| 474 | `EndRenderScripts` | End Render Scripts | Number | NestControl | 0.0 | Common / End Render Scripts |  |
| 475 | `EndRenderScript` | End Render Script | Text | TextEditControl | '' | Common / End Render Scripts |  |

## E2: serialisation

Files: `docs/phase4_evidence/S8_E2_TextPlus_follower_size_bound.setting` (follower with `CharacterSizeX/Y`, each bound to its own `SMK2_Motion`) and `S8_E2_TextPlus_follower_all_bound.setting` (opacity, size X/Y, rotation Z and the offset driver bound on one follower). What the file shows:
- `TextPlus` has `StyledText = Input { SourceOp = "Follower2", Source = "StyledText" }`.
- `Follower2 = StyledTextFollower` holds `Delay`, `Text`, `TransformSize`, and `CharacterSizeX = Input { SourceOp = "SMK2Motion2", Source = "Output" }`.
- Each bound modifier is its own `Fuse.SMK2_Motion` tool (`SMK2Motion2`, `SMK2Motion3`) with only the non-default inputs written. There is **no BezierSpline** in the file.
- Size X and size Y each need their own modifier (two modifiers for one scale).
- The `Order` I set (0) is not written to the file, so Order is not safe to rely on when reading a saved file; set it from the mapping in E4.

## E3: binding Motion to follower inputs

| Input | Accepts modifier? | Staggered per letter by Delay? | Evidence |
|---|---|---|---|
| `Opacity1` | yes | yes (letters fade in one after another) | `S8_E3_bound_inputs_sheet.png`, top row |
| `CharacterSizeX` / `CharacterSizeY` | yes | yes. Start spacing about 2.4 frames per letter (E6). | sheet, second row |
| `CharacterAngleZ` | yes | yes (letters rotate in one after another) | sheet, fourth row |
| `CharacterOffsetZ` | yes | yes, but it changes the rendered letter size (depth), not the vertical position | first render of `S8_E3_Inputs_Bound` (letters grew large) |
| `CharacterOffset`, `CharacterPivot` (Point) | **no** (`AddModifier` returns false, no connection) | n/a | `S8_E3_Probe` |
| Vertical position | NOT achieved. I drove `CharacterOffset` Y with an expression `Point(0, <Number driver>)`. The expression evaluates (−0.05 → 0 over the In), but even a static `CharacterOffset`, `WordOffset`, `LineOffset` or `Offset1` of 0.3 to 1.0 changed nothing in the render. Cause not found. | n/a | `S8_E3_Inputs_Bound` row 3 |
| All together (`Opacity1`, size X/Y, rotation Z, offset driver) | yes | yes | sheet, fifth row |

Other inputs that accepted the modifier in `S8_E3_Probe`: `CharacterSpacing`, `SoftnessX1`, `SoftnessGlow1`, `Red1`, `Thickness1`, `LineSizeX`, `WordSizeX`, `CharacterShearX`, `CharacterOffsetZ`, `MiterLimit1`.

## E4: Order and units

I rendered "ONE TWO THREE" (13 characters, 8 rows, one per Order value, Delay 2.4 frames, Motion bound to `CharacterSizeX`). The letters merged into 7 or 8 ink clusters, so values are per cluster, left to right, as the first frame with ink:

| Order value | Behaviour | First-ink frames, left to right |
|---|---|---|
| 0 | Left to Right | 1, 3, 6, 11, 20, 25, 30 |
| 1 | Right to Left | 30, 27, 25, 15, 8, 3, 1 |
| 2 | Inside Out | 15, 13, 10, 1, 6, 10, 15 |
| 3 | Outside In | 1, 3, 6, 11, 8, 3, 1 |
| 4 | Random, one by one | 8, 3, 22, 6, 25, 1, 10, 18 |
| 5 | Completely random | 25, 23, 2, 16, 21, 8, 22 |
| 6 | Manual Curve (no curve drawn: everything starts at once) | 1, 1, 1, 1, 1, 1, 1, 1 |
| 7 (default) | Automatic (behaves as Left to Right) | 1, 3, 6, 11, 20, 25, 27, 30 |

The menu list returned by the API starts with "Automatic", but the numeric value of Automatic is 7 (its default). A script must set Order using the numbers above.

Units (`S8_E4_Units`, two-line text "ONE TWO / THREE FOUR", Motion bound to Character, Word or Line size; `S8_E4_units_sheet.png`):
- Character bound: each letter staggers.
- Word bound (Delay 6): each word appears as a block. "THREE" appears at about frame 50 (its first character is index 8, 8 × 6 = 48) and "FOUR" at about 86–92 (index 14 × 6 = 84).
- Line bound (Delay 12): the second line appears at about frame 98–104 (index 8 × 12 = 96).
- So **Delay is per character position, and a word or line starts at the delay of its first character.** There is no letter/word/line unit menu; `DelayType` is None / Between Each Character / Between First and Last Character.

## E5: Delay units

`S8_E5_Rate24` (24 fps) and `S8_E5_Rate60` (60 fps, comp rate set to 60), 8 letters, Motion In 0.5 s. Average start spacing between letters in frames, from the first-ink frames:

| Setting | 24 fps comp | 60 fps comp |
|---|---|---|
| Delay = 2 | 1.86 (first-ink 2, 3, 6, 7, 9, 11, 13, 15) | 2.1 (2, 4, 7, 9, 10, 13, 14, 17) |
| Delay = expression `0.05 * comp:GetPrefs("Comp.FrameFormat.Rate")` | 1.14, value 1.2 (2, 2, 4, 5, 6, 7, 8, 10) | 3.1, value 3.0 (2, 5, 9, 12, 14, 18, 20, 24) |

Delay is in **frames**; it does not scale with the comp rate. The expression set with `mod.Delay.SetExpression(...)` is accepted and evaluates (1.2 at 24 fps, 3.0 at 60 fps), so a delay in seconds can be written as `seconds * rate`.

## E6: offsets (`S8_E6_Offsets`)

8 letters at 24 fps, Delay 2.4 frames (0.1 s), Motion In 0.5 s and Out 0.5 s (size 0 → 1 → 0), clip of 120 frames. Measured from the ink area of each letter:

| Letter | In first ink | In reaches 97% | Out starts | Last frame with ink |
|---|---|---|---|---|
| 1 | 2 | 6 | 109 | 116 |
| 2 | 4 | 8 | 112 | 118 |
| 3 | 6 | 10 | 114 | 119 |
| 4 | 9 | 13 | 116 | 119 |
| 5 | 11 | 15 | 119 | 119 |
| 6 | 13 | 18 | not started by frame 119 | still full at 119 |
| 7 | 16 | 20 | not started | still full |
| 8 | 18 | 23 | not started | still full |

- Letters start 0.1 s apart and each runs the same In. The spring reaches 97% about 4 frames after its start; the Motion value for letter 1 settles by frame about 12.
- Motion's Out follows the clip end for letter 1 (starts at frame 108–109, ends at 119). The follower delays the Out of later letters by their index × Delay, so letters 6–8 are still fully visible on the last frame. For the last letter to finish before the clip end, its Out would have to start earlier by (letters − 1) × Delay. Not tested.

## E7: save, quit, relaunch

`S8_E3_Inputs_Bound` (5 followers, 13 bound modifiers). After saving and a full quit and relaunch, the connection map of every follower (input ID → Motion tool) was identical to before. The bound tools are `SMK2_Motion` modifiers (no BezierSpline). Frames 6 and 12 re-rendered **pixel-identical**.

## E8: per-letter blur, colour, tracking (`S8_E8_PerLetter`)

| Effect | Input | Modifier accepted | Visible per-letter result |
|---|---|---|---|
| Blur | `SoftnessX1`, `SoftnessY1` | yes | **No visible blur in my render** (Motion 0.05 → 0). NOT VERIFIED that it works. |
| Colour | `Red1` (and `Green1`, `Blue1`) | yes | Yes: the red channel changes letter by letter (text went from cyan to white). My attempt to set `Green1` and `Blue1` to 0 by assignment did not take effect. |
| Tracking | `CharacterSpacing` | yes | Yes: letters pull in from wide spacing one after another |

Image: `S8_E8_per_letter_sheet.png`. Other per-letter inputs the follower exposes: opacity per element, shear, pivot (Points do not accept modifiers), size, rotation.

## E9: cost

60 fps, 1080p, 300 frames to PNG, 12-letter text, background +0.001 before each run. Times are first-to-last PNG time ÷ 299.

| Variant | Comp | ms/frame |
|---|---|---|
| Static Text+ (no follower) | `S8_E9_Static` | 5.6 |
| Text+ with follower, nothing bound | `S8_E9_Follower0` | 5.4 |
| 1 bound Motion (Opacity1) | `S8_E9_Bound1` | 33.2 and 31.5 |
| 3 bound Motion (Opacity1, Size X, Size Y) | `S8_E9_Bound3` | 107.5 and 107.2 |

Each bound modifier costs about 25–30 ms per frame, roughly ten times the expected 3 ms. I did not test scaling with the letter count, so the reason (the follower evaluating each modifier once per letter) is a guess: NOT VERIFIED. The static and follower-only runs were single runs.

## For you

- Decide how to get per-letter vertical position: the Point offsets cannot be driven by a modifier and had no visible effect in my test.
- The Out phase of later letters runs past the clip end (E6).
- The cost per bound modifier (E9) may limit binding more than one or two inputs on long texts.
- Whether the Inspector shows the bound follower inputs as linked: NOT VERIFIED (I did not take a screenshot of it).
