# Phase 13 Gate — H5 fix re-test and Phase 12 leftovers (run by Agent A, **the only session driving Resolve**)

**Do not run a second Claude session against the same Resolve** (the Phase 12 crash H15 happened while two sessions were scripting it). Standard hygiene as before (scripting only, deselect before paste, cold renders, readable graphs,
one comp per check, `SaveProject()`, project `SMK Phase13`, keep "SMK Test" untouched, NOT VERIFIED where not observed). Write `docs/PHASE13_RESULTS.md`, push `phase13-results`, paste the table.

**Fix under test (H5):** on a comp attached to a trimmed timeline clip the host can report `RenderEnd = 0`. `smk.clipSeconds` then returned 0 s, so every Out had already finished and the element was blank. Now an unusable range
(`RenderEnd <= RenderStart`, nil) means "clip length unknown": the Out never starts and the element holds (In still plays). Applied to Shape, Animator, Motion, Motion Rig, Connector, Cursor and to the Text/Stat expressions
(`if T<=0 then T=1e9`). If the host really gives no range, the user sets **Clip Length (s)** on the Fuse/macro to get an Out (the text macros have no such control: they hold). Unit tests execute the new expressions; nothing is verified in Resolve yet.

| # | Check | Pass criteria / report |
|---|---|---|
| Q1 | **Repeat H5 exactly** (your steps: PNG-sequence clip, trim to 80 frames, `InsertFusionCompositionIntoTimeline`, paste StatCard + Shape + a TextLetter + CardStack + Connector + Cursor + ProgressRing, render frames 0/5/10/30/60/79) | Everything renders (non-bg px > 0 where expected). Report `comp.RenderStart/RenderEnd` as read **by a Fuse** (add a one-off debug print in a copy of SMK2_Shape, or read the same in a Text+ expression `comp.RenderEnd` shown as text) |
| Q2 | Same with a **video** clip (any short mp4/mov), trimmed head and tail, and an untrimmed one | As Q1; compare Out timing: does the Out end at the clip end when the range is valid? |
| Q3 | If the range is valid for some clips: confirm clip-relative start (first frame of the trimmed clip = t 0) and the Out ending exactly on the trimmed last frame; if it is unusable: confirm the element holds and that setting **Clip Length** on Shape/Animator gives the Out | Report which case occurs and the exact values read |
| Q4 | **Late start 90000** again, isolated: a Text+-only comp at RenderStart 90000 (does the host itself fail?), then the same with Shape/Animator/TextLetter | Say whether SMK or the host fails; if SMK, give the console/pixel evidence |
| Q5 | **H6 mp4 decode.** `pip install imageio-ffmpeg` (or `opencv-python`) in the Python you use for scripting, decode 3 frames of the H6 mp4 | Frames contain the products; report first/mid/last non-bg px |
| Q6 | Benchmark the variants once: `_Glass/_Neon/_Soft` of UIBlock, CardStack, StatCard, ClickDemo vs base (1080p, cold 60 fps, first/second) | Add to `docs/PERFORMANCE.md`; expect same cost as base |
| Q7 | Relief blockiness (H8): Relief Size 80 / Depth 12 at Quality 0 / 1 / 2 on a Shape ring | Which setting shows blocks/tiling; mean abs diff Quality 0 vs 2 |
| Q8 | Re-run H1 smoke on all 34 after the rebuild (only 4 frames each) | 136/136 as before |

**For the user by hand:** trim a real clip with the mouse on the Edit page and watch an SMK element; viewer fps; look and feel.
