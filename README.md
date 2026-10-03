# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–4 done; spikes S8–S10 done. Phase 4b: SMK Text rebuilt as a chain (28 ms/12 letters) with auto letter count, awaiting `docs/PHASE4B_GATE.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
