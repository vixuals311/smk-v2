# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # build + copy Fuses and macros into Resolve (--dry-run, --uninstall, --target DIR)
python build/package.py          # release zip: dist/release/SMK2_v<VERSION>.zip (+ .sha256), with Windows/macOS installers
python tools/gen_manual.py       # regenerate docs/MANUAL.md from the sources
```

`studio/SMK2_Stagger.lua` numbers selected elements 0,1,2… so Index × Stagger delays them in order (Resolve Studio Fusion script; dialog shell UNVERIFIED). `NOTICE` and `docs/CLEAN_ROOM.md` hold the licence / clean-room review.

**Status:** Phases 0–8 done and gated in Resolve (Callout parked). Shipped Fuses: Shape, Cursor, Connector, Look, Relief, Reflection, Page Curl, Animator/Motion/MotionRig, plus generated macros (UI Block, Progress Ring/Bar, Text Letter/Word/Line). Phase 9 passed: `SMK2_Bloom` (multi-pass pyramid glow, cost independent of radius). Release tooling (M5) done: package, installer, manual, stagger tool, licence review. Next: long shadow and Reflection blur on the multi-pass path. Results: `docs/PHASE*_RESULTS.md`; open items: `docs/DEFERRED_WORK.md`; agents: `docs/AGENTS_PLAN.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
