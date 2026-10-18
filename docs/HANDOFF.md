# Handoff — continuing SMK v2 on another device / in a new chat

**Repo:** `vixuals311/smk-v2`, branch `main` (release **2.0.0**; files in `releases/`). Start a new chat with: *"Read README.md and docs/HANDOFF.md in vixuals311/smk-v2 and continue."*

## What this is
Fusion SaaS Motion Kit v2 for DaVinci Resolve/Fusion: GPU Fuses (Shape, Cursor, Connector, Look, Relief, Reflection, Page Curl, Bloom, Long Shadow, Animator, Motion, Motion Rig) + 22 generated macros
(UI Block, Progress Ring/Bar, Text Letter/Word/Line, Callout, Card Stack, Stat Card, Click Demo, and Glass/Neon/Soft variants) + an Edit-page titles bundle (`.drfx`). Seconds-based, clip-relative timing; sizes in px @1920; positive angle = counter-clockwise.
Plan and design: `docs/ARCHITECTURE.md`; engines: `docs/MOTION_ENGINES_REFERENCE.md`; costs: `docs/PERFORMANCE.md`; manual (generated): `docs/MANUAL.md`; clean-room/licence: `NOTICE`, `docs/CLEAN_ROOM.md`.

## Status
Phases 0–16 done. Every phase has `docs/PHASE<N>_GATE.md` (what to test) and `docs/PHASE<N>_RESULTS.md` (what Resolve showed). Release candidate verified from the zip (Phase 15, 9/9). Owner hand-check of rc1: all good; viewer 4–5 fps first pass, 24 fps cached (normal; see manual "Playback speed").
rc2 changed defaults only (Connector magnets Auto, Look/Bloom glow behind): **re-checked in Resolve in Phase 16, all pass** (`docs/PHASE16_RESULTS.md`). Remaining before 2.0.0: owner approval, then set VERSION and package.

## Open items (see `docs/DEFERRED_WORK.md`)
1. **Licence**: DONE: proprietary end-user agreement in `LICENSE` (draft, no legal review; fill in the licensor name and contact before selling).
2. 2.0.0 released (VERSION, zip, sha256 and drfx in `releases/`).
3. Optional: macro cost optimisation (D12-002; CardStack 23.5 ms warm), Studio Lite (D14-001, recommended to drop), Callout rework (parked), Click Demo button reaction (D11-002), Stat Card auto-shrink (D11-001).

## How we work (the loop)
- Lead session (Claude, no Resolve): builds code + unit tests (`for t in tests/test_*.py; do python3 $t; done`; needs `pip install lupa`; gcc optional for kernel-parity), writes the next `docs/PHASE<N>_GATE.md`, pushes to `main`.
- One Claude Desktop agent (Resolve, scripting only) runs the gate, writes `docs/PHASE<N>_RESULTS.md`, pushes branch `phase<N>-results`. Lead merges: `git fetch origin phase<N>-results:refs/remotes/origin/phase<N>-results && git merge origin/phase<N>-results`.
- **Only one session may drive Resolve** (two sessions crashed it once).
- Standard gate rules for the agent: scripting only; deselect (`FlowView.Select()`) before each paste; comp rate = timeline rate; cold renders (Background +0.001); readable node graphs (distinct `flow:SetPos`, left→right, 2–3 units apart, clear names, one comp per check named after the check, a Note per group); `ProjectManager.SaveProject()`; phase-named project; keep "SMK Test" untouched; write NOT VERIFIED where not observed; Shape sources are empty on frame 0 and the last frames.
- Build: `python build/build.py` (src → dist). Install: `python scripts/install.py` (`--dry-run`, `--uninstall`, `--target`). Release: `python build/package.py`. Manual: `python tools/gen_manual.py`. Titles: `python build/make_drfx.py`.

## Hard-won rules (each cost a Resolve round)
- Fuse: globals (not file locals) shared between `Create()` and `Process`; `req:IsPreCalc()` early return; `IMG_DataWindow` is the only way to pad/place an image; multi-pass DVIP and two source textures work (S12, Phase 8); Fuses need ~3 ms/instance/frame.
- Macros/expressions: read an input's `.Value` for text; never read another tool's `.Output`; read the source tool's own input, not a linked one; wide `INP_MinAllowed/MaxAllowed` when the slider range is narrower than the legal range; expressions ≤ ~2300 chars; forward-only DAG; Text+ per-letter animation via StyledTextFollower bound to Calculation/Vector.
- A `.drfx` carries titles but not Fuses; Resolve loads every sub-folder of `Fuses/` (keep old spikes out); missing Fuses → "Unknown tool" modal that freezes scripting.
- Unit tests must feed text controls as objects, and must execute the generated expressions.
