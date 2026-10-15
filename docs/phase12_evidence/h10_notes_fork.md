# H10 numbers handed over (1080p, 60 fps comp, 300 frames, cold PNG, ms/frame first run a / second run b)
Each instance has its own source/parameters; memory = Resolve.exe working set at 18:51 after all runs: ~7.4 GB (not measured per comp).
| Comp | a | b |
|---|---|---|
| H10_TextLetter_x20 (12 letters each) | 408.2 | 279.6 |
| H10_UIBlock_x20 | 108.2 | 107.3 |
| H10_StatCard_x10 | 184.5 | 75.3 |
| H10_CardStack_x10 | run a done (≈ in p8bench/H10_CardStack_x10_1080p_a), run b NOT measured; thread died |
| Bloom x5 (Shape-fed, H9S_Bloom_x5_1080p) | 110.8 | 80.1 |
Baseline Card x5 46.8/26.4, x10 83.3/33.1 (H9S_Card_*). Resolve responsive (scripting calls returned) after every run; one crash earlier at 18:05:45 while building H9S_Bloom_x10 (Resolve.exe.26188.dmp).
Scripting-host threads died silently ~6 times (Callout, Connector, TextLine, Look x10 ...): two sessions drove the same Resolve at times.
