# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # copy Fuses into Resolve
```

**Status:** Phases 0–4d done (SMK Text complete; UTF-8 character count fix pending a Resolve re-check). Next: Callout, Connector, Look, Cursor, Studio Lite.

This repo was split out of the v1 repo's `smk-v2/` folder.
