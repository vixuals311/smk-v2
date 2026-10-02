# Phase 0 Results

Date: 2026-10-02 · Branch: `phase0-results` · Repo build: `2.0.0-dev` (`python build/build.py`)

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment

| Item | Value |
|---|---|
| Resolve | **Studio** 21.1.0.14 (Free not available, so Free vs Studio is NOT VERIFIED) |
| OS | Windows 11 Pro for Workstations, build 26100 |
| GPU | NVIDIA GeForce RTX 4070 SUPER (11.4 GiB), driver 591.86 |
| GPU mode | **CUDA** (Resolve log: "Compute API set to automatic, defaulting to CUDA"). OpenCL is also detected but I could not switch to it, so OpenCL is NOT VERIFIED. Metal is NOT VERIFIED (Windows only). |
| Timeline | 24 fps, 1920x1080, 5 s (120 frames) Fusion composition. The 1080x1920, 4K, 30 fps and 60 fps variants were also used where noted. |
| Unit tests | `tests/test_smk_core.py`: 39 passed, 0 failed. `tests/test_fuse_harness.py`: 11 passed, 0 failed. Same counts before and after my fixes. |

### How the tests were run

- I had no screen access to Resolve. Everything was driven through the Resolve scripting API and measured on **Deliver-page renders** (PNG, analysed with PIL).
- **The Fusion Console could not be read.** To capture `print()` output, the *installed* copies of the Fuses got a 3-line header that tees `print` to a log file (copied to `docs/phase0_evidence/console.log`). This is harness-only (`scripts/install.sh`). The repo sources are not modified for it.
- The full tee'd output is in [`phase0_evidence/console.log`](phase0_evidence/console.log). It includes the pre-fix failures and my probe output.
- Tools were created with `comp:AddTool("Fuse.<id>")` and `tool:AddModifier(...)`, not by GUI right-click. This covers the same code path, but not the GUI menus.
- Resolve hung twice (a `Saver` render and one stuck S6 render). I force-killed and relaunched it. The existing `SMK Test` project was saved first and not touched. Test work is in new projects `SMK Phase0 Spikes`, `SMK P0 fps30` and `SMK P0 fps60`.
- For S5 I used a simulated mouse click on Resolve's "Install bundle?" dialog (see S5).

## Results

Images and scripts referenced below are in `docs/phase0_evidence/images` and `docs/phase0_evidence/scripts`.

| Spike | Result | Evidence | Console output |
|---|---|---|---|
| **S1** GPU | **PASS** (CUDA, Studio), after a fix | `s1_gradient_1920x1080.png`: corners R=x, G=y, B=0.5 (e.g. (1,253,128), (254,2,128)). `s1_checker_1920x1080.png` and `s1_checker_1080x1920.png`: 32 px cells, with horizontal and vertical runs all 32 px, so no stretching in 16:9 or 9:16. | After fix: `[S1] GPU OK 1920x1080 t=0` and `[S1] GPU OK 1080x1920 t=0`. **Before the fix**, the first request per render printed `[S1] GPU FAILED -> CPU fallback: ...fuse:50: attempt to index local 'node' (a nil value) [t=5 precalc=true ...]`. `DVIPComputeNode()` returns nil on PreCalc requests, and `REG_NoPreCalcProcess = true` does not prevent them. |
| **S2** Text follower | **PASS** | Text+ "HELLO", Follower Delay 2, modifier on Follower `Size`. `s2_follower_frame6.png` at frame 6: H largest, E smaller, L smaller still, then nothing, which is a clear stagger. After save, close and reopen: `Size` is still connected to `Fuse.SMK2_Spike_S2_FollowerMod`, there is no `BezierSpline` in the comp, and a re-render is **pixel-identical** (PIL diff bbox = None). | One render pass printed `req.Time=0.000, -2.000, -4.000, -6.000, -8.000` (distinct per character, step = Delay 2). Frame 6 printed `6, 4, 2, 0, -2`. |
| **S3** Clip timing | **PASS** after a fix (`self.Comp:GetAttrs()` is invalid in a Fuse). Live drag-trim in the UI is NOT VERIFIED. | See the S3 detail below. | Original code threw `SMK2_Spike_S3_ClipTime.fuse:27: attempt to call method 'GetAttrs' (a nil value)`. Fixed: `[S3] t=60 RenderStart=0 RenderEnd=119 GlobalStart=0 GlobalEnd=119 Rate=24 mode=3 out=119` |
| **S4** DoD | **FAIL as written.** The overlay and fps comparison are NOT VERIFIED. | `s4_original_shrink_on_fullframe.png`: with Shrink on, a 30%x20% box should show orange inside blue. The whole frame was orange. | `[S4] DoD -> 0,0..1920,1080`. The assignment `out.DataWindow = ImgRectI(...)` is silently ignored (read-back is the full frame). See the S4 detail below. |
| **S5** `.drfx` | **PARTIAL.** The Title appears. The Fuse does **not** load from the bundle. | Built `Fuses/SMK2_Drfx_Probe.fuse` + `Edit/Titles/SMK/test.setting` (`images/SMK2_S5_test.drfx`). After install, `InsertFusionTitleIntoTimeline("test")` returned a Template TextPlus containing "SMK drfx test". `AddTool("Fuse.SMK2_Drfx_Probe")` returned None, also after a full restart. The Fuse was not copied into `Fuses/`. | The dialog `Install "SMK2_S5_test"? This will add the selected template bundle to the Effects Library.` appeared (`images/dialog.png`). The file landed in `Support\Fusion\Templates\SMK2_S5_test.drfx`. |
| **S6** Motion blur | **PARTIAL.** The GPU path works after a fix and is smoother than Transform, but it is not faster. | See the S6 detail below. | Before fix: `[S6] GPU FAILED: ...fuse:55: attempt to index local 'node' (a nil value)` (PreCalc, same as S1). After: `[S6] GPU OK t=0 n=8` |
| **`SMK2 Motion`** | **PASS** after a fix (`GetAttrs` error, same as S3). Frame 0, mid-clip, trim, reopen and 24/30/60 fps are all OK. The last frame is close to To but not exactly To. | See the Motion detail below. | n/a (no prints) |

### S3 detail

| Case | RenderStart / RenderEnd | GlobalStart / End | Rate | Mode outputs |
|---|---|---|---|---|
| Fusion page, 120-frame comp | 0 / 119 | 0 / 119 | 24 | mode 0: 0 at t=0, 4.9583 at t=119. 1 = 5, 2 = 0, 3 = 119, 4 = 24. |
| Edit page, Fusion clip trimmed to 47 frames (source 120) | 0 / **46** | -24 / 95 | 24 | 1 = 1.9583, 2 = 0, 3 = 46, 4 = 24 |
| Edit page, clip re-added trimmed to 29 frames | 0 / **28** | 0 / 119 | 24 | 1 = 1.2083 |
| Same clip after a Title insert split it | **5** / 28 | 0 / 119 | 24 | n/a |
| Edit page Title, 1 frame long | 0 / 0 | 0 / 1 | 24 | 0 |

- Fix: in a Fuse, `self.Comp` is an ffi `FusionDoc*`. It has **fields** `RenderStart`, `RenderEnd`, `GlobalStart` and `GlobalEnd`. It has no `:GetAttrs()` and no `COMPN_` names. `:GetPrefs("Comp.FrameFormat.Rate")` works.
- Values follow the clip's actual in/out when the clip is re-trimmed or split through the API.
- **Not tested:** dragging a trim handle in the Edit UI on an already-open comp (no UI control).

### S4 detail

- `ImgRectI` takes `(left, bottom, right, top)`.
- Variants tried:
  - `out.DataWindow = rect` (on a Copy, or on `IMG_Like`) is a **no-op**.
  - `Image({IMG_Like=img, IMG_DataWindow=rect})` **does** set the data window, so `out.DataWindow` reads back 576,432..1344,648. But `out:Fill(green)` still painted the **whole frame** in the downstream Merge.
  - `Crop(out, {...})`, `ChannelOpOf("Copy", ...)` and `CopyOf` gave a **blank** (transparent) foreground, so I could not copy pixels into a data-window-limited image.
- So I could not get a correct "image unchanged inside, small DoD" output.
- fps with 20 stacked copies, Shrink on vs off: **NOT VERIFIED**. The original Shrink was a no-op, so on and off would be identical.
- The DoD overlay itself (View > Show DoD) was not looked at, because I had no viewer access.

### S5 detail

- Layout that worked for the Title: `Edit/Titles/SMK/test.setting` at the archive root (no `Templates/` prefix).
- `Fuses/` inside the `.drfx` is ignored by Resolve 21.1 on Windows. Confirms the checklist's expectation that a separate Fuse install step is needed.
- Windows only. macOS is NOT VERIFIED.
- Installation was a **simulated mouse click** on Resolve's "Install" dialog.
- I removed the test `.drfx` from `Support\Fusion\Templates` afterwards. The `SMK` test title may still show in the Effects Library until Resolve restarts.

### S6 detail

Render of 120 frames to PNG; "fps" is derived from that render time. Source is the S1 checker. Motion is 300 px amplitude, `sin(t/12)`. The shutter is 0.5 frame for S6 and 180° for Transform. Transform has motion blur on, Quality 2, with the same expression for position.

| Case | 1080p ms | 4K ms |
|---|---|---|
| No blur baseline (S1 only) | 1742 | 3242 |
| S6 Samples 1 / 8 / 16 / 32 | 2254 / 2234 / 2259 / 2244 | 3239 / 3253 / 3233 / 3252 |
| Transform, motion blur on | 2240 | 3240 (no blur: 3258) |
| **8 chained** at 4K: S6 N=8 / N=32 | n/a | **7227 / 7234** (about 16.6 fps) |
| **8 chained** at 4K: Transform blur | n/a | **3735** (about 32 fps) |

- Single-node numbers are limited by PNG output (about 53 fps at 1080p, 37 fps at 4K). They do **not** discriminate between S6 and Transform.
- In an 8-node chain, S6 costs about **4 ms/frame/node more than Transform** at 4K, whatever the sample count. N=8 and N=32 were identical, so the cost is Fuse per-node overhead (probably GPU transfers) and not the kernel.
- Quality at frame 0, where velocity is about 25 px/frame (transition width along the centre row of the checker):
  - S6 N=1: 1 px (no blur).
  - S6 N=8, 16 and 32: a continuous 15 px ramp (expected about 12.5 px).
  - Transform at Quality 2: 2 px steps with many more edge transitions (299 vs 59). That is discrete ghost copies, not a smooth ramp.
- Result: **smoother** than Transform at Quality 2 for N>=8, but **slower** in a chain, so it fails the "fewer ms/frame" half of the criterion.
- Not measured: interactive playback fps in the viewer, and Transform at higher Quality settings.

### `SMK2 Motion` detail

Tested with From 0.5, Rest 1.5, To 0.5, measured as checker cell size (32 px x Size), through Deliver renders. Defaults: In 0.5 s, Out 0.5 s.

| Check | Result |
|---|---|
| Frame 0 | cell 16 px, Size 0.5, equals From |
| Mid-clip | cell 48 px, Size 1.5, equals Rest |
| In phase, 0.25 s | Size 1.53, overshoot above Rest |
| Last frame | cell 16 px, Size 0.5, to within measurement. In a 0..1 test the last frame was 0.0039, not exactly To, because the last frame is at 4.958 s and the clip is 5.0 s. |
| Trim | on a 47-frame Edit clip with From .25, Rest .75, To .25: mid / first = 3.0 (correct), last = first (back at To), frame 40 is mid-Out. **Out follows the trim.** |
| Save / reopen | Project closed and reopened after a Resolve restart. The modifier is still connected with the same parameters, and renders give the same values (frame 4: 1.312). |
| 24 / 30 / 60 fps | At t = 0 s, 1/6 s, mid, 4.667 s and the last frame: Size 0.5, **1.312**, 1.5, **0.938**, 0.5 at all three rates. Same timing in seconds. |

- The pre-fix Motion code was not run. It contains the same `self.Comp:GetAttrs()` call that failed in S3, so I applied the same fix and tested only the fixed version.

## Code changes

All changes are small; the unit tests still pass (39/0 and 11/0).

| File | Change |
|---|---|
| `spikes/SMK2_Spike_S1_GPU.fuse` | Added `if req:IsPreCalc() then OutImage:Set(req, out) return end`. Print the `pcall` error and request flags on failure. Print `t=` on success. |
| `spikes/SMK2_Spike_S6_MotionBlur.fuse` | Same PreCalc early return. Print the `pcall` error. Print `[S6] GPU OK t=.. n=..`. |
| `spikes/SMK2_Spike_S3_ClipTime.fuse` | `self.Comp:GetAttrs()` / `COMPN_*` replaced by fields `self.Comp.RenderStart/RenderEnd/GlobalStart/GlobalEnd`. Print includes mode and result. |
| `src/fuses/SMK2_Motion.lua` | Same `GetAttrs` replacement (`c.RenderStart`, `c.RenderEnd`). |
| `tests/test_fuse_harness.py` | Mock `self.Comp` now mirrors Resolve (plain fields instead of `GetAttrs`). |
| `spikes/SMK2_Spike_S2`, `S4` | **Unchanged.** S2 works as-is. S4 does not work and I found no working API in the time spent. |

## Recommendations

| Spike | One line |
|---|---|
| S1 | Go: DVIP GPU Fuses work on CUDA/Studio. Always early-return on `req:IsPreCalc()` before `DVIPComputeNode`. Still check OpenCL, Free edition and Metal. |
| S2 | Go: a Fuse modifier on a Follower input is evaluated per character and survives save/reopen with no splines. Check Opacity and the GUI Modify-With path. |
| S3 | Go: read `self.Comp.RenderStart/RenderEnd/GlobalStart/GlobalEnd` as fields. The fallback of Start/End as inputs is not needed. Confirm live trimming in the UI. |
| S4 | No-go for now: keep full-frame output and rely on fewer nodes. Revisit only if someone finds the right Fuse DoD API. |
| S5 | Use the installer-script fallback: the `.drfx` delivers Titles but not Fuses. Ship Fuses with a copy step. |
| S6 | Do not switch to the in-kernel blur for speed. Use native Transform blur by default. Use S6 only where smoothness matters, with N=8. |
| `SMK2 Motion` | Go: timing, trim, reopen and fps independence all verified after the `GetAttrs` fix. |

## Needs the user

1. S1 on **OpenCL**, **Free** edition and **macOS/Metal**. I could not switch Resolve's compute API.
2. S2 through the actual GUI path: right-click `Size` or `Opacity` > Modify With. I attached by script, and tested `Size` only.
3. S3: drag-trim an already-open Edit clip and watch the values update live. Also the Title case on a normal-length title.
4. S4: open View > Show DoD, and confirm no overlay shrink. Also check the 20-node fps once a working DoD API exists.
5. S5 on macOS, and a fresh-user double-click.
6. S6 interactive playback fps in the viewer (1080p/4K), and eyeball the edges. Compare against Transform at higher Quality.
