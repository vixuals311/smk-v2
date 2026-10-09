# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–5 done (motion core, Shape, UI Block, Progress, Text, Cursor). Phase 6: `SMK2_Callout` + Shape line endpoints / draw-on / end dot, awaiting `docs/PHASE6_GATE.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
