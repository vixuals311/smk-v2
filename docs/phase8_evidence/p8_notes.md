R1 R1_defaults: Shape card left/top edge (177,184,198)/(173,180,195) vs source (115,128,153); right/bottom (67,74,89); centre identical; outside bg identical (diff 0); card interior 20 px in differs by up to 13-15/255 (bevel tail, centre exact); text+ and TextLetter show bevel (r1_relief.png)
R2 directions on grey card edge delta (left/right/top/bottom): 0: -77/+76/+3/-4 (lit right); 90: +1/-1/+77/-79 (lit top); 135: +55/-55/+52/-53 (lit upper-left); 225: +54/-53/-57/+58 (lit lower-left)
R3 size2/8/30 at depth2: lit width(>2) 5/19/69 px, first px +54/+60/+62; depth0/1/2/6 at size 8: 0/+35/+60/+89 (monotone), shadow side -0/-34/-58/-87
R4 inner white border 14px on dark card: Alpha mode profile 255,255,255,255,255,31.. (no relief); Brightness mode 255,255,200,153,19,24,29,31 (relief at inner edge)
R5 relief map: flat (127,127,127), left edge 182, right 72, top 180; outside object = background unchanged (map only inside alpha)
R6 premult bright/dark: default and size30 depth4: alpha-inconsistent 0, fg<0 0 (min -0.6), fg>alpha 0
R7 4K down vs 1080p mean 0.012/255 max 12; 24/30/60 at 0.5s max diff 0; vertical 1080x1920 bevel narrower in proportion to width (px@1920): lit edge profile 1080p [61,49,35,7,0], 1080x1920 [56,38,9,0,0]
R7 cost 60fps 300f cold PNG (a/b): 1080p NoFx 11.2/8.3, S8 Normal 17.4/12.1, S30 High 17.6/12.2; 4K NoFx 19.1/18.4, S8 Normal 24.5/19.0, S30 High 25.2/19.9
F1 F1_defaults: Shape/Text+/Look standing objects mirrored below baseline, fades out (f1_defaults.png); faint horizontal banding visible on gradient reflection
F2 baseline rows 864/648/324 reflection starts at baseline+0 (gap 0), gap +20 -> starts +20 rows below, gap -10 -> overlaps 10 rows above; extent limited by object height (228 px) and Length (100 -> 92 px visible); baseline 0.2 reflection ends at frame bottom (row 1079)
F3 right-edge 10-90% width at +5/+40/+100/+200/+350 rows: growth0 [0,0,0,0,-]; growth4 [0,1,2,8,14]; growth15 [1,3,8,31,57]; growth4+blur0 10 [5,6,7,18,22]; growth15 Q0 [1,3,8,31,54]; Q2 [1,3,7,31,46]; stepped ghost streaks visible at all qualities, Q2 smoother
F4 ripple p2p = 2*amp (12/40/40), zero at baseline, speed sign flips direction, t=0.25 vs 0.75 differ, 24fps frame6 == 60fps frame15 pixel-identical (diff 0)
F5 tint red a1 refl (212,8,10) object unchanged white; blue a0.5 (23,23,133) (alpha scales opacity, colour multiplies); keep off object = bg (38,38,51)
F6 premult bright/dark: alpha-inconsistent 0, fg<0 0, fg>alpha 0 (card and text)
F7 before fix: Text+ canvas small DoD (819,705,1108,808): reflection NOT clipped (output DW = canvas); 400x200 image: reflection cut at image bottom (16 px of 89). FIX: SMK2_Reflection pads IMG_DataWindow below and sideways + kernel off/osize
F7 after fix: small 400x200 image Reflection DW (0,-170,400,200); reflection now reaches row 711 (image bottom 640) instead of being cut at 639; canvas Text+ case unchanged (diff bbox only the small image)
F8 1080p/1080x1920/4K same look (4K down vs 1080p mean 0.010/255 max 85; reflection depth/width 0.1422/0.1417/0.1422); 24/30/60 fps frames at 0.5 s and 1.0 s pixel-identical; cost 60fps cold 1080p 17.6/12.0 ms (baseline 11.2/8.3), 4K 24.5/18.5 (baseline 19.1/18.4)
C1 C1_defaults solid red page: pre-delay frames identical to page (frames 0-8 coverage 1.0, 1 unique colour); roll travels right->left (covered columns 0..max falling 1912->0); gone by frame 34 (1.42 s = 0.2+1.2); last frame empty. Structure at f18: flat page 0-610 | paper back 610-1225 (hard edge = paper end, with drop shadow on page) | roll crest 1225 | nothing
C2 C2_reveal: frame 2 page intact, frame 18 reveal (51,204,77) beyond crest, frame 36 full reveal; crest edge was a 1-px hard step (BUG: t<=R cut the half pixel) -> FIX pagecurl t<=R+0.5 oracle+kernel + test
C3 manual 0/.25/.5/.75/1: progress 0 pixel-identical to source (diff 0); coverage 1.000/0.779/0.521/0.263/0.000 (monotone), 1 gone
C4 directions 0/90/180/270: curl travels in direction (remaining page ahead; centroid offset +462/+255/+465/+252 px), far edge straight (constant per scanline: 925/574/994/505); 45: boundary slope dx/dy 1.000 residual 1.9 px (perpendicular to travel)
C5 15 renders (c5_contact_sheet.png): one hard step per render at the end of the paper back (x=43,150,428 for R20/70/200) = paper edge, no seam inside roll; shadow/ambient/light/back controls act as named
C6 auto in: coverage 0 at frames 0-4, 0.4 at f18, 1.0 from f30 to 119, last frame = page colour only
C7 progress 0 vs source pixel-identical (4 pages); at 0.5 holes between letters stay transparent (bg), flap shadow under back region
C8 24/30/60 fps frames at 0.5 s and 1.0 s pixel-identical; trimmed 46-frame range: coverage f0 1.0 f20 0.438 f33 0 f45 0 (curl time is clip-length independent)
C9 two textures AddInput src+bg: accepted; C1/C2 render the curl and the reveal (no pass-through fallback); console text not readable (Resolve logs contain no GPU failed lines)
C10 4K down vs 1080p mean 0.024 max 5; far edge/width 0.5177/0.5180/0.5176; cost 60fps cold (a/b) 1080p NoFx 5.3/4.6 curl 10.2/8.3; 4K NoFx 18.2/18.2 curl 19.7/18.8
L1 R120 Draft/Normal/High vs Max mean diff 2.62/1.52/1.52 (/255); ring roughness 1.23/1.23/1.23/1.04; spread 0.5/1/2 blue excess d=10: 136/82/29, d=60: 65/19/1, d=100: 21/2/0
L2 glow only: object removed, glow centre (115,166,255), with object on top ok
L3 ellipse outline 20: outer radius mean 19.37 std 0.48 (min19 max20); Text+ still shows fine serration at outer corners
L4 Look inputs: no duplicate custom inputs (only Fusion standard Comments/Frame Render Script repeated)
E K11 re-test (192 cap): max deviation 1080p/1080x1920/4K: Curve 0 (straight w/o magnet), Bezier 0.017/0.015/0.033, Spline N6 0.174/0.304/0.347 px (was 0.71/1.18/1.41); 4K crop smooth, no facets
E K13 cold 60fps 300f: 1: 12.0/8.9 ms, 5: 35.1/18.1, 10: 64.4/30.3 (Phase 7: 12.8/9.7, 38.3/19.6, 70.0/32.0)
S12 all 4 methods work, both Defer on and off give identical results (10-90% edge width m0 1, m1 5, m2 22, m3 10 px at 1080p; 4K 1/6/25/11); intermediate W/4xH/4 sizes OK; cost 60fps cold (a/b): 1080p NoFx 11.3/8.4, m0 17.0/12.0, m1 17.4/12.4, m3 18.0/12.5; 4K NoFx 24.5/21.6, m0 33.0/27.1, m1 33.3/26.9, m3 34.0/24.1
