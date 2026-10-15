S1 shadow vs bypass: 448,892 px differ (max 102/102/104), output window (-2,-285,2205,1082) on canvas inputs
S2 dir 0/45/90/135/180/-45/-90 thin bars (4x150 px): shadow goes right/up-right/up/up-left/left/down-right/down; centre-line reach 294/294/300/294/240(frame edge)/294/300 px for L300; 0 non-monotone dips; values at 10/100/200 px 99/69/34 (diagonals), 178/94/59 (along the bar)
S3 reach (>=2/255) from object edge: L50 49, L200 198, L400 396, L1000 993; curve 0.5 at L/4 177 vs 153 (curve 1) vs 114 (curve 2); reach c0.5 398, c2 370
S4 premult red a0.6 / black a1 op .5 / red text: alpha-inconsistent 0, fg<0 0, fg>alpha 0; shadow colour on dark (143,12,12)
S5 DW: text canvas (-2,-427,2347,1082) = padded right/bottom for -45 L600 only; 400x200 image (-2,-91,491,202); shadow reaches ~594 px diag from text corner
S6 4K down vs 1080p mean 0.037 max 46; reach/width 0.1458/0.1461/0.1444; fps 24/30/60 diff 0
S7 Shape: first object f1 first shadow f1 last obj 116 last shadow 117 corr .742; TextLetter first obj f2 shadow f1, last obj 115 shadow 118, corr .986
S8 60fps cold (a/b): 1080p NoFx 12.0/8.5 L100 19.7/13.7 L1000 20.1/14.2; 4K NoFx 18.5/17.9 L100 26.5/20.5 L1000 30.1/21.3; 5: NoFx 36.0/18.5 shadow(L400) 64.9/32.5; 10: NoFx 66.4/30.8 shadow 123.9/60.0
F1 grain: mean abs diff vs Q2 (growth15): Q0 0.20, Q1 0.32 /255; streaks gone visually
F2 ripple0 frame-to-frame diff 0.0 (0.003 once); ripple6 0.37 (movement); grain rms 2.23 constant
F3 cost growth15 Q1 ripple6: 1080p 18.5/12.6 (Phase 8 growth4: 17.6/12.0), 4K 24.8/19.5 (24.5/18.5)
O1 ellipse outline 20: mean 19.46 std 0.53; text stem outer edge std 0.00 px at 6/20/40
O2 cost: 1080p NoFx 5.3/4.8 Outline20 10.9/10.7; 4K NoFx 17.9/18.3 Outline20 70.5/70.8
I1 Bloom default intensity 4 vs Look R120 Max: blue excess 191/111/35/10/0 vs 141/85/49/21/2; mean abs diff 2.45
