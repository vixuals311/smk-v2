# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime around one GPU engine node per element. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
python tests/test_smk_core.py && python tests/test_fuse_harness.py
```

**Status:** Phase 0 passed (see `docs/PHASE0_RESULTS.md`). Phase 1 built: `smk_core` v2, `SMK2_Motion` modifier and `SMK2_Animator`
GPU Fuse (written against the Phase 0 findings; awaiting the gate in `docs/PHASE1_GATE.md`).
Install into Resolve: `python scripts/install.py`.

This repo was split out of the v1 repo's `smk-v2/` folder.
