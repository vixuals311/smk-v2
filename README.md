# SMK v2 — Fusion SaaS Motion Kit v2

Rebuild of the v1 runtime. Motion is driven through one modifier per element (no extra nodes); see below. See `docs/ARCHITECTURE.md` and the Master Plan.

```
python build/build.py            # src -> dist/fuses, dist/spikes, dist/SMK2_Phase0_Spikes_*.zip
pip install lupa
for t in tests/test_*.py; do python $t; done
python scripts/install.py        # build + copy Fuses and macros into Resolve (--dry-run, --uninstall, --target DIR)
python build/package.py          # release zip: dist/release/SMK2_v<VERSION>.zip (+ .sha256), with Windows/macOS installers
python tools/gen_manual.py       # regenerate docs/MANUAL.md from the sources
python build/make_drfx.py        # dist/SMK2_Titles_v<VERSION>.drfx: every product as an Edit-page title (install Fuses first)
```

`studio/SMK2_Stagger.lua` numbers selected elements 0,1,2… so Index × Stagger delays them in order (Resolve Studio Fusion script; dialog shell UNVERIFIED). `LICENSE` is the end-user agreement; `NOTICE` and `docs/CLEAN_ROOM.md` hold the credits and clean-room review.

**Download (2.0.0):** `releases/SMK2_v2.0.0.zip` (everything: Fuses, macros, installers, manual, licence, and the Edit-page titles bundle) and `releases/SMK2_Titles_v2.0.0.drfx` (titles only; install the Fuses first). SHA-256 in `releases/*.sha256`.

**Status:** Phases 0–8 done and gated in Resolve (Callout parked). Shipped Fuses: Shape, Cursor, Connector, Look, Relief, Reflection, Page Curl, Animator/Motion/MotionRig, plus generated macros (UI Block, Progress Ring/Bar, Text Letter/Word/Line). Phase 9 passed: `SMK2_Bloom` (multi-pass pyramid glow, cost independent of radius). Release tooling (M5) done: package, installer, manual, stagger tool, licence review. Phase 10 passed (Long Shadow, Reflection blur, Look outline). Phase 11 passed: products `SMK2_CardStack`, `SMK2_StatCard`, `SMK2_ClickDemo` and Glass/Neon/Soft style presets (22 macros). Phase 12 (hardening) done: 33/34 tools pass, cost table in `docs/PERFORMANCE.md`; H5 was a bad test trim (corrected in Phase 13; the defensive unknown-clip-length fix stays). Phase 14 passed (Edit-page titles `.drfx`). **Release 2.0.0 (rc1 verified from the zip in Phase 15, rc2 defaults re-checked in Phase 16). Awaiting the owner's hand-check list (`docs/PHASE15_GATE.md`, bottom). Results: `docs/PHASE*_RESULTS.md`; open items: `docs/DEFERRED_WORK.md`; agents: `docs/AGENTS_PLAN.md`.

This repo was split out of the v1 repo's `smk-v2/` folder.
