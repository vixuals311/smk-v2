B1 bloom vs bypass: 293,147 differing px (max diff 74/109/160), Bloom output window (-158,-158,2078,1238); halo blue excess right of the card at 5/30/60/100/150: 50/10/4/0/0
B2 before fix (6 levels): left excess at 1/10/30/60/100: R10 144/4/0/0/0 ext 12; R40 154/22/4/1/0 ext 42; R120 154/38/10/2/1 ext 70; R300 153/35/13/1/1 (R300 ~ R120: pyramid saturated)
B2 after fix (extra halvings sh=ceil(log2(R/128)) up to 3): R300 132/48/23/9/5/1 (halo clearly larger); R120 unchanged
B3 square Look Max R120 vs Bloom R120: mean abs diff 3.32/255 (text 3.49); Look excess 141/85/49/21/2 at 1/10/30/60/100 ext 104; Bloom 151/34/11/4/0 ext 74
B4 I0.5/1.2/3 left d=10: 16/37/95; S0.5/1/2 d=10: 91/37/6, d=60 27/2/0, d=100 6/0/0; red ok; Brightness left (bright) 132/27/7/2, right 0
B5 behind object centre (204,77,77)=source; glow only centre (115,166,255); additive (255,243,255); fringe: additive alpha-inconsistent 11 px, fg>alpha 23 px (max 5.4); behind/glow only/text 0
B6 Bloom DW canvas text (-392,-392,2312,1472) = 1.3*300+2 pad; 400x200 image (-84,-84,484,284); halo continues past image bounds smoothly (13,7,3,1); full-frame additive: border (205,240,255), corner (171,191,225) vs interior (243,255,255) = glow falls off at frame edge
B7 before fix 4K down vs 1080p mean 0.130 max 50, extent/width 0.0385 (1080p) 0.0198 (4K); after fix mean 0.013 max 50, extent/width 0.0339/0.0339/0.0398 (1080p/4K/1080x1920); fps 24/30/60 at 0.5/1.0 s diff 0
B8 60fps cold 300f (a/b): 1080p NoFx 11.6/8.6, Bloom R40 18.6/13.0, R300 19.3/13.2, Look Max R120 18.4/12.2; 4K NoFx 19.6/18.3, Bloom R40 27.0/20.4, R300 26.1/20.0, Look Max R120 26.0/22.2; 5 NoFx 35.4/18.3 Bloom 66.3/30.7; 10 NoFx 68.6/31.0 Bloom 132.1/58.0
B9 animated: object px f10 2916 f40 2912 f119 0, glow px 3872/3793/0; glow-without-object only f118 (fade tail); trim46: glow follows, f45 object+glow both present (Shape Out not tied to trimmed range)
B10 two instances: ids Background/Fuse.SMK2_Bloom/Fuse.SMK2_Shape/MediaOut/Merge/Note; restart pending
B11 inputs: custom Glow From, Radius (px @1920), Intensity, Brightness Threshold, Spread (gamma), Glow Colour, Glow Behind Object, Glow Only, Opacity; no duplicate ids
