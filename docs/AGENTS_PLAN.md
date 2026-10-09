# Agent plan — DECISION: one Resolve agent only (user, 2026-10)

**Update:** we run a single agent (Agent A, Resolve QA). Agent B below is optional and NOT being run now; its repo-only tasks (manual generator, packaging, installer, stagger tool, licence review)
will be done by the lead session between Resolve rounds instead. The section is kept for reference.

# (reference) Two-agent plan

Resolve can only be driven by **one** agent at a time (one app, one project database, UI focus) — two agents in Resolve crash it or corrupt each other's comps.
So the split is by *what needs Resolve*:

* **Agent A — "Resolve QA"**: the only agent that touches Resolve. Runs `docs/PHASE7_GATE.md` (Connector, then Look), fixes generator/Fuse bugs it finds, writes `docs/PHASE7_RESULTS.md`, pushes branch `phase7-results`.
  May edit: `src/fuses/*`, `src/core/*`, `build/make_macros.py`, `tests/test_connector*.py`, `tests/test_look.py`, `docs/PHASE7_*`, `docs/phase7_evidence/`.
* **Agent B — "Repo & packaging"**: never opens Resolve. Works only on files Agent A does not own, on branch `agent-b-phase7`:
  `docs/manual/`, `tools/`, `packaging/`, `studio/`, `scripts/` (installer), `tests/test_package*.py`, `tests/test_studio*.py`, `NOTICE`, `LICENSE`, `docs/PHASE7B_*`.
  It runs the existing test suites to make sure nothing regresses and reports any failure instead of editing Agent A's files.
* **Merge rule:** I (the lead session) merge both branches into `main`; neither agent pushes to `main`. Agent B pulls `main` before starting each task.

## Agent B tasks (no Resolve needed)
1. **B1 Manual generator** `tools/gen_manual.py`: load every built Fuse in a mocked Fusion API (see `tests/test_fuse_harness.py` pattern), dump each input (ID, display name, type, default, range, menu items) into `docs/manual/<Node>.md` tables, and add hand-written Quick Start sections (what it is, 3-step use, tips, known limits from `docs/ARCHITECTURE.md`). Also one page per macro (parse `dist/templates/*.setting`: published controls by page).
2. **B2 Packaging** `build/package.py`: release zip `SMK2_v<ver>.zip` with `Fuses/SMK2/*.fuse`, `Macros/SMK2/*.setting`, installers for Windows (`install.bat`) and macOS (`install.command`), `README`, `NOTICE`; strips `._*`, `.DS_Store`, `__MACOSX`, `CustomData.Path`; SHA-256 manifest. Tests (`tests/test_package.py`): archive contents, no absolute/personal paths, every `.setting` parses (brace balance), every Fuse loads in the mock harness, versions consistent.
3. **B3 Installer hardening** `scripts/install.py`: `--dry-run`, `--uninstall`, `--target <dir>`, Windows/macOS/Linux path detection, clear messages; tests with temp dirs for all three platform branches (mock `sys.platform`).
4. **B4 Studio Lite stagger tool** (`studio/SMK2_Stagger.lua`): Fusion-page script that assigns **Index** 0..n−1 (and optionally sets **Stagger**) on the selected SMK nodes/macros, ordered by selection order, X position, or Y position; one undo transaction (`comp:StartUndo/EndUndo`); never keyframes/indexes StartFrame-style inputs (use `SetInput`). Put the ordering/assignment logic in a pure Lua module with unit tests via `lupa` (mock tools: `GetAttrs().TOOLS_RegID`, `GetInputList`, `SetInput`, `GetInput`, `Name`); the Fusion-facing shell stays tiny. Mark the shell UNVERIFIED (Agent A will test it later). Which inputs to set: Fuses `Index`/`Stagger`; macros: the published `Animator_Index`/`Animator_Stagger` (or `Index`/`Stagger` for text and progress macros) — discover from `dist/templates/*.setting`.
5. **B5 Clean-room / licence review:** grep the repo for NeoEdit names, author paths (`/Users/`, drive letters), copied code; write `NOTICE`; confirm no `CustomData.Path` in templates; list any findings in `docs/PHASE7B_REVIEW.md`. Run `/code-review` (high) on `src/` and report findings (do not edit Agent A's files — list them).
Report at the end: one table (task, files added, tests added, result), pushed on `agent-b-phase7`.
