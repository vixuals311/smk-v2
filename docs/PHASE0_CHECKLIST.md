# Phase 0 — Resolve Validation Checklist (one page)

Install: copy `dist/spikes/*.fuse` to the Resolve `Fuses` folder (Win: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses`,
macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses`), restart Resolve, open the Console (Workspace > Console).
**Everything here is written without a Resolve install — API calls are unverified. Report the exact console error for any spike that fails to load.**

**Your setup (fill in):** Resolve ☐ Free ☐ Studio · version ____ · OS ☐ Win ☐ macOS · GPU ____ · API ☐ CUDA ☐ Metal ☐ OpenCL

| # | Test | Pass | Fail → fallback |
|---|---|---|---|
| S1 | Add `SMK2 Spike S1 GPU` to a comp. Gradient shows, console `[S1] GPU OK`. Toggle Checker: cells are square on 16:9 and 9:16. Repeat on each GPU API / Free vs Studio you own | ☐ | ☐ magenta/`FAILED` → CPU path in same Fuse |
| S2 | Text+ → Follower (Per Character, Delay 2) → right-click Size or Opacity → Modify With → `SMK2 Spike S2 Follower`. Distinct `req.Time` per character in console; staggered ramp; Save → reopen: still connected, no BezierSpline on that input | ☐ | ☐ script-written splines |
| S3 | `SMK2 Spike S3 ClipTime` on Fusion page, then on an Edit-page Fusion clip trimmed shorter than the comp, and on a Title. Cycle Output mode 0–4. Values match the visible clip; update after trimming | ☐ | ☐ Start/End as inputs |
| S4 | `SMK2 Spike S4 DoD` between a Background and Merge, Shrink on. DoD overlay shrinks, image unchanged. 20 stacked copies: fps on vs off | ☐ fps ____ vs ____ | ☐ keep full frame |
| S5 (*) | Make a `.drfx` (zip with `Fuses/` + `Templates/Edit/Titles/SMK/` containing any one title .setting). Install by double-click. Do the Fuse and the Title both appear without a manual Fuse copy? Test on both OSes | ☐ | ☐ installer script copies Fuses |
| S6 | `SMK2 Spike S6 MotionBlur` vs Transform (motion blur on, same shutter). 1080p + 4K, Samples 1/8/16/32: fps and edge quality | ☐ fps ____ vs ____ | ☐ native Transform blur |

Also verify the **modifier** `SMK2 Motion` (built to `dist/fuses`): attach to Transform Size; check frame 0 = From, mid-clip = Rest, last frame → To; trim the clip and confirm Out follows; Save → reopen unchanged; same look at 24/30/60 fps.

Record results in `docs/PHASE0_RESULTS.md` (date, build, pass/fail per spike, console output of failures).

(*) **S5 prior evidence (from the NeoEdit bundle):** its `.drfx` packs contain only `Edit/{Effects,Generators,Transitions}/<vendor>/…` `.setting` + `.png`
files; its six Fuses ship in a separate `Fuses/` folder for manual install. Expect S5 = "needs a separate Fuse install step", so the
installer-script fallback is the working assumption; the test just confirms it on your build.

(**) **S3 prior evidence:** the bundle's macros read `comp.RenderStart`, `comp.RenderEnd` and `comp:GetPrefs("Comp.FrameFormat.Rate")` inside
*expressions* on the Edit page, so the values exist there. Whether `self.Comp:GetAttrs()` inside a Fuse `Process` returns them is what S3 tests;
if not, the fallback is the same expressions feeding Start/End/Rate inputs on the node.
