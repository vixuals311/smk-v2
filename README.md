# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime around one GPU engine node per element. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
python tests/test_smk_core.py && python tests/test_fuse_harness.py
```

**Status:** Phase 0 prepared (6 spikes + checklist, `docs/PHASE0_CHECKLIST.md`); Phase 1 started (`smk_core` v2 + `SMK2_Motion`
modifier). The Animator GPU Fuse waits for the S1/S3/S4/S6 results — no GPU production code before the gate.

This repo was split out of the v1 repo's `smk-v2/` folder.
