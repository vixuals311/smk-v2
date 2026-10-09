# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–8 done and gated in Resolve (Callout parked). Shipped Fuses: Shape, Cursor, Connector, Look, Relief, Reflection, Page Curl, Animator/Motion/MotionRig, plus generated macros (UI Block, Progress Ring/Bar, Text Letter/Word/Line). Next: multi-pass Look (pyramid glow, bloom, long shadow; spike S12 passed), release packaging, manual. Results: `docs/PHASE*_RESULTS.md`; open items: `docs/DEFERRED_WORK.md`; agents: `docs/AGENTS_PLAN.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
