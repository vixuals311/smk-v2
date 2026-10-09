# Deferred work register (v2)

| ID | Item | Why deferred | Status |
|---|---|---|---|
| D2-001 | Share Inspector helpers (phase controls, engine cfg) between Animator, Rig and Shape via a build-time module | Three copies exist; refactor deferred until Resolve-verified | OPEN |
| D2-002 | In-kernel motion blur | Phase 0 S6: native Transform blur is faster/cleaner in chains | DEFERRED (use native Transform) |
| D2-003 | DoD shrink | Phase 0 S4: `DataWindow` assignment ignored | DEFERRED |
| D2-004 | Merge Pivot via script/Rig | Phase 1b R5: Merge has no scriptable Pivot input | OPEN |
| D2-005 | Shape: arrow (line end dot done in Phase 6), glass/backdrop blur, inverted (spotlight) mode, gradient stops > 2 | Not in first slice | OPEN |
| D2-006 | SMK Look (glow, outline, shine, long shadow) | Phase 2 second slice | OPEN |
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
| D7-002 | Look: long shadow (log-step), inner glow/shadow, bevel, pyramid glow (multi-pass; needs a multi-pass DVIP spike), bilinear-accurate test oracle | Beyond first Look slice | OPEN |
| D2-011 | Multi-element Shape (one Fuse, N elements: bars, grids, lists) | Fallback if S7 fails; also suits charts | OPEN |
