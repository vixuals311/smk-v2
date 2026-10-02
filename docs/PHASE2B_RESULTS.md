# Phase 2b Gate Results: tight output buffers (S7) and realistic card counts

Date: 2026-10-02 · Branch: `phase2b-results` · Built from `main` at `0fdea08`. **No source changes were made** (the Shape Fuse and the spike are untouched).

Anything not observed is marked **NOT VERIFIED** with the reason.

## Environment and method

- Same machine as earlier phases: Resolve **Studio** 21.1.0.14, Windows 11 (build 26100), RTX 4070 SUPER, CUDA.
- Steps run: `git pull`, `python scripts/install.py --include-spikes` (Fuses and spikes in `Fuses/SMK2/`), Resolve restart.
- Unit tests: `test_smk_core` 49/0, `test_fuse_harness` 12/0, `test_animator` 10/0, `test_motion_rig` 9/0, `test_shape` 34/0. `test_shape_kernel` is still SKIPPED (no C compiler).
- Same method as earlier phases: scripting API plus Deliver-page PNG renders, analysed with PIL. Console output: the installed copy of the S7 spike has a harness-only header that tees `print()` to a log (the Fusion Console cannot be read through the API). The repo source is unchanged.
- All timings are Deliver render times (PNG output, 300 frames) and are **not** viewer fps. Viewer fps is NOT VERIFIED everywhere because I have no viewer access.

## Project and comps (open these by hand)

Project **`SMK Phase2b Gate`** (same layout rules as Phase 2: Note on top, sources left, SMK nodes, Merges, MediaOut right, every tool named, positions set with `FlowView.SetPos`, saved with `ProjectManager.SaveProject()`). Your `SMK Test` project was not touched.

| Check | Comp to open | Notes |
|---|---|---|
| T1 | `T1_Methods` | 5 rows `T1_M0..M4_Gen` plus `T1_Mx_Merge` over one grey `T1_Background`. `T1_MediaOut` is currently on Method 0; reconnect it to see each method. |
| T2 | `T1_Methods` and `T5_BoxMove` | Pixel parity was measured from renders of these two comps. |
| T3 | `T1_Methods` | NOT VERIFIED (no viewer). Open it, switch `T1_MediaOut` between methods and use View ▸ Show DoD. |
| T4 | `T4_Speed20` (60 fps) | `T4_M0_Chain_End`, `T4_M3_Chain_End`, `T4_M1_Chain_End` select the chain. |
| T5 | `T5_BoxMove` | Centre 0.25/0.65 static for Methods 0–4, and Centre X keyframed on Methods 0 and 3. |
| T6 | `T6_Transform_Blur` | Rows `M0_Blur`, `M3_Blur`, `M0_Transform`, `M3_Transform`. |
| T7 | `T7_Cards` (60 fps) | 12 cards in one chain. Tap `T7_MediaOut` at `Card03_`, `Card05_`, `Card08_` or `Card12_MergeText`. |

A second project, **`SMK Phase2b Crash Control`** (comps `C1_BlurOnBackground`, `C2_BlurOnS7_M3`, `C3_BlurOnS7_M0`, `C4_BlurMerge`), holds the controls I used to find the cause of a crash (see T6).

## Results

| Check | Comp | Result | Evidence |
|---|---|---|---|
| **T1** all five methods | `T1_Methods` | **Ran without errors; only Method 3 truly honours the placement.** | Dumps below. No error text from any method (0 error/failed lines). All five rendered a PNG. |
| **T2** pixel parity vs Method 0 | `T1_Methods` | **All 4 match at the centred position (max diff 0/255), but that is a coincidence for Methods 1, 2 and 4** (see T5). | With the box centred (CX/CY 0.5): Method 1, 2, 3 and 4 each differ from Method 0 by a maximum of **0** per channel (diff bbox none), and nothing outside the 640×360 box at (640,360)–(1280,720) is painted. |
| **T3** DoD overlay | `T1_Methods` | **NOT VERIFIED** | No viewer access. The console dump shows the DataWindow each method claims (below). |
| **T4** speed | `T4_Speed20` | **FAIL: no speed-up from a tight buffer or DataWindow** | 20 animated copies, 60 fps, 300 frames: Method 0 **140.8 ms/frame**, Method 3 (best working) **145.8 ms/frame**, Method 1 (small buffer) 149.2 ms/frame. Table below. |
| **T5** box move | `T5_BoxMove` | **Method 3 PASS. Methods 1, 2, 4 FAIL.** | See below. |
| **T6** Transform and Blur | `T6_Transform_Blur` | **PASS for Method 3** | See below. |
| **T7** realistic counts | `T7_Cards` | Render **32.5 / 42.5 / 52.5 / 55.8 ms/frame** for 3 / 5 / 8 / 12 cards; viewer fps NOT VERIFIED | Table below. |

### T1: the `[S7]` console dump for each method

One representative dump per method (Resolve prints each twice per frame; the full first 66 lines are in `docs/phase2b_evidence/t1_s7_console_dump.txt`). No error text was printed by any method.

```
Method 0 (full frame control):
[S7] method 0: Width=1920 Height=1080 DW=0,0..1920,1080
[S7]   OriginalWidth = 1920   OriginalHeight = 1080   XOffset = 0   YOffset = 0   Depth = 5

Method 1 (small buffer + IMG_XOffset/IMG_YOffset):
[S7] method 1: Width=640 Height=360 DW=0,0..640,360
[S7]   OriginalWidth = 640   OriginalHeight = 360   XOffset = 0   YOffset = 0   Depth = 5

Method 2 (as 1 + IMG_OriginalWidth/Height):
[S7] method 2: Width=640 Height=360 DW=0,0..640,360
[S7]   OriginalWidth = 640   OriginalHeight = 360   XOffset = 0   YOffset = 0   Depth = 5

Method 3 (full size + IMG_DataWindow):
[S7] method 3: Width=1920 Height=1080 DW=640,360..1280,720
[S7]   OriginalWidth = 1920   OriginalHeight = 1080   XOffset = 0   YOffset = 0   Depth = 5

Method 4 (small buffer, IMG_Like probe):
[S7] method 4: Width=640 Height=360 DW=0,0..640,360
[S7]   OriginalWidth = 640   OriginalHeight = 360   XOffset = 0   YOffset = 0   Depth = 5
```

What each method did, exactly:
- **Method 0:** a normal full 1920×1080 buffer.
- **Method 1:** the constructor is accepted but `IMG_XOffset` and `IMG_YOffset` are **ignored** (they read back 0); the image is a 640×360 buffer whose data window is 0,0..640,360 and whose original size is 640×360.
- **Method 2:** `IMG_OriginalWidth/Height` are **ignored** (they read back 640×360); same as Method 1.
- **Method 3:** `IMG_DataWindow` in the constructor **is honoured** (DataWindow reads back 640,360..1280,720 on a 1920×1080 buffer). The compute kernel iterates the data window (the box lands at the right global pixels).
- **Method 4:** the `IMG_Like` probe plus width/height/offset is accepted, but again offsets and original size are **ignored** (640×360 buffer, offsets 0, original 640×360).

### T5: moving the box (Centre X/Y)

Static Centre (0.25, 0.65): Method 0 draws the box at (160,198)–(800,558).

| Method | Box position | Max diff vs Method 0 | Verdict |
|---|---|---|---|
| 1 | (640,360)–(1280,720): **stays centred, ignores Centre X/Y** | 128 / 192 / 192 | FAIL |
| 2 | same as 1 | 128 / 192 / 192 | FAIL |
| 3 | (160,198)–(800,558) | **0** | PASS |
| 4 | same as 1 | 128 / 192 / 192 | FAIL |

So the small-buffer methods work only when the box happens to be at the canvas centre: Fusion places a smaller image centred in the canvas because the offsets are dropped. Method 3 animated (Centre X keyframed 0.25 → 0.75 over frames 0–24): all 25 frames are **pixel-identical to Method 0** (max diff 0) and there are no stale pixels outside the box.

### T4: speed (60 fps timeline, 1080p, 300 frames to PNG)

| Variant | Total ms | ms/frame | fps equivalent |
|---|---|---|---|
| 20 × Method 0 (full frame), **not animated** | 2 243 | 7.5 | 134 (static graph, cached; not meaningful) |
| 20 × Method 0, Centre X keyframed (a changing output each frame) | 42 248 | **140.8** | 7.1 |
| 20 × **Method 3** (DataWindow), animated | 43 743 | **145.8** | 6.9 |
| 20 × Method 1 (small buffer, but wrong position when moved), animated | 44 763 | 149.2 | 6.7 |

- A tight buffer or a DataWindow **did not make the Merges cheaper**: even a real 640×360 buffer (Method 1) costs the same as the full frame. So the cost in this chain is not the full-frame fill. It is the per-Fuse-node and per-Merge overhead that earlier phases measured (about 3 ms each, plus the Merge).
- The static graph is fast only because Fusion caches an unchanged result; once the output changes each frame the cost is the same for every method.

### T6: Transform and Blur downstream (frame 12)

| Chain | Result |
|---|---|
| Transform (Size 1.4, Angle 20, Centre 0.6/0.45) → Merge, Method 0 vs Method 3 | **pixel-identical** (max diff 0), same bounding box (643,203)–(1661,985) |
| Blur 60 → Merge, Method 0 vs Method 3 | max diff **1 to 2 / 255** (rounding), same bounding box (442,162)–(1478,919). The blurred halo extends well beyond the 640×360 box on both, so **it is not cropped** and there is no offset error. |
| Blur 60 straight from the generator (no Merge), Method 0 vs Method 3 | max diff 1 / 255, same bounding box (442,167)–(1478,913) |

**A crash during T6, and its cause:** my first T6 build crashed Resolve twice (once at render time, once when the project was reopened with that timeline current; crash dumps in the Resolve `logs` folder). The cause was **my own script**, not the Fuse: I had written `blur.Filter = blur.Filter`, which set the Blur node's `Filter` (a `FuID` input) to an empty value (it read back `None` instead of `Fast Gaussian`). Rebuilt Blur nodes with the default filter render fine. The four control comps in `SMK Phase2b Crash Control` (Blur on a Background, on Method 3, on Method 0, and Blur then Merge) all render without a crash. I did not re-trigger the crash on purpose to prove it.

Side effects of that crash, for anyone using the project: to recover, I moved the S7 Fuse out temporarily, clicked through Resolve's "Unknown tool found" dialogs by simulated mouse clicks, and made `T1_Methods` the current timeline; the Fuse IDs survived (checked: all S7 nodes are still `Fuse.SMK2_Spike_S7_TightBuffer` after restoring the Fuse).

### T7: realistic card counts (Phase 2 Shape, 60 fps, 1080p, 300 frames, Text+ label per card)

| Cards | Total ms | ms/frame | fps equivalent (render) |
|---|---|---|---|
| 3 | 9 759 | **32.5** | 30.8 |
| 5 | 12 742 | **42.5** | 23.5 |
| 8 | 15 750 | **52.5** | 19.0 |
| 12 | 16 745 | **55.8** | 17.9 |
| (20, from Phase 2 H13) | 42 246 | 140.8 | 7.1 |

- **24 fps** (41.7 ms/frame): crossed at about 5 cards in render time.
- **60 fps** (16.6 ms/frame): **not met even with 3 cards**.
- Viewer fps for each count (first playback and cached): **NOT VERIFIED**; please measure on `T7_Cards`.
- The time grows by about 10 ms per card up to 8 cards, then flattens (8 to 12 cards adds only 3.3 ms); between 12 and 20 cards it rises steeply again. I do not know why (not investigated).

## Recommendations

| Item | One line |
|---|---|
| S7 methods 1, 2, 4 | Dead end: `IMG_XOffset/YOffset` and `IMG_OriginalWidth/Height` are accepted but ignored, so a small buffer cannot be positioned. |
| S7 method 3 | Works (placement, animation, Transform, Blur) but gives **no speed-up**: a full-size buffer with a DataWindow costs the same as a full frame. |
| T4 | A tight output buffer is not the lever. Even a genuine 640×360 buffer costs the same per Merge, so the cost is Fuse and Merge node overhead, not pixels. To reach higher fps, reduce the number of nodes (for example one Fuse drawing several cards, or draw the text in the same node as the card). |
| T7 | If a target is 24 fps in render, about 5 cards is the limit today; 60 fps is not reachable with this node structure at any count tested. |

## Needs the user

1. **T3:** open `T1_Methods`, connect `T1_MediaOut` to each `T1_Mx_Merge`, and use View ▸ Show DoD to see which methods give a small box (expected: Method 3 small box on a full canvas; Methods 1, 2, 4 a 640×360 image).
2. **T7 (and T4):** measure viewer playback fps (first play and cached) on `T7_Cards` at taps 3 / 5 / 8 / 12, and on `T4_Speed20` for the M0 and M3 chains.
3. Decide whether to continue with tight buffers at all, given T4 (no gain from a real small buffer); the alternative is the "fewer nodes" direction in the recommendations.
