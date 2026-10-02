# Prompt for Claude Desktop (paste everything below the line)

---

You have access to DaVinci Resolve on this machine. Your job is to run the SMK v2 "Phase 0" validation spikes and report REAL results. Never guess or invent a result: if you could not observe something, write "NOT VERIFIED" and say why.

## 0. Setup
1. Get the code: `git clone https://github.com/vixuals311/smk-v2` (or `git pull` if it exists). Read `docs/PHASE0_CHECKLIST.md` and `docs/ARCHITECTURE.md`.
2. `pip install lupa`, then run `python build/build.py`, `python tests/test_smk_core.py`, `python tests/test_fuse_harness.py`. Report pass/fail counts.
3. Record the environment: Resolve edition (Free/Studio) and version, OS, GPU model, GPU processing mode (Preferences > Memory and GPU: CUDA / Metal / OpenCL / Auto), timeline fps.
4. Copy every file in `dist/spikes/` AND `dist/fuses/SMK2_Motion.fuse` into the Resolve Fuses folder (Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses`; macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses`). Restart Resolve. Open the Fusion Console (Workspace > Console) and keep its output.

## 1. Run each spike (use the Fusion page in a new project; a 5 s clip, 1920x1080, 24 fps)
For every spike, follow the matching row in `docs/PHASE0_CHECKLIST.md` and the comment block at the top of each `spikes/*.fuse` file. Capture: the exact Console output, a screenshot of the viewer where useful, and PASS / FAIL / NOT VERIFIED.
- **S1 GPU:** add "SMK2 Spike S1 GPU". Expect a smooth gradient and `[S1] GPU OK`. Toggle Checker; cells must be square. Change the comp to 1080x1920 and re-check. If a magenta frame or "FAILED" appears, record it. If you can change the GPU mode (CUDA/Metal/OpenCL), repeat for each.
- **S2 Follower:** Text+ with text "HELLO", Follower per-character, delay 2. Modify Size with "SMK2 Spike S2 Follower". Record whether the Console shows different `req.Time` values per character in one frame and whether the letters visibly stagger. Then save the project, close and reopen it: confirm the connection survives and no BezierSpline appeared on that input.
- **S3 ClipTime:** run on the Fusion page; then put a Fusion clip on the Edit timeline, trim it shorter than the comp, and re-check. Cycle the Output modes 0 to 4. Record the printed RenderStart/RenderEnd/Rate and whether they follow the trim.
- **S4 DoD:** Background -> S4 -> Merge. With Shrink on, does the DoD overlay shrink and stay correct? Stack 20 copies and record playback fps with Shrink on vs off.
- **S5 packaging:** make a tiny `.drfx` (zip with `Fuses/<one spike>.fuse` and `Edit/Titles/SMK/test.setting`, any simple Text+ title saved as .setting). Install it by double-click. Report whether the Fuse and the title both appear without a manual Fuse copy.
- **S6 MotionBlur:** compare "SMK2 Spike S6 MotionBlur" (Samples 1, 8, 16, 32) against a Transform node with motion blur moving identically, at 1080p and, if possible, 4K. Record fps/ms per frame and visible quality.
- **SMK2 Motion modifier:** attach it to Transform.Size. Check frame 0 = From, mid-clip = Rest, final frame -> To; trim the clip and confirm Out follows; save/reopen unchanged; try 24/30/60 fps and confirm the same timing in seconds.

## 2. If something fails to load
Copy the exact error from the Console. You may fix obvious API mistakes in the spike Fuse (the Fuses were written without a Resolve install), re-test, and describe every change you made.

## 3. Report
Create `docs/PHASE0_RESULTS.md` in the repo with: the environment block, a table (spike, PASS/FAIL/NOT VERIFIED, evidence, console output), any code fixes, and a one-line recommendation per spike (use the GPU Fuse or the CPU fallback, etc.). Commit it on a branch named `phase0-results` and push it. Also paste the table here in chat. Do not start Phase 1 work.

If a check needs a human (e.g. you cannot see the viewer), list those checks at the end as a short numbered list of exactly what to look at.
