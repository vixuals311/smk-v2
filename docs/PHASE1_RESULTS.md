# Phase 1 Gate Results

Date: 2026-10-02 · Branch: `phase1-results` · Built from `main` at `c479121` (`feat(phase1): SMK2_Animator …`) plus the one fix below.

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as Phase 0: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python scripts/install.py` (Fuses landed in `Fuses/SMK2/`), then a Resolve restart. First I deleted my Phase 0 `SMK2_*.fuse` copies from the Fuses root so the IDs could not clash.
- Unit tests: `test_smk_core` 48/0, `test_fuse_harness` 11/0, `test_animator` 10/0, all passing, also after the fix.
- Method is the same as Phase 0: scripting API plus Deliver-page PNG renders, analysed with PIL. I could not see the viewer or the Fusion Console, so nothing here was judged by eye.
- The installed copies of the Fuses had a harness-only header that tees `print()` to a log file. After the tests I reinstalled the clean builds with `install.py`.
- Test projects: `SMK Phase1 Gate`, `SMK P1 fps30` and `SMK P1 fps60` (all new). Your `SMK Test` project was not touched.
- Tools were added by script (`AddTool("Fuse.SMK2_Animator")`), not through the GUI menus.

## One bug fixed (blocked everything)

The first render with `SMK2 Animator` failed:
`SMK2_Animator.fuse:… attempt to index field 'Image' (a nil value)`, and every Deliver render ended "Fusion composition could not be processed".

- **Cause:** the input table was a file-level `local I = {}`. Resolve runs `Process` in a re-executed copy of the chunk where `Create()` has not run. A probe showed `Create end I keys=45` but `Process I keys=0`, a different table.
- **Fix** in `src/fuses/SMK2_Animator.lua`: `I` is now a global assigned at the top of `Create()`, the same pattern `SMK2_Motion` already used. Four lines changed. Unit tests still 48/11/10 passing.

## Results

| Gate | Result | Evidence (measured on renders) |
|---|---|---|
| **G1** defaults | **PASS** (after the fix) | Text+ "SMK" at 24 fps, 120 frames. Frame 0 is invisible. Frame 3: centre x 889.5 px, max luma 157 (coming in from the left, partly faded). Frame 6: 967.5, 255. Frame 12: 964.5 (settled). Frames 60 and 108 are identical (hold, centre 963). Frame 114: centre 1117, luma 50 (sliding right and fading). Frame 119: invisible. Console: no errors. See `images/g1_in_f3.png`, `g1_out_f114.png`. |
| **G2** engines | **PASS** (visual taste NOT VERIFIED) | Centre x over frames 1–15 for each In engine. They are distinct: Ease 784→963 monotone. **Spring** 794, 842, 890, 928, 954, 968, 974, 974, 972 … 962 (overshoots to 974, settles after the 12-frame In Duration). Bounce dips (918 at frames 6–7) then settles. **Elastic** swings past rest to 1020, then 946 and settles. Overshoot peaks at 982. Inertia 826→963 monotone and slow. All six end at 963 with no jump at the end. I judged "looks distinct" from numbers only, not by eye. |
| **G3** fade/slide/scale/rotation | **PASS** | Baseline text bbox 286×101 px at 1920×1080. **Fade** 0.5 gives max luma 128. **Slide** angle 180, 0.1 gives a 192 px left shift (0.1×1920). Angle 90 gives a 192 px upward shift, so the distance is a fraction of frame *width* for both axes. **Scale** 0.5 gives 143×51. **Rotation** 90 gives 101×286 (width and height swapped, no shear). At **1080×1920**: slide 0.1 gives 108 px (0.1×1080), rotation 90 turns 161×57 into 57×161, scale 0.5 gives 81×29. Rotation direction (CW or CCW) not checked. |
| **G4** pivot | **PASS** | Scale 0.5 about pivot (0,0): centre (481.5, 809.5), predicted (481.5, 810). About (1,1): (1441.5, 269.5), as predicted. Scale 0 gives an empty frame, no error. Rotation 20° about (0,0): centre (723.5, 241), predicted (720, 243). About (1,1): (1209.5, 833), predicted (1205.6, 835). Rotation 90 about the corner pivots throws the card off-screen (the maths says so), so I checked 90 about the centre and 20 about the corners instead. |
| **G5** trim on Edit page | **PASS** (live drag-trim NOT VERIFIED) | Media clip on the Edit page, Fusion comp, trimmed to 46 frames (RenderEnd 45): Out starts at frame 35 (left edge 14 px, luma falling) and the card is gone by frame 43. A 29-frame clip: Out starts at frame 18. The Out phase sits at (clip end − 0.5 s) for each trim, not at frame 108. I could not drag a trim handle on an open comp, only re-add the clip with a new range, so "no re-open" while dragging is NOT VERIFIED. |
| **G6** Index and Stagger | **PASS** | Stagger 0.1: first visible frame for Index 0..5 is 1, 3, 5, 8, 10, 13, a step of about 2.4 frames (0.1 s at 24 fps). With Stagger 0.2 and Index 3 it is 15 (offset 14 vs 7, doubled). The values were changed by script on a live comp with no reload. |
| **G7** 24/30/60 fps | **PASS** | Same comp built in separate projects at 24, 30 and 60 fps, sampled at the same seconds (frames 4/8/12/112/116 at 24, ×1.25 at 30, ×2.5 at 60). Text bbox centre and max luma are identical at all three rates: 928.5/209, 973.5/255, 964.5/255, 1073.5/108, 1140.5/19. |
| **G8** save, close, reopen | **PASS** | Saved and closed the project, then reopened it. The Animator is still connected to Text+, there is no BezierSpline in the comp, and no animated or connected input other than `Image`. A re-render of frame 6 is **pixel-identical** to the pre-save render (diff bbox = None). Done within one Resolve session (not an app restart). |
| **G9** two Animators, one renamed | **PASS** | A1 (slide left 0.1) and `CardB` (renamed, slide right 0.3, Ease, scale 0.5) in one comp. A1 shifted −192 px, `CardB` +576 px at 143 px wide. No cross-talk. |
| **G10** benchmark, 20 Animators | **FAIL** against the 60 fps target (playback fps NOT VERIFIED) | 1080p, **60 fps** timeline, 300 frames to PNG, 20 Text+ cards merged over a 1080p Background (Index 0..19, Stagger 0.05). **20 Animators: 20 234 ms, 67 ms/frame, 14.8 fps.** Same graph with the Animators removed: 2 254 ms, 7.5 ms/frame (133 fps). 20 native Transforms (animated by expression): 8 259 ms, 27.5 ms/frame (36 fps). So each Animator costs about 3 ms/frame, about 2.5× a native Transform. Interactive viewer playback fps was not measured (no viewer access), and **20 v1 UIBlocks: NOT VERIFIED (v1 not installed here)**. |
| **G11** transparent edges | **PASS** | Text+ with softness, Animator at 50% opacity over a mid-gray Background, compared with a native Merge at Blend 0.5. Maximum difference 1 level out of 255 per channel. No pixel is darker than the background, so there is no dark fringe. The edge has 19 intermediate levels, so the edges really are soft. See `images/g11_*.png`. |

## Recommendations

| Gate | One line |
|---|---|
| G1–G9, G11 | Go. The behaviour matches the gate. |
| G10 | Not met on render throughput (14.8 fps vs a 60 fps target). Each Fuse node costs about 3 ms/frame on its own, the same per-node overhead seen for S6 in Phase 0. Fixing it needs a different design (fewer Fuse nodes, e.g. one multi-card pass), not an API fix. Measure interactive playback before deciding. |
| G2 | Go on the numbers. Someone should look at Elastic: it swings to the right of rest almost immediately. |

## Needs the user

1. G10: watch real **viewer playback fps** at 60 fps 1080p with the 20-card graph (render time is only a proxy, and cached playback may behave differently). Compare with 20 v1 UIBlocks, which I do not have.
2. G5: drag a trim handle on an open Edit-page clip and watch the Out phase follow without reopening.
3. G2: eyeball the six In engines (in particular Elastic and Bounce) for how they feel.
4. G3: confirm the rotation direction you want (clockwise vs counter-clockwise).
5. G8: do the save, close and reopen with a full Resolve restart in between.
6. G1/G9: try the same thing through the GUI (add the Fuse from the Effects Library, rename in the Nodes view).
