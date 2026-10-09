# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–7 done (Callout parked). Phase 8 built and unit-tested, awaiting `docs/PHASE8_GATE.md`: `SMK2_Relief` (bevel/emboss), `SMK2_Reflection`, `SMK2_PageCurl`, Look upgrades (glow only, spread, adaptive quality), Connector 192-point paths, spike S12 (multi-pass GPU). Two-agent plan: `docs/AGENTS_PLAN.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
