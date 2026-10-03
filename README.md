# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–2d done (see `docs/PHASE*_RESULTS.md`). Phase 3: Shape track colour + `SMK2_ProgressRing` / `SMK2_ProgressBar` macros, awaiting `docs/PHASE3_GATE.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
