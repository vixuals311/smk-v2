BUGS FOUND AND FIXED (build/make_macros.py): (1) CardStack L2..L4 Style expression read UIL_L2.Font.Value of a linked input -> evaluates None -> render "composition could not be processed" (P1 failed); now reads UIL_L1.Font.Value. (2) StatCard number expression concatenated UIS_Ctrl.Prefix/Suffix (Text objects, cdata) -> None -> render failed (T1); now .Value. (3) StatCard Value control clamped at 1,000,000 by script (INP_MaxAllowed) -> now +-1e12. (4) StatCard Soft/Glass/Neon did not restyle number/caption (labels list empty) -> Soft showed white text on a light card; now UIS_Num+UIS_Label.
P1 first ink frames per card 2,4,7,11; last ink 114,112,112,112; last frame empty; frame 0 empty
P2 pitch px at gap 0/0.015/0.05: 134 (touching run 538)/163/230 = (0.07+gap)*1920; changed case pitch 173=(0.06+0.03)*1920; 1080p/4K fractions top 0.1224 pitch 0.0849-0.0852; vertical top 0.463 (y fraction of height) pitch 0.0843-0.0852
P3 weights 0-7 all render, ink px 392..1347 per card 1; Arial renders; text independent (different widths); colour (255,230,26)
P4 stagger 0: first ink 2,2,2,2; 0.12: 2,4,7,11; 0.3: 2,9,17,23; Spring-in Elastic-out: last ink 108 x4; last frame empty all; trim46: first 2,4,7,11 last 40,38,38,38 f45 empty
P5 cost 60fps cold a/b: Stack1 87.3/27.5; Stack3 265.6(partial)/75.2; UIBlock x4 33.7/33.5; node count 20 inner tools each (CardStack 20, UIBlock 5 x4)
T1 '0' to f7, 9,519 at f20, 12,066 f30, 12,480 from f40 on; card ink 0 at f0, 2601 f40..100, 136 f115, 0 f118-119
T2 last-frame strings: 0 '0'; 7 '7'; 999 '999'; 1000 '1,000'; 1234567 '1,234,567' (after fix; before 1,000,000 clamp); 1000000 '1,000,000'; 12480 dec1 '12,480.0' dec2 '12,480.00'; commas off '12480'; prefix $ '$12,480'; suffix % '12,480%', K '12,480K'; 1234.5 dec2 prefix $ suffix ' USD' '$1,234.50 USD'; 12345.678 '$12,345.68K'
T3 engines max/min: Ease 12480/0; Spring 12614 (+1.07%); Bounce 12480; Elastic 17065 (+36.7%); Overshoot 13726 (+9.98%); Inertia 12480; no negative values (min 0.0); all end on '12,480' and never change after settling (f36-41)
T4 strings at t=0.2,0.3,0.5,1.0,1.5,1.7,2.0 s identical at 24/30/60: 0,0,4,621,10,920,12,444,12,480,12,480
T5 long value '1,234,567,890' text bbox 688..1234 (546 px) vs card 499 px -> overflows the card by ~22 px each side, centred, not clipped by the frame; weights 0/4/5/7 Arial TNR Impact complete
T6 cost 60fps cold: 1 stat card 25.3/16.1; 5 stat cards 90.0/42.4
D1 expression P2 'Point(UID_Card.CX, UID_Card.CY)' evaluates (0.6,0.4)
D2 tip offset from button centre (0,+1) px at 4 positions/widths; ripple ring centre (1151.5,647.5) vs tip (1152,649)
D4 cursor fades in f11, arrives within 4 px at f46 (Smooth), Snappy f28 near, Spring overshoots to (1204,586); fast M2 0.6/start 0.2 -> within 4 px f27; button first f4; last cursor f112
D5 cursor image 1080x1920 / 3840x2160 full frame, tip offset (0,+1)
D6 cost 60fps cold ClickDemo 27.5/16.4
V1 22 macros listed; 16 products + 6 older all complete; 0 expressions returning None (1064 + 83 evaluated); inner tools UIBlock 5, CardStack 20, StatCard 7, ClickDemo 7 equal across variants; published controls 82/83/94/93 equal across variants
V2 contrast text vs fill-over-test-bg: Glass 5.8:1, Neon 17.5:1, Soft 14.6:1
O2 60fps cold a/b: 1080p NoFx 5.2/4.8, outline20 10.0/8.9 (Phase10 10.9/10.7); 4K NoFx 18.4/18.3, outline20 45.7/45.8 (Phase10 70.5/70.8); outer edge std 0.00 px at 20 and 40 px
