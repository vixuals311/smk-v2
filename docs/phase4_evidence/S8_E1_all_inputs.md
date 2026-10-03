# S8 E1: all 475 follower inputs

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
| 124 | `Pivot1` | Pivot 1 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 1 |  |
| 125 | `PivotZ1` | Pivot Z 1 | Number | SliderControl | 0.0 | Shading / Pivot 1 |  |
| 126 | `Shear1` | Shear 1 | Number | NestControl | 0.0 | Shading / Shear 1 |  |
| 127 | `ShearX1` | Shear X 1 | Number | SliderControl | 0.0 | Shading / Shear 1 |  |
| 128 | `ShearY1` | Shear Y 1 | Number | SliderControl | 0.0 | Shading / Shear 1 |  |
| 129 | `Size1` | Size 1 | Number | NestControl | 0.0 | Shading / Size 1 |  |
| 130 | `SizeX1` | Size X 1 | Number | SliderControl | 1.0 | Shading / Size 1 |  |
| 131 | `SizeY1` | Size Y 1 | Number | SliderControl | 1.0 | Shading / Size 1 |  |
| 132 | `Properties2` | Properties 2 | Number | NestControl | 1.0 | Shading / Properties 2 |  |
| 133 | `Opacity2` | Opacity 2 | Number | SliderControl | 1.0 | Shading / Properties 2 |  |
| 134 | `ElementShape2` | Appearance 2 | Number | MultiButtonControl | 1.0 | Shading / Properties 2 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 135 | `Thickness2` | Thickness 2 | Number | SliderControl | 0.02 | Shading / Properties 2 |  |
| 136 | `JoinStyle2` | Join Style 2 | Number | MultiButtonControl | 1.0 | Shading / Properties 2 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 137 | `MiterLimit2` | Miter Limit 2 | Number | SliderControl | 10.0 | Shading / Properties 2 |  |
| 138 | `LineStyle2` | Line Style 2 | Number | ComboControl | 0.0 | Shading / Properties 2 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 139 | `ExtendHorizontal2` | Extend Horizontal 2 | Number | SliderControl | 0.0 | Shading / Properties 2 |  |
| 140 | `ExtendVertical2` | Extend Vertical 2 | Number | SliderControl | 0.0 | Shading / Properties 2 |  |
| 141 | `Round2` | Round 2 | Number | SliderControl | 0.0 | Shading / Properties 2 |  |
| 142 | `ElementSeparator2` |  | Number | SeparatorControl | 0.0 | Shading / Properties 2 |  |
| 143 | `Type2` | Type 2 | Number | MultiButtonControl | 0.0 | Shading / Properties 2 | 0=Solid; 1=Image; 2=Gradient |
| 144 | `OverrideColor2` | Override Color Fonts 2 | Number | CheckboxControl | 1.0 | Shading / Properties 2 |  |
| 145 | `ElementSpacer2` |  | Number | SpacerControl | 0.0 | Shading / Properties 2 |  |
| 146 | `Red2` | Red 2 | Number | ColorControl | 1.0 | Shading / Properties 2 |  |
| 147 | `Green2` | Green 2 | Number | ColorControl | 0.0 | Shading / Properties 2 |  |
| 148 | `Blue2` | Blue 2 | Number | ColorControl | 0.0 | Shading / Properties 2 |  |
| 149 | `Alpha2` | Alpha 2 | Number | ColorControl | 1.0 | Shading / Properties 2 |  |
| 150 | `ImageShadingSampling2` | Image Sampling 2 | Number | MultiButtonControl | 1.0 | Shading / Properties 2 | 0=None; 1=Pixel; 2=Area |
| 151 | `ImageShadingEdges2` | Image Edges 2 | Number | MultiButtonControl | 1.0 | Shading / Properties 2 | 0=Black; 1=Wrap; 2=Duplicate |
| 152 | `ShadingMappingSpacer2` |  | Number | SpacerControl | 0.0 | Shading / Properties 2 |  |
| 153 | `ShadingMapping2` | Shading Mapping 2 | Number | MultiButtonControl | 1.0 | Shading / Properties 2 | 0=Stretch to Fit; 1=Maintain Aspect |
| 154 | `ShadingMappingAngle2` | Shading Mapping Angle 2 | Number | ScrewControl | 0.0 | Shading / Properties 2 |  |
| 155 | `ShadingMappingSize2` | Shading Mapping Size 2 | Number | SliderControl | 1.0 | Shading / Properties 2 |  |
| 156 | `ShadingMappingAspect2` | Shading Mapping Aspect 2 | Number | SliderControl | 1.0 | Shading / Properties 2 |  |
| 157 | `Softness2` | Softness 2 | Number | NestControl | 1.0 | Shading / Softness 2 |  |
| 158 | `SoftnessX2` | Softness X 2 | Number | SliderControl | 0.0 | Shading / Softness 2 |  |
| 159 | `SoftnessY2` | Softness Y 2 | Number | SliderControl | 0.0 | Shading / Softness 2 |  |
| 160 | `SoftnessOnFillColorToo2` | Apply Softness to Fill Color 2 | Number | CheckboxControl | 0.0 | Shading / Softness 2 |  |
| 161 | `SoftnessGlow2` | Softness Glow 2 | Number | SliderControl | 0.0 | Shading / Softness 2 |  |
| 162 | `SoftnessBlend2` | Softness Blend 2 | Number | SliderControl | 1.0 | Shading / Softness 2 |  |
| 163 | `Position2` | Position 2 | Number | NestControl | 1.0 | Shading / Position 2 |  |
| 164 | `PriorityBack2` | Priority 2 | Number | SliderControl | 7.0 | Shading / Position 2 |  |
| 165 | `Offset2` | Offset 2 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 2 |  |
| 166 | `OffsetZ2` | Offset Z 2 | Number | SliderControl | 0.0 | Shading / Position 2 |  |
| 167 | `Rotation2` | Rotation 2 | Number | NestControl | 0.0 | Shading / Rotation 2 |  |
| 168 | `AngleX2` | Angle X 2 | Number | ScrewControl | 0.0 | Shading / Rotation 2 |  |
| 169 | `AngleY2` | Angle Y 2 | Number | ScrewControl | 0.0 | Shading / Rotation 2 |  |
| 170 | `AngleZ2` | Angle Z 2 | Number | ScrewControl | 0.0 | Shading / Rotation 2 |  |
| 171 | `PivotNest2` | Pivot 2 | Number | NestControl | 0.0 | Shading / Pivot 2 |  |
| 172 | `Pivot2` | Pivot 2 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 2 |  |
| 173 | `PivotZ2` | Pivot Z 2 | Number | SliderControl | 0.0 | Shading / Pivot 2 |  |
| 174 | `Shear2` | Shear 2 | Number | NestControl | 0.0 | Shading / Shear 2 |  |
| 175 | `ShearX2` | Shear X 2 | Number | SliderControl | 0.0 | Shading / Shear 2 |  |
| 176 | `ShearY2` | Shear Y 2 | Number | SliderControl | 0.0 | Shading / Shear 2 |  |
| 177 | `Size2` | Size 2 | Number | NestControl | 0.0 | Shading / Size 2 |  |
| 178 | `SizeX2` | Size X 2 | Number | SliderControl | 1.0 | Shading / Size 2 |  |
| 179 | `SizeY2` | Size Y 2 | Number | SliderControl | 1.0 | Shading / Size 2 |  |
| 180 | `Properties3` | Properties 3 | Number | NestControl | 1.0 | Shading / Properties 3 |  |
| 181 | `Opacity3` | Opacity 3 | Number | SliderControl | 1.0 | Shading / Properties 3 |  |
| 182 | `ElementShape3` | Appearance 3 | Number | MultiButtonControl | 0.0 | Shading / Properties 3 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 183 | `Thickness3` | Thickness 3 | Number | SliderControl | 0.02 | Shading / Properties 3 |  |
| 184 | `JoinStyle3` | Join Style 3 | Number | MultiButtonControl | 1.0 | Shading / Properties 3 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 185 | `MiterLimit3` | Miter Limit 3 | Number | SliderControl | 10.0 | Shading / Properties 3 |  |
| 186 | `LineStyle3` | Line Style 3 | Number | ComboControl | 0.0 | Shading / Properties 3 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 187 | `ExtendHorizontal3` | Extend Horizontal 3 | Number | SliderControl | 0.0 | Shading / Properties 3 |  |
| 188 | `ExtendVertical3` | Extend Vertical 3 | Number | SliderControl | 0.0 | Shading / Properties 3 |  |
| 189 | `Round3` | Round 3 | Number | SliderControl | 0.0 | Shading / Properties 3 |  |
| 190 | `ElementSeparator3` |  | Number | SeparatorControl | 0.0 | Shading / Properties 3 |  |
| 191 | `Type3` | Type 3 | Number | MultiButtonControl | 0.0 | Shading / Properties 3 | 0=Solid; 1=Image; 2=Gradient |
| 192 | `OverrideColor3` | Override Color Fonts 3 | Number | CheckboxControl | 1.0 | Shading / Properties 3 |  |
| 193 | `ElementSpacer3` |  | Number | SpacerControl | 0.0 | Shading / Properties 3 |  |
| 194 | `Red3` | Red 3 | Number | ColorControl | 0.0 | Shading / Properties 3 |  |
| 195 | `Green3` | Green 3 | Number | ColorControl | 0.0 | Shading / Properties 3 |  |
| 196 | `Blue3` | Blue 3 | Number | ColorControl | 0.0 | Shading / Properties 3 |  |
| 197 | `Alpha3` | Alpha 3 | Number | ColorControl | 1.0 | Shading / Properties 3 |  |
| 198 | `ImageShadingSampling3` | Image Sampling 3 | Number | MultiButtonControl | 1.0 | Shading / Properties 3 | 0=None; 1=Pixel; 2=Area |
| 199 | `ImageShadingEdges3` | Image Edges 3 | Number | MultiButtonControl | 1.0 | Shading / Properties 3 | 0=Black; 1=Wrap; 2=Duplicate |
| 200 | `ShadingMappingSpacer3` |  | Number | SpacerControl | 0.0 | Shading / Properties 3 |  |
| 201 | `ShadingMapping3` | Shading Mapping 3 | Number | MultiButtonControl | 1.0 | Shading / Properties 3 | 0=Stretch to Fit; 1=Maintain Aspect |
| 202 | `ShadingMappingAngle3` | Shading Mapping Angle 3 | Number | ScrewControl | 0.0 | Shading / Properties 3 |  |
| 203 | `ShadingMappingSize3` | Shading Mapping Size 3 | Number | SliderControl | 1.0 | Shading / Properties 3 |  |
| 204 | `ShadingMappingAspect3` | Shading Mapping Aspect 3 | Number | SliderControl | 1.0 | Shading / Properties 3 |  |
| 205 | `Softness3` | Softness 3 | Number | NestControl | 1.0 | Shading / Softness 3 |  |
| 206 | `SoftnessX3` | Softness X 3 | Number | SliderControl | 5.0 | Shading / Softness 3 |  |
| 207 | `SoftnessY3` | Softness Y 3 | Number | SliderControl | 5.0 | Shading / Softness 3 |  |
| 208 | `SoftnessOnFillColorToo3` | Apply Softness to Fill Color 3 | Number | CheckboxControl | 0.0 | Shading / Softness 3 |  |
| 209 | `SoftnessGlow3` | Softness Glow 3 | Number | SliderControl | 0.0 | Shading / Softness 3 |  |
| 210 | `SoftnessBlend3` | Softness Blend 3 | Number | SliderControl | 1.0 | Shading / Softness 3 |  |
| 211 | `Position3` | Position 3 | Number | NestControl | 1.0 | Shading / Position 3 |  |
| 212 | `PriorityBack3` | Priority 3 | Number | SliderControl | 6.0 | Shading / Position 3 |  |
| 213 | `Offset3` | Offset 3 | Point | OffsetControl | {1: 0.05, 2: -0.05, 3: 0.0} | Shading / Position 3 |  |
| 214 | `OffsetZ3` | Offset Z 3 | Number | SliderControl | 0.0 | Shading / Position 3 |  |
| 215 | `Rotation3` | Rotation 3 | Number | NestControl | 0.0 | Shading / Rotation 3 |  |
| 216 | `AngleX3` | Angle X 3 | Number | ScrewControl | 0.0 | Shading / Rotation 3 |  |
| 217 | `AngleY3` | Angle Y 3 | Number | ScrewControl | 0.0 | Shading / Rotation 3 |  |
| 218 | `AngleZ3` | Angle Z 3 | Number | ScrewControl | 0.0 | Shading / Rotation 3 |  |
| 219 | `PivotNest3` | Pivot 3 | Number | NestControl | 0.0 | Shading / Pivot 3 |  |
| 220 | `Pivot3` | Pivot 3 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 3 |  |
| 221 | `PivotZ3` | Pivot Z 3 | Number | SliderControl | 0.0 | Shading / Pivot 3 |  |
| 222 | `Shear3` | Shear 3 | Number | NestControl | 0.0 | Shading / Shear 3 |  |
| 223 | `ShearX3` | Shear X 3 | Number | SliderControl | 0.0 | Shading / Shear 3 |  |
| 224 | `ShearY3` | Shear Y 3 | Number | SliderControl | 0.0 | Shading / Shear 3 |  |
| 225 | `Size3` | Size 3 | Number | NestControl | 0.0 | Shading / Size 3 |  |
| 226 | `SizeX3` | Size X 3 | Number | SliderControl | 1.0 | Shading / Size 3 |  |
| 227 | `SizeY3` | Size Y 3 | Number | SliderControl | 1.0 | Shading / Size 3 |  |
| 228 | `Properties4` | Properties 4 | Number | NestControl | 1.0 | Shading / Properties 4 |  |
| 229 | `Opacity4` | Opacity 4 | Number | SliderControl | 1.0 | Shading / Properties 4 |  |
| 230 | `ElementShape4` | Appearance 4 | Number | MultiButtonControl | 2.0 | Shading / Properties 4 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 231 | `Thickness4` | Thickness 4 | Number | SliderControl | 0.02 | Shading / Properties 4 |  |
| 232 | `JoinStyle4` | Join Style 4 | Number | MultiButtonControl | 1.0 | Shading / Properties 4 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 233 | `MiterLimit4` | Miter Limit 4 | Number | SliderControl | 10.0 | Shading / Properties 4 |  |
| 234 | `LineStyle4` | Line Style 4 | Number | ComboControl | 0.0 | Shading / Properties 4 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 235 | `ExtendHorizontal4` | Extend Horizontal 4 | Number | SliderControl | 0.0 | Shading / Properties 4 |  |
| 236 | `ExtendVertical4` | Extend Vertical 4 | Number | SliderControl | 0.0 | Shading / Properties 4 |  |
| 237 | `Round4` | Round 4 | Number | SliderControl | 0.0 | Shading / Properties 4 |  |
| 238 | `ElementSeparator4` |  | Number | SeparatorControl | 0.0 | Shading / Properties 4 |  |
| 239 | `Type4` | Type 4 | Number | MultiButtonControl | 0.0 | Shading / Properties 4 | 0=Solid; 1=Image; 2=Gradient |
| 240 | `OverrideColor4` | Override Color Fonts 4 | Number | CheckboxControl | 1.0 | Shading / Properties 4 |  |
| 241 | `ElementSpacer4` |  | Number | SpacerControl | 0.0 | Shading / Properties 4 |  |
| 242 | `Red4` | Red 4 | Number | ColorControl | 0.0 | Shading / Properties 4 |  |
| 243 | `Green4` | Green 4 | Number | ColorControl | 0.0 | Shading / Properties 4 |  |
| 244 | `Blue4` | Blue 4 | Number | ColorControl | 1.0 | Shading / Properties 4 |  |
| 245 | `Alpha4` | Alpha 4 | Number | ColorControl | 1.0 | Shading / Properties 4 |  |
| 246 | `ImageShadingSampling4` | Image Sampling 4 | Number | MultiButtonControl | 1.0 | Shading / Properties 4 | 0=None; 1=Pixel; 2=Area |
| 247 | `ImageShadingEdges4` | Image Edges 4 | Number | MultiButtonControl | 1.0 | Shading / Properties 4 | 0=Black; 1=Wrap; 2=Duplicate |
| 248 | `ShadingMappingSpacer4` |  | Number | SpacerControl | 0.0 | Shading / Properties 4 |  |
| 249 | `ShadingMapping4` | Shading Mapping 4 | Number | MultiButtonControl | 1.0 | Shading / Properties 4 | 0=Stretch to Fit; 1=Maintain Aspect |
| 250 | `ShadingMappingAngle4` | Shading Mapping Angle 4 | Number | ScrewControl | 0.0 | Shading / Properties 4 |  |
| 251 | `ShadingMappingSize4` | Shading Mapping Size 4 | Number | SliderControl | 1.0 | Shading / Properties 4 |  |
| 252 | `ShadingMappingAspect4` | Shading Mapping Aspect 4 | Number | SliderControl | 1.0 | Shading / Properties 4 |  |
| 253 | `Softness4` | Softness 4 | Number | NestControl | 1.0 | Shading / Softness 4 |  |
| 254 | `SoftnessX4` | Softness X 4 | Number | SliderControl | 0.0 | Shading / Softness 4 |  |
| 255 | `SoftnessY4` | Softness Y 4 | Number | SliderControl | 0.0 | Shading / Softness 4 |  |
| 256 | `SoftnessOnFillColorToo4` | Apply Softness to Fill Color 4 | Number | CheckboxControl | 0.0 | Shading / Softness 4 |  |
| 257 | `SoftnessGlow4` | Softness Glow 4 | Number | SliderControl | 0.0 | Shading / Softness 4 |  |
| 258 | `SoftnessBlend4` | Softness Blend 4 | Number | SliderControl | 1.0 | Shading / Softness 4 |  |
| 259 | `Position4` | Position 4 | Number | NestControl | 1.0 | Shading / Position 4 |  |
| 260 | `PriorityBack4` | Priority 4 | Number | SliderControl | 5.0 | Shading / Position 4 |  |
| 261 | `Offset4` | Offset 4 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 4 |  |
| 262 | `OffsetZ4` | Offset Z 4 | Number | SliderControl | 0.0 | Shading / Position 4 |  |
| 263 | `Rotation4` | Rotation 4 | Number | NestControl | 0.0 | Shading / Rotation 4 |  |
| 264 | `AngleX4` | Angle X 4 | Number | ScrewControl | 0.0 | Shading / Rotation 4 |  |
| 265 | `AngleY4` | Angle Y 4 | Number | ScrewControl | 0.0 | Shading / Rotation 4 |  |
| 266 | `AngleZ4` | Angle Z 4 | Number | ScrewControl | 0.0 | Shading / Rotation 4 |  |
| 267 | `PivotNest4` | Pivot 4 | Number | NestControl | 0.0 | Shading / Pivot 4 |  |
| 268 | `Pivot4` | Pivot 4 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 4 |  |
| 269 | `PivotZ4` | Pivot Z 4 | Number | SliderControl | 0.0 | Shading / Pivot 4 |  |
| 270 | `Shear4` | Shear 4 | Number | NestControl | 0.0 | Shading / Shear 4 |  |
| 271 | `ShearX4` | Shear X 4 | Number | SliderControl | 0.0 | Shading / Shear 4 |  |
| 272 | `ShearY4` | Shear Y 4 | Number | SliderControl | 0.0 | Shading / Shear 4 |  |
| 273 | `Size4` | Size 4 | Number | NestControl | 0.0 | Shading / Size 4 |  |
| 274 | `SizeX4` | Size X 4 | Number | SliderControl | 1.0 | Shading / Size 4 |  |
| 275 | `SizeY4` | Size Y 4 | Number | SliderControl | 1.0 | Shading / Size 4 |  |
| 276 | `Properties5` | Properties 5 | Number | NestControl | 1.0 | Shading / Properties 5 |  |
| 277 | `Opacity5` | Opacity 5 | Number | SliderControl | 1.0 | Shading / Properties 5 |  |
| 278 | `ElementShape5` | Appearance 5 | Number | MultiButtonControl | 0.0 | Shading / Properties 5 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 279 | `Thickness5` | Thickness 5 | Number | SliderControl | 0.02 | Shading / Properties 5 |  |
| 280 | `JoinStyle5` | Join Style 5 | Number | MultiButtonControl | 1.0 | Shading / Properties 5 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 281 | `MiterLimit5` | Miter Limit 5 | Number | SliderControl | 10.0 | Shading / Properties 5 |  |
| 282 | `LineStyle5` | Line Style 5 | Number | ComboControl | 0.0 | Shading / Properties 5 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 283 | `ExtendHorizontal5` | Extend Horizontal 5 | Number | SliderControl | 0.0 | Shading / Properties 5 |  |
| 284 | `ExtendVertical5` | Extend Vertical 5 | Number | SliderControl | 0.0 | Shading / Properties 5 |  |
| 285 | `Round5` | Round 5 | Number | SliderControl | 0.0 | Shading / Properties 5 |  |
| 286 | `ElementSeparator5` |  | Number | SeparatorControl | 0.0 | Shading / Properties 5 |  |
| 287 | `Type5` | Type 5 | Number | MultiButtonControl | 0.0 | Shading / Properties 5 | 0=Solid; 1=Image; 2=Gradient |
| 288 | `OverrideColor5` | Override Color Fonts 5 | Number | CheckboxControl | 1.0 | Shading / Properties 5 |  |
| 289 | `ElementSpacer5` |  | Number | SpacerControl | 0.0 | Shading / Properties 5 |  |
| 290 | `Red5` | Red 5 | Number | ColorControl | 1.0 | Shading / Properties 5 |  |
| 291 | `Green5` | Green 5 | Number | ColorControl | 1.0 | Shading / Properties 5 |  |
| 292 | `Blue5` | Blue 5 | Number | ColorControl | 1.0 | Shading / Properties 5 |  |
| 293 | `Alpha5` | Alpha 5 | Number | ColorControl | 1.0 | Shading / Properties 5 |  |
| 294 | `ImageShadingSampling5` | Image Sampling 5 | Number | MultiButtonControl | 1.0 | Shading / Properties 5 | 0=None; 1=Pixel; 2=Area |
| 295 | `ImageShadingEdges5` | Image Edges 5 | Number | MultiButtonControl | 1.0 | Shading / Properties 5 | 0=Black; 1=Wrap; 2=Duplicate |
| 296 | `ShadingMappingSpacer5` |  | Number | SpacerControl | 0.0 | Shading / Properties 5 |  |
| 297 | `ShadingMapping5` | Shading Mapping 5 | Number | MultiButtonControl | 1.0 | Shading / Properties 5 | 0=Stretch to Fit; 1=Maintain Aspect |
| 298 | `ShadingMappingAngle5` | Shading Mapping Angle 5 | Number | ScrewControl | 0.0 | Shading / Properties 5 |  |
| 299 | `ShadingMappingSize5` | Shading Mapping Size 5 | Number | SliderControl | 1.0 | Shading / Properties 5 |  |
| 300 | `ShadingMappingAspect5` | Shading Mapping Aspect 5 | Number | SliderControl | 1.0 | Shading / Properties 5 |  |
| 301 | `Softness5` | Softness 5 | Number | NestControl | 1.0 | Shading / Softness 5 |  |
| 302 | `SoftnessX5` | Softness X 5 | Number | SliderControl | 0.0 | Shading / Softness 5 |  |
| 303 | `SoftnessY5` | Softness Y 5 | Number | SliderControl | 0.0 | Shading / Softness 5 |  |
| 304 | `SoftnessOnFillColorToo5` | Apply Softness to Fill Color 5 | Number | CheckboxControl | 0.0 | Shading / Softness 5 |  |
| 305 | `SoftnessGlow5` | Softness Glow 5 | Number | SliderControl | 0.0 | Shading / Softness 5 |  |
| 306 | `SoftnessBlend5` | Softness Blend 5 | Number | SliderControl | 1.0 | Shading / Softness 5 |  |
| 307 | `Position5` | Position 5 | Number | NestControl | 1.0 | Shading / Position 5 |  |
| 308 | `PriorityBack5` | Priority 5 | Number | SliderControl | 4.0 | Shading / Position 5 |  |
| 309 | `Offset5` | Offset 5 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 5 |  |
| 310 | `OffsetZ5` | Offset Z 5 | Number | SliderControl | 0.0 | Shading / Position 5 |  |
| 311 | `Rotation5` | Rotation 5 | Number | NestControl | 0.0 | Shading / Rotation 5 |  |
| 312 | `AngleX5` | Angle X 5 | Number | ScrewControl | 0.0 | Shading / Rotation 5 |  |
| 313 | `AngleY5` | Angle Y 5 | Number | ScrewControl | 0.0 | Shading / Rotation 5 |  |
| 314 | `AngleZ5` | Angle Z 5 | Number | ScrewControl | 0.0 | Shading / Rotation 5 |  |
| 315 | `PivotNest5` | Pivot 5 | Number | NestControl | 0.0 | Shading / Pivot 5 |  |
| 316 | `Pivot5` | Pivot 5 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 5 |  |
| 317 | `PivotZ5` | Pivot Z 5 | Number | SliderControl | 0.0 | Shading / Pivot 5 |  |
| 318 | `Shear5` | Shear 5 | Number | NestControl | 0.0 | Shading / Shear 5 |  |
| 319 | `ShearX5` | Shear X 5 | Number | SliderControl | 0.0 | Shading / Shear 5 |  |
| 320 | `ShearY5` | Shear Y 5 | Number | SliderControl | 0.0 | Shading / Shear 5 |  |
| 321 | `Size5` | Size 5 | Number | NestControl | 0.0 | Shading / Size 5 |  |
| 322 | `SizeX5` | Size X 5 | Number | SliderControl | 1.0 | Shading / Size 5 |  |
| 323 | `SizeY5` | Size Y 5 | Number | SliderControl | 1.0 | Shading / Size 5 |  |
| 324 | `Properties6` | Properties 6 | Number | NestControl | 1.0 | Shading / Properties 6 |  |
| 325 | `Opacity6` | Opacity 6 | Number | SliderControl | 1.0 | Shading / Properties 6 |  |
| 326 | `ElementShape6` | Appearance 6 | Number | MultiButtonControl | 0.0 | Shading / Properties 6 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 327 | `Thickness6` | Thickness 6 | Number | SliderControl | 0.02 | Shading / Properties 6 |  |
| 328 | `JoinStyle6` | Join Style 6 | Number | MultiButtonControl | 1.0 | Shading / Properties 6 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 329 | `MiterLimit6` | Miter Limit 6 | Number | SliderControl | 10.0 | Shading / Properties 6 |  |
| 330 | `LineStyle6` | Line Style 6 | Number | ComboControl | 0.0 | Shading / Properties 6 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 331 | `ExtendHorizontal6` | Extend Horizontal 6 | Number | SliderControl | 0.0 | Shading / Properties 6 |  |
| 332 | `ExtendVertical6` | Extend Vertical 6 | Number | SliderControl | 0.0 | Shading / Properties 6 |  |
| 333 | `Round6` | Round 6 | Number | SliderControl | 0.0 | Shading / Properties 6 |  |
| 334 | `ElementSeparator6` |  | Number | SeparatorControl | 0.0 | Shading / Properties 6 |  |
| 335 | `Type6` | Type 6 | Number | MultiButtonControl | 0.0 | Shading / Properties 6 | 0=Solid; 1=Image; 2=Gradient |
| 336 | `OverrideColor6` | Override Color Fonts 6 | Number | CheckboxControl | 1.0 | Shading / Properties 6 |  |
| 337 | `ElementSpacer6` |  | Number | SpacerControl | 0.0 | Shading / Properties 6 |  |
| 338 | `Red6` | Red 6 | Number | ColorControl | 1.0 | Shading / Properties 6 |  |
| 339 | `Green6` | Green 6 | Number | ColorControl | 1.0 | Shading / Properties 6 |  |
| 340 | `Blue6` | Blue 6 | Number | ColorControl | 1.0 | Shading / Properties 6 |  |
| 341 | `Alpha6` | Alpha 6 | Number | ColorControl | 1.0 | Shading / Properties 6 |  |
| 342 | `ImageShadingSampling6` | Image Sampling 6 | Number | MultiButtonControl | 1.0 | Shading / Properties 6 | 0=None; 1=Pixel; 2=Area |
| 343 | `ImageShadingEdges6` | Image Edges 6 | Number | MultiButtonControl | 1.0 | Shading / Properties 6 | 0=Black; 1=Wrap; 2=Duplicate |
| 344 | `ShadingMappingSpacer6` |  | Number | SpacerControl | 0.0 | Shading / Properties 6 |  |
| 345 | `ShadingMapping6` | Shading Mapping 6 | Number | MultiButtonControl | 1.0 | Shading / Properties 6 | 0=Stretch to Fit; 1=Maintain Aspect |
| 346 | `ShadingMappingAngle6` | Shading Mapping Angle 6 | Number | ScrewControl | 0.0 | Shading / Properties 6 |  |
| 347 | `ShadingMappingSize6` | Shading Mapping Size 6 | Number | SliderControl | 1.0 | Shading / Properties 6 |  |
| 348 | `ShadingMappingAspect6` | Shading Mapping Aspect 6 | Number | SliderControl | 1.0 | Shading / Properties 6 |  |
| 349 | `Softness6` | Softness 6 | Number | NestControl | 1.0 | Shading / Softness 6 |  |
| 350 | `SoftnessX6` | Softness X 6 | Number | SliderControl | 0.0 | Shading / Softness 6 |  |
| 351 | `SoftnessY6` | Softness Y 6 | Number | SliderControl | 0.0 | Shading / Softness 6 |  |
| 352 | `SoftnessOnFillColorToo6` | Apply Softness to Fill Color 6 | Number | CheckboxControl | 0.0 | Shading / Softness 6 |  |
| 353 | `SoftnessGlow6` | Softness Glow 6 | Number | SliderControl | 0.0 | Shading / Softness 6 |  |
| 354 | `SoftnessBlend6` | Softness Blend 6 | Number | SliderControl | 1.0 | Shading / Softness 6 |  |
| 355 | `Position6` | Position 6 | Number | NestControl | 1.0 | Shading / Position 6 |  |
| 356 | `PriorityBack6` | Priority 6 | Number | SliderControl | 3.0 | Shading / Position 6 |  |
| 357 | `Offset6` | Offset 6 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 6 |  |
| 358 | `OffsetZ6` | Offset Z 6 | Number | SliderControl | 0.0 | Shading / Position 6 |  |
| 359 | `Rotation6` | Rotation 6 | Number | NestControl | 0.0 | Shading / Rotation 6 |  |
| 360 | `AngleX6` | Angle X 6 | Number | ScrewControl | 0.0 | Shading / Rotation 6 |  |
| 361 | `AngleY6` | Angle Y 6 | Number | ScrewControl | 0.0 | Shading / Rotation 6 |  |
| 362 | `AngleZ6` | Angle Z 6 | Number | ScrewControl | 0.0 | Shading / Rotation 6 |  |
| 363 | `PivotNest6` | Pivot 6 | Number | NestControl | 0.0 | Shading / Pivot 6 |  |
| 364 | `Pivot6` | Pivot 6 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 6 |  |
| 365 | `PivotZ6` | Pivot Z 6 | Number | SliderControl | 0.0 | Shading / Pivot 6 |  |
| 366 | `Shear6` | Shear 6 | Number | NestControl | 0.0 | Shading / Shear 6 |  |
| 367 | `ShearX6` | Shear X 6 | Number | SliderControl | 0.0 | Shading / Shear 6 |  |
| 368 | `ShearY6` | Shear Y 6 | Number | SliderControl | 0.0 | Shading / Shear 6 |  |
| 369 | `Size6` | Size 6 | Number | NestControl | 0.0 | Shading / Size 6 |  |
| 370 | `SizeX6` | Size X 6 | Number | SliderControl | 1.0 | Shading / Size 6 |  |
| 371 | `SizeY6` | Size Y 6 | Number | SliderControl | 1.0 | Shading / Size 6 |  |
| 372 | `Properties7` | Properties 7 | Number | NestControl | 1.0 | Shading / Properties 7 |  |
| 373 | `Opacity7` | Opacity 7 | Number | SliderControl | 1.0 | Shading / Properties 7 |  |
| 374 | `ElementShape7` | Appearance 7 | Number | MultiButtonControl | 0.0 | Shading / Properties 7 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 375 | `Thickness7` | Thickness 7 | Number | SliderControl | 0.02 | Shading / Properties 7 |  |
| 376 | `JoinStyle7` | Join Style 7 | Number | MultiButtonControl | 1.0 | Shading / Properties 7 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 377 | `MiterLimit7` | Miter Limit 7 | Number | SliderControl | 10.0 | Shading / Properties 7 |  |
| 378 | `LineStyle7` | Line Style 7 | Number | ComboControl | 0.0 | Shading / Properties 7 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 379 | `ExtendHorizontal7` | Extend Horizontal 7 | Number | SliderControl | 0.0 | Shading / Properties 7 |  |
| 380 | `ExtendVertical7` | Extend Vertical 7 | Number | SliderControl | 0.0 | Shading / Properties 7 |  |
| 381 | `Round7` | Round 7 | Number | SliderControl | 0.0 | Shading / Properties 7 |  |
| 382 | `ElementSeparator7` |  | Number | SeparatorControl | 0.0 | Shading / Properties 7 |  |
| 383 | `Type7` | Type 7 | Number | MultiButtonControl | 0.0 | Shading / Properties 7 | 0=Solid; 1=Image; 2=Gradient |
| 384 | `OverrideColor7` | Override Color Fonts 7 | Number | CheckboxControl | 1.0 | Shading / Properties 7 |  |
| 385 | `ElementSpacer7` |  | Number | SpacerControl | 0.0 | Shading / Properties 7 |  |
| 386 | `Red7` | Red 7 | Number | ColorControl | 1.0 | Shading / Properties 7 |  |
| 387 | `Green7` | Green 7 | Number | ColorControl | 1.0 | Shading / Properties 7 |  |
| 388 | `Blue7` | Blue 7 | Number | ColorControl | 1.0 | Shading / Properties 7 |  |
| 389 | `Alpha7` | Alpha 7 | Number | ColorControl | 1.0 | Shading / Properties 7 |  |
| 390 | `ImageShadingSampling7` | Image Sampling 7 | Number | MultiButtonControl | 1.0 | Shading / Properties 7 | 0=None; 1=Pixel; 2=Area |
| 391 | `ImageShadingEdges7` | Image Edges 7 | Number | MultiButtonControl | 1.0 | Shading / Properties 7 | 0=Black; 1=Wrap; 2=Duplicate |
| 392 | `ShadingMappingSpacer7` |  | Number | SpacerControl | 0.0 | Shading / Properties 7 |  |
| 393 | `ShadingMapping7` | Shading Mapping 7 | Number | MultiButtonControl | 1.0 | Shading / Properties 7 | 0=Stretch to Fit; 1=Maintain Aspect |
| 394 | `ShadingMappingAngle7` | Shading Mapping Angle 7 | Number | ScrewControl | 0.0 | Shading / Properties 7 |  |
| 395 | `ShadingMappingSize7` | Shading Mapping Size 7 | Number | SliderControl | 1.0 | Shading / Properties 7 |  |
| 396 | `ShadingMappingAspect7` | Shading Mapping Aspect 7 | Number | SliderControl | 1.0 | Shading / Properties 7 |  |
| 397 | `Softness7` | Softness 7 | Number | NestControl | 1.0 | Shading / Softness 7 |  |
| 398 | `SoftnessX7` | Softness X 7 | Number | SliderControl | 0.0 | Shading / Softness 7 |  |
| 399 | `SoftnessY7` | Softness Y 7 | Number | SliderControl | 0.0 | Shading / Softness 7 |  |
| 400 | `SoftnessOnFillColorToo7` | Apply Softness to Fill Color 7 | Number | CheckboxControl | 0.0 | Shading / Softness 7 |  |
| 401 | `SoftnessGlow7` | Softness Glow 7 | Number | SliderControl | 0.0 | Shading / Softness 7 |  |
| 402 | `SoftnessBlend7` | Softness Blend 7 | Number | SliderControl | 1.0 | Shading / Softness 7 |  |
| 403 | `Position7` | Position 7 | Number | NestControl | 1.0 | Shading / Position 7 |  |
| 404 | `PriorityBack7` | Priority 7 | Number | SliderControl | 2.0 | Shading / Position 7 |  |
| 405 | `Offset7` | Offset 7 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 7 |  |
| 406 | `OffsetZ7` | Offset Z 7 | Number | SliderControl | 0.0 | Shading / Position 7 |  |
| 407 | `Rotation7` | Rotation 7 | Number | NestControl | 0.0 | Shading / Rotation 7 |  |
| 408 | `AngleX7` | Angle X 7 | Number | ScrewControl | 0.0 | Shading / Rotation 7 |  |
| 409 | `AngleY7` | Angle Y 7 | Number | ScrewControl | 0.0 | Shading / Rotation 7 |  |
| 410 | `AngleZ7` | Angle Z 7 | Number | ScrewControl | 0.0 | Shading / Rotation 7 |  |
| 411 | `PivotNest7` | Pivot 7 | Number | NestControl | 0.0 | Shading / Pivot 7 |  |
| 412 | `Pivot7` | Pivot 7 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 7 |  |
| 413 | `PivotZ7` | Pivot Z 7 | Number | SliderControl | 0.0 | Shading / Pivot 7 |  |
| 414 | `Shear7` | Shear 7 | Number | NestControl | 0.0 | Shading / Shear 7 |  |
| 415 | `ShearX7` | Shear X 7 | Number | SliderControl | 0.0 | Shading / Shear 7 |  |
| 416 | `ShearY7` | Shear Y 7 | Number | SliderControl | 0.0 | Shading / Shear 7 |  |
| 417 | `Size7` | Size 7 | Number | NestControl | 0.0 | Shading / Size 7 |  |
| 418 | `SizeX7` | Size X 7 | Number | SliderControl | 1.0 | Shading / Size 7 |  |
| 419 | `SizeY7` | Size Y 7 | Number | SliderControl | 1.0 | Shading / Size 7 |  |
| 420 | `Properties8` | Properties 8 | Number | NestControl | 1.0 | Shading / Properties 8 |  |
| 421 | `Opacity8` | Opacity 8 | Number | SliderControl | 1.0 | Shading / Properties 8 |  |
| 422 | `ElementShape8` | Appearance 8 | Number | MultiButtonControl | 0.0 | Shading / Properties 8 | 0=Text Fill; 1=Text Outline; 2=Border Fill; 3=Border Outline |
| 423 | `Thickness8` | Thickness 8 | Number | SliderControl | 0.02 | Shading / Properties 8 |  |
| 424 | `JoinStyle8` | Join Style 8 | Number | MultiButtonControl | 1.0 | Shading / Properties 8 | 0=Bevel; 1=Round; 2=Miter; 3=Miter Clip |
| 425 | `MiterLimit8` | Miter Limit 8 | Number | SliderControl | 10.0 | Shading / Properties 8 |  |
| 426 | `LineStyle8` | Line Style 8 | Number | ComboControl | 0.0 | Shading / Properties 8 | 0=Solid; 1=Dash; 2=Dot; 3=Dash Dot; 4=Dash Dot Dot |
| 427 | `ExtendHorizontal8` | Extend Horizontal 8 | Number | SliderControl | 0.0 | Shading / Properties 8 |  |
| 428 | `ExtendVertical8` | Extend Vertical 8 | Number | SliderControl | 0.0 | Shading / Properties 8 |  |
| 429 | `Round8` | Round 8 | Number | SliderControl | 0.0 | Shading / Properties 8 |  |
| 430 | `ElementSeparator8` |  | Number | SeparatorControl | 0.0 | Shading / Properties 8 |  |
| 431 | `Type8` | Type 8 | Number | MultiButtonControl | 0.0 | Shading / Properties 8 | 0=Solid; 1=Image; 2=Gradient |
| 432 | `OverrideColor8` | Override Color Fonts 8 | Number | CheckboxControl | 1.0 | Shading / Properties 8 |  |
| 433 | `ElementSpacer8` |  | Number | SpacerControl | 0.0 | Shading / Properties 8 |  |
| 434 | `Red8` | Red 8 | Number | ColorControl | 1.0 | Shading / Properties 8 |  |
| 435 | `Green8` | Green 8 | Number | ColorControl | 1.0 | Shading / Properties 8 |  |
| 436 | `Blue8` | Blue 8 | Number | ColorControl | 1.0 | Shading / Properties 8 |  |
| 437 | `Alpha8` | Alpha 8 | Number | ColorControl | 1.0 | Shading / Properties 8 |  |
| 438 | `ImageShadingSampling8` | Image Sampling 8 | Number | MultiButtonControl | 1.0 | Shading / Properties 8 | 0=None; 1=Pixel; 2=Area |
| 439 | `ImageShadingEdges8` | Image Edges 8 | Number | MultiButtonControl | 1.0 | Shading / Properties 8 | 0=Black; 1=Wrap; 2=Duplicate |
| 440 | `ShadingMappingSpacer8` |  | Number | SpacerControl | 0.0 | Shading / Properties 8 |  |
| 441 | `ShadingMapping8` | Shading Mapping 8 | Number | MultiButtonControl | 1.0 | Shading / Properties 8 | 0=Stretch to Fit; 1=Maintain Aspect |
| 442 | `ShadingMappingAngle8` | Shading Mapping Angle 8 | Number | ScrewControl | 0.0 | Shading / Properties 8 |  |
| 443 | `ShadingMappingSize8` | Shading Mapping Size 8 | Number | SliderControl | 1.0 | Shading / Properties 8 |  |
| 444 | `ShadingMappingAspect8` | Shading Mapping Aspect 8 | Number | SliderControl | 1.0 | Shading / Properties 8 |  |
| 445 | `Softness8` | Softness 8 | Number | NestControl | 1.0 | Shading / Softness 8 |  |
| 446 | `SoftnessX8` | Softness X 8 | Number | SliderControl | 0.0 | Shading / Softness 8 |  |
| 447 | `SoftnessY8` | Softness Y 8 | Number | SliderControl | 0.0 | Shading / Softness 8 |  |
| 448 | `SoftnessOnFillColorToo8` | Apply Softness to Fill Color 8 | Number | CheckboxControl | 0.0 | Shading / Softness 8 |  |
| 449 | `SoftnessGlow8` | Softness Glow 8 | Number | SliderControl | 0.0 | Shading / Softness 8 |  |
| 450 | `SoftnessBlend8` | Softness Blend 8 | Number | SliderControl | 1.0 | Shading / Softness 8 |  |
| 451 | `Position8` | Position 8 | Number | NestControl | 1.0 | Shading / Position 8 |  |
| 452 | `PriorityBack8` | Priority 8 | Number | SliderControl | 1.0 | Shading / Position 8 |  |
| 453 | `Offset8` | Offset 8 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Position 8 |  |
| 454 | `OffsetZ8` | Offset Z 8 | Number | SliderControl | 0.0 | Shading / Position 8 |  |
| 455 | `Rotation8` | Rotation 8 | Number | NestControl | 0.0 | Shading / Rotation 8 |  |
| 456 | `AngleX8` | Angle X 8 | Number | ScrewControl | 0.0 | Shading / Rotation 8 |  |
| 457 | `AngleY8` | Angle Y 8 | Number | ScrewControl | 0.0 | Shading / Rotation 8 |  |
| 458 | `AngleZ8` | Angle Z 8 | Number | ScrewControl | 0.0 | Shading / Rotation 8 |  |
| 459 | `PivotNest8` | Pivot 8 | Number | NestControl | 0.0 | Shading / Pivot 8 |  |
| 460 | `Pivot8` | Pivot 8 | Point | OffsetControl | {1: 0.0, 2: 0.0, 3: 0.0} | Shading / Pivot 8 |  |
| 461 | `PivotZ8` | Pivot Z 8 | Number | SliderControl | 0.0 | Shading / Pivot 8 |  |
| 462 | `Shear8` | Shear 8 | Number | NestControl | 0.0 | Shading / Shear 8 |  |
| 463 | `ShearX8` | Shear X 8 | Number | SliderControl | 0.0 | Shading / Shear 8 |  |
| 464 | `ShearY8` | Shear Y 8 | Number | SliderControl | 0.0 | Shading / Shear 8 |  |
| 465 | `Size8` | Size 8 | Number | NestControl | 0.0 | Shading / Size 8 |  |
| 466 | `SizeX8` | Size X 8 | Number | SliderControl | 1.0 | Shading / Size 8 |  |
| 467 | `SizeY8` | Size Y 8 | Number | SliderControl | 1.0 | Shading / Size 8 |  |
| 468 | `CommentsNest` | Comments | Number | NestControl | 1.0 | Common / Comments |  |
| 469 | `Comments` | Comments | Text | TextEditControl | '' | Common / Comments |  |
| 470 | `FrameRenderScriptNest` | Frame Render Script | Number | NestControl | 1.0 | Common / Frame Render Script |  |
| 471 | `FrameRenderScript` | Frame Render Script | Text | TextEditControl | '' | Common / Frame Render Script |  |
| 472 | `StartRenderScripts` | Start Render Scripts | Number | NestControl | 0.0 | Common / Start Render Scripts |  |
| 473 | `StartRenderScript` | Start Render Script | Text | TextEditControl | '' | Common / Start Render Scripts |  |
| 474 | `EndRenderScripts` | End Render Scripts | Number | NestControl | 0.0 | Common / End Render Scripts |  |
| 475 | `EndRenderScript` | End Render Script | Text | TextEditControl | '' | Common / End Render Scripts |  |
