# SMK v2 Architecture (from the Master Plan, 2026-09-29)

Four layers, five core nodes. Only core nodes render or animate; products are presets.

| Layer | Contents | Status |
|---|---|---|
| Library | `src/core/smk_core.lua` — seconds/clip-relative timing, easing + real-time spring, stagger, integer hash. Inlined at build. | **Done (39 tests)** |
| Core nodes | Animator (GPU), Shape (SDF), Text, Look, Motion (modifier) | Motion + Animator built (Phase 1 gate pending); Shape/Text/Look not started |
| Products | UI Block, Callout, Connector, Progress, Counter, Focus Zoom, Cursor, ... as `.drfx` presets | Not started |
| Workflow | SMK Studio Lite | Not started (frozen until Phases 1-3 pass) |

## Timing model
`t` = seconds from clip start (`(frame - RenderStart)/rate`), `T` = clip length, `d = Index × Stagger`.
In starts at `InDelay + d`; Out starts at `T − OutOffset − OutDur`; Hold is the settled state in between.
Each phase has its own engine; only the active one is evaluated. Springs use real time and may settle past the phase end
(no end-of-duration jump). If Out begins before an In spring has settled, Out wins (value steps from the in-flight value).

## Rules carried from v1
No global-name scripts; opacity only via `Merge.Blend` or the Animator (never `Transform.Blend`); forward-only DAG;
one undo per Studio action; no runtime `require()`; unkeyed persistence (never index-assign StartFrame-style inputs).
New IDs are `SMK2_*`; no v1 migration in 2.0.

## Clean-room
Ideas only from NeoEditFX; no code or node graphs copied. The bundle was obtained from a redistribution site.

## Compatibility notes
Fusion embeds LuaJIT (Lua 5.1): core uses no bitwise operators / `goto` / integer division. Tests run it on Lua 5.5 via lupa,
so 5.1-only breakage is guarded by a grep in review, not by the runtime.

## Phase 0 findings that shape the code (2026-10, Resolve Studio 21.1, CUDA)
- GPU Fuses must return early on `req:IsPreCalc()` (`DVIPComputeNode` is nil there).
- Inside a Fuse, `self.Comp` is a plain-field object: use `self.Comp.RenderStart/RenderEnd`, not `:GetAttrs()`.
- Follower→Fuse modifier staggering works (S2). DoD cannot be shrunk by assigning `DataWindow` (S4): output full-frame.
- Fuses are not loaded from a `.drfx` (S5): separate installer. Native Transform blur beats the in-kernel blur in chains (S6).

## Phase 1 findings (G1–G9, G11 pass; G10 fails) → design change
20 text cards at 1080p/60 fps: baseline 7.5 ms/frame; +20 native Transforms 27.5 ms; +20 SMK2 Animators 67 ms (≈3 ms per Fuse node).
Conclusion: the budget is spent per node, so stacked-card products must **not add a node per element**. Products drive the
Merge the element already has through one `SMK2 Motion Rig` modifier (Phase 1b gate). `SMK2 Animator` remains for single
elements and for effects that need image resampling. File-level locals in a Fuse are not visible in `Process` (Resolve re-executes
the file); share state through globals filled in `Create()`.

## Decision after Phase 1b (2026-10-02)
Fuse *modifiers* cost ~3 ms/instance/frame just like Fuse nodes (null modifier x20 = 67.5 ms; native expressions 22.5 ms; baseline 7.5 ms),
so the Rig is not faster than the Animator. User-measured viewer playback (60 fps timeline, 20 cards): 23–26 fps first pass,
58 fps once cached — this, not Deliver render time, is what artists see, so the gate is re-scoped to
"first-pass ≥ 24 fps and cached ≥ 58 fps; render ms/frame tracked as the regression metric".
Rule going forward: **one Fuse instance per element, never more.** `SMK2 Shape` therefore carries its own motion; Animator/Rig remain
for animating existing images. If a stack needs more speed, Studio Lite can bake native expressions from the same core math.
Rotation convention confirmed: positive = counter-clockwise.

## Phase 2 results (2026-10-02)
Shape H1–H11 pass; colour pickers fine; ring sweep clockwise from 12 o'clock; live Edit-page trim moves Out (verified by user).
Benchmark (render ms/frame, 20 cards, 1080p): Shape+Merges 50.8; Shape+Text+ 140.8; v1 UIBlock+Text+ ≈ 2,526. Viewer fps (user): Shape+Text+ 6–7,
v1 6–8. Time is dominated by full-frame Merges (every generator output is 1080p float32) and by Text+ merges (≈4.5 ms each).
Next lever: tight output buffers (S7). If unavailable: multi-element Shape (one Fuse draws N elements) for repeated groups.

## Phase 2b results (2026-10-02) — tight buffers are not the lever
Only `Image({IMG_DataWindow=...})` places a small image correctly (XOffset/YOffset/OriginalWidth ignored), and it gives **no speed-up**
(20 cards: full-frame 140.8, DataWindow 145.8, small buffer 149.2 ms/frame). Cost is per-node overhead, not pixels. Realistic counts (render ms/frame):
3 cards 32.5, 5 → 42.5, 8 → 52.5, 12 → 55.8; user viewer: 12 cards 24 fps, 20 cards 13–16 fps first play, 58 fps cached.
**Decision: stop chasing frame-time with buffer tricks.** Keep one Fuse per element and ≤2 Fuses per product. S4/S7 closed (D2-003 resolved as "not a lever").
Next: products as generated presets (`build/make_macros.py`), then Look, Text and Studio Lite.
