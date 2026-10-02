# Phase 2b Gate — tight output buffers (spike S7) + realistic card counts

**Why:** Phase 2 viewer playback for the 20 Shape + 20 Text+ graph was 6–7 fps (render 140.8 ms/frame); v1 was 6–8 fps. Breakdown:
20 Shapes + Merges 50.8 ms (≈2.5 ms each, full-frame 1080p float32 each), 20 Text+ merges ≈ 90 ms. Text+ is cheap per Merge
because its output covers only the text box; our generators output the full frame, so every Merge pays full-frame fill. If a Fuse can
output a small image (bounding box) positioned in the canvas, Merge cost should drop sharply. S4 failed (`DataWindow` assignment
ignored; `IMG_Like + IMG_DataWindow` still filled the full frame). S7 tries the other allocation styles.

Install with spikes: `python scripts/install.py --include-spikes`, restart Resolve.

| # | Check | Pass criteria / what to report |
|---|---|---|
| T1 | `SMK2 Spike S7 TightBuffer` Methods 0–4, each into a Merge over a grey Background (1920×1080), Console open | For every method: the `[S7]` console dump (Width/Height/DataWindow/attributes), any error text, a PNG render |
| T2 | Pixel parity | A method "works" only if the green→blue box is at **exactly the same pixels** as Method 0 (diff max ≤ 1/255) and nothing else is painted |
| T3 | DoD overlay | View ▸ Show DoD (viewer): is the box small for the working method? (Claude Desktop: NOT VERIFIED if no viewer; user checks) |
| T4 | Speed | For Method 0 and the best working method: 20 copies of the generator (each on its own Merge over one Background), 60 fps timeline, 300 frames, report ms/frame |
| T5 | Box move | Change Centre X/Y (and animate it): the box moves correctly, no clipping or stale pixels outside the box |
| T6 | Same box through a downstream Transform and a Blur | Works on the small-buffer output (no crop of the blurred halo, no offset error) |
| T7 | Realistic counts: use the Phase 2 Shape (full-frame today) for 3, 5, 8 and 12 Shape cards, each with a Text+ label merged over a Background | Render ms/frame **and** user-measured viewer fps (user does the viewer part): where does it cross 24 and 60 fps? |

If every method fails, say exactly what each did (e.g. "XOffset ignored", "constructor error: …"). Do not change the Shape Fuse in this phase.
