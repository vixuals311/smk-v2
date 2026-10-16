# Deferred work register (v2)

| ID | Item | Why deferred | Status |
|---|---|---|---|
| D2-001 | Share Inspector helpers (phase controls, engine cfg) between Animator, Rig and Shape via a build-time module | Three copies exist; refactor deferred until Resolve-verified | OPEN |
| D2-002 | In-kernel motion blur | Phase 0 S6: native Transform blur is faster/cleaner in chains | DEFERRED (use native Transform) |
| D2-003 | DoD shrink | Phase 0 S4: `DataWindow` assignment ignored | DEFERRED |
| D2-004 | Merge Pivot via script/Rig | Phase 1b R5: Merge has no scriptable Pivot input | OPEN |
| D2-005 | Shape: arrow (line end dot done in Phase 6), glass/backdrop blur, inverted (spotlight) mode, gradient stops > 2 | Not in first slice | OPEN |
| D2-006 | SMK Look (glow, outline, shine) | Built in Phase 7; long shadow moved to D7-002 | RESOLVED (Phase 7) |
| D2-007 | CPU fallback for GPU failure in Shape | Shape outputs transparent on GPU failure (oracle is too slow for full frames) | OPEN |
| D2-008 | Viewer-fps measurement automation | Needs viewer access; user measures manually | OPEN |
| D2-009 | Elastic engine: confirm feel across amplitude/period | User: feels smooth (Phase 1) | RESOLVED (Phase 1) |
| D2-010 | Tight (bounding-box) output buffer for Shape/Look/Animator | Spike S7: no speed-up (Phase 2b) | RESOLVED: not a lever |
| D2-012 | Font Style combo shows "--" in the published macro; label text does not rotate (fixed in 2d) | Phase 2c | OPEN (Style) |
| D3-001 | Counter variants: currency, K/M, decimals, prefix/suffix (Text modifier or Text+ expression formats) | After Phase 3 ring/bar | OPEN |
| D4-001 | SMK Text: per-phase effects (different In and Out look), exact per-unit count for Word/Line Out (character count used; auto count for letters done in 4b), per-word stagger for the Word variant, text presets (defaults only), Cursor/typewriter reveal | After Phase 4 gate | OPEN |
| D5-001 | Cursor: trail, hover/highlight states, scroll, text-select drag, hand/I-beam cursor shapes, per-waypoint easing | Beyond first cursor slice | OPEN |
| D6-001 | Callout (parked by user): reorder the sequence to dot first, then line, then card; auto line start from the card edge (magnetic); then re-gate | User request | PARKED |
| D7-001 | Connector: auto-routing around obstacles, orthogonal routing with multiple bends, label on path, branching/multi-target, rope-physics sag | Beyond first Connector slice | OPEN |
| D7-002 | Look: long shadow (log-step), inner glow/shadow (bevel done: SMK2_Relief), pyramid glow (multi-pass; needs a multi-pass DVIP spike), bilinear-accurate test oracle | Beyond first Look slice | OPEN |
| D2-011 | Multi-element Shape (one Fuse, N elements: bars, grids, lists) | Fallback if S7 fails; also suits charts | OPEN |
| D8-001 | Build pyramid glow / bloom / long shadow / big-radius blur on multi-pass GPU | S12 PASSED (Phase 8): chained DVIP sessions and W/4 intermediates work, cost ~ single pass | DONE: Bloom passed (Phase 9); Long Shadow built (Phase 10 gate) |
| D8-002 | Page Curl: 3D-correct curl on arbitrary corner pivot, curl from a corner (diagonal peel with the cone), stagger by Index for several pages | First slice is a straight roll | OPEN |
| D8-003 | Reflection: ripple from a noise map, per-pixel fresnel fade, vertical-axis (side) mirror | Beyond first slice | OPEN |
| D8-004 | Relief: use a second input as a height map; inner/outer bevel modes | Beyond first slice | OPEN |
| D8-005 | Neo-style effects not yet studied: only Paper Curl, Reflection, Bevel, Emboss, Glow were supplied | Waiting for more samples | OPEN |
| D8-006 | Reflection blur stepped streaks: per-pixel spiral rotation + adaptive taps | Phase 8 F3 | FIXED, in Phase 10 gate |
| D8-007 | Look outline serration: directions scale with width (24-72) | Phase 8 L3 | FIXED, in Phase 10 gate |
| D8-008 | Clearer Reflection/Relief labels | Phase 8 notes | DONE (I1) |
| D10-001 | Look outline cost at 4K (70 ms at 20 px): capped rings 6 x directions 56; re-measure; consider a distance-field outline via multi-pass | Phase 10 O2 | IN REVIEW |
| D11-001 | Stat card: a very long value (10 digits) overflows the card; add auto-shrink or a width cap | Phase 11 T5 | OPEN |
| D11-002 | Click Demo: the button does not react to the click (press/flash); viewer crosshair for the macro-level cursor start unverified | Phase 11 D3 | OPEN |
| D11-003 | Elastic count engine overshoots a stat counter by 37 %: consider a clamp option | Phase 11 T3 | OPEN |
| D12-001 | H5: SMK elements blank on a comp of a trimmed timeline clip (RenderEnd reads 0) | Phase 12 | RESOLVED: was an invalid test trim (frames numbered 86400+); defensive fix kept |
| D12-002 | Macro cost: every macro > 5 ms/frame at 1080p (CardStack 23.5 ms warm, 89 ms cold; Callout/ClickDemo/CardStack +47..70 ms at 4K). Ideas: merge Shape+Label into one Fuse draw, share the Animator, cut Text+ re-render | Phase 12 H9 | OPEN (M4b optimisation) |
| D12-003 | Motion modifier +8 ms: forces Text+ re-render each frame | Phase 12 H9 | OPEN |
| D12-004 | Relief blocky / faint tiling at extreme depth+size | Phase 12 H8 | FIX BUILT (spiral jitter), Phase 14 E9 |
| D12-005 | Resolve crash during two-session scripting (H15); not reproduced alone | Phase 12 H15 | WATCH: run one session only |
| D14-001 | Studio Lite (macros baked to native tools, no Fuses): frozen; needs an owner decision on whether 1.0 needs it | ARCHITECTURE | DECISION NEEDED |
| D15-001 | Connector line starts at the block centre and crosses the block's label unless the start point is moved to the box edge; consider default magnet = Auto in Connector | Phase 15 demo | DONE in rc2: Start/End Magnet default Auto |
| D15-002 | Look + Bloom on a bright plain card blows out to white: gentler default | Phase 15 demo | DONE in rc2: Glow Behind Object is on by default in Look and Bloom |
