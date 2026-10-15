# SMK v2 performance (Phase 12, H9)

Resolve Studio 21.1.0.14, Windows 11, project `SMK Phase12`. Scripting only. Method: one comp per item (`H9_<item>_<1080p|4K>`), 60 fps comp = timeline rate, **cold** (Background +0.001 before each run), 300 frames rendered to PNG through the Deliver queue; ms/frame = (last PNG time − first PNG time) ÷ 299. Each item is rendered twice: **first** (cold, includes kernel compile / cache fill) and **second** (warm). "Δ" = item minus the "no effect" comp (Text+ over a plain background: **4.7 / 4.9 ms at 1080p, 18.4 / 18.4 ms at 4K**, first / second). Raw data and scripts: `docs/phase12_evidence/` (`h9_*.json`, `h9s_*.json`, `h10_*.json`, `perf_table.md`, `h14.py`, `h15.py`, `benchread.py`).

How to read the numbers: the PNG encoder and disk write dominate small effects (that is the 4.7 ms baseline); numbers below ±1 ms are noise. Viewer playback fps was **NOT VERIFIED** (yours).

## 1. Each Fuse and macro alone (flag: Δ > 5 ms per instance at 1080p)

Image Fuses are fed by a Text+ (DoD ≈ the text box), Shape/Cursor/Connector/macros are generators. **Caveat:** an image Fuse fed by a small source does only a small amount of work (section 3), so Fuse rows below are a *lower bound*; section 2 uses a frame-filling Shape card as source, which matches Phases 8–10.

| Product | 1080p first | 1080p second | Δ first | **Δ second** | 4K first | 4K second | Δ first | Δ second | > 5 ms at 1080p? |
|---|---|---|---|---|---|---|---|---|---|
| Animator | 9.6 | 7.7 | 4.9 | 2.8 | 18.6 | 18.6 | 0.2 | 0.2 | ok |
| Motion (modifier on Text+ Size) | 13.3 | 13.0 | 8.6 | 8.1 | 36.6 | 33.9 | 18.2 | 15.5 | **> 5 ms** |
| MotionRig (modifier on Merge) | 7.6 | 7.5 | 2.9 | 2.6 | 18.8 | 18.4 | 0.4 | 0.0 | ok |
| Shape | 13.5 | 9.3 | 8.8 | 4.4 | 25.5 | 18.2 | 7.1 | −0.2 | first run only |
| Cursor | 12.1 | 8.8 | 7.4 | 3.9 | 29.8 | 24.7 | 11.4 | 6.3 | first run only |
| Connector | 10.7 | 10.6 | 6.0 | 5.7 | 25.2 | 18.6 | 6.8 | 0.2 | **> 5 ms** |
| Look (defaults: glow on) | 7.4 | 8.0 | 2.7 | 3.1 | 30.5 | 25.7 | 12.1 | 7.3 | ok (4K +7) |
| Relief | 5.3 | 5.0 | 0.6 | 0.1 | 18.6 | 18.1 | 0.2 | −0.3 | ok |
| Reflection | 12.1 | 8.5 | 7.4 | 3.6 | 26.2 | 22.4 | 7.8 | 4.0 | first run only |
| PageCurl | 10.7 | 7.5 | 6.0 | 2.6 | 23.8 | 20.5 | 5.4 | 2.1 | first run only |
| Bloom | 5.5 | 4.9 | 0.8 | 0.0 | 19.4 | 19.0 | 1.0 | 0.6 | ok |
| LongShadow | 5.4 | 5.2 | 0.7 | 0.3 | 18.7 | 19.1 | 0.3 | 0.7 | ok |
| SMK2_UIBlock | 22.5 | 15.6 | 17.8 | 10.7 | 40.7 | 31.9 | 22.3 | 13.5 | **> 5 ms** |
| SMK2_ProgressRing | 27.6 | 19.8 | 22.9 | 14.9 | 46.6 | 38.5 | 28.2 | 20.1 | **> 5 ms** |
| SMK2_ProgressBar | 27.9 | 20.2 | 23.2 | 15.3 | 47.3 | 38.2 | 28.9 | 19.8 | **> 5 ms** |
| SMK2_TextLetter (default text) | 20.0 | 19.4 | 15.3 | 14.5 | 36.6 | 35.1 | 18.2 | 16.7 | **> 5 ms** |
| SMK2_TextWord | 20.7 | 19.3 | 16.0 | 14.4 | 51.2 | 37.1 | 32.8 | 18.7 | **> 5 ms** |
| SMK2_TextLine | 19.9 | 19.5 | 15.2 | 14.6 | 36.3 | 39.0 | 17.9 | 20.6 | **> 5 ms** |
| SMK2_Callout | 29.1¹ | 14.9 | 24.4 | 10.0 | 84.0 | 85.6 | 65.6 | 67.2 | **> 5 ms** |
| SMK2_CardStack | 89.1 | 28.4 | 84.4 | 23.5 | 121.1 | 65.9 | 102.7 | 47.5 | **> 5 ms** |
| SMK2_StatCard | 26.0 | 16.9 | 21.3 | 12.0 | 59.0 | 33.0 | 40.6 | 14.6 | **> 5 ms** |
| SMK2_ClickDemo | 28.0 | 17.1 | 23.3 | 12.2 | 105.7 | 88.9 | 87.3 | 70.5 | **> 5 ms** |

¹ Callout 1080p first run produced 297 of 300 frames inside the wait window (value from 296 intervals).

The `_Glass`, `_Neon` and `_Soft` variants of UIBlock, CardStack, StatCard and ClickDemo have the same node structure as their base macro and were **not benchmarked separately (NOT VERIFIED)**; they were rendered in H1 only.

### What is expensive (flagged, not fixed)
- **Every macro is > 5 ms at 1080p** (second run Δ 10–24 ms): they are built from 5–20 nodes each, several of them full-frame. CardStack is the heaviest (Δ 23.5 ms warm and **84 ms on the first, cold run**: ~3× first/second ratio). At 4K Callout (+67 ms), ClickDemo (+70 ms) and CardStack (+47 ms) are the heaviest.
- **Motion** costs +8 ms at 1080p and +15 ms at 4K *because the animated Text+ Size forces Text+ to re-render every frame*; the modifier itself is cheap (MotionRig, a modifier on a Merge, costs +2.6 ms).
- **Connector** +5.7 ms warm at 1080p, but only +0.2 ms warm at 4K: the 1080p number is noise-prone; first run +6.8 at 4K.
- Look at 4K: +7.3 ms warm (+12 first) with defaults (glow on, Quality Normal).

## 2. Several instances (1080p, 60 fps, 300 frames; frame-filling Shape card feeds each Fuse)

Baseline = the same number of Shape cards with **no** effect. ms/frame first / second run.

| Instances | cards only | + Look | + Relief | + Bloom | + LongShadow |
|---|---|---|---|---|---|
| 1 | 12.2 / 8.7 | 22.9 / 16.0 | 22.6 / 15.6 | 37.9² / 18.7² | 19.3² / 13.4² |
| 5 | 34.8 / 18.3 | 69.3 / 32.7 | 69.1 / 32.6 | 69.2 / 30.2 | 63.4² / 30.6² |
| 10 | 68.5 / 30.8 | 131.3² / 54.8² | 115.4 / 49.0 | 128.4² / 52.1² | 119.9² / 54.9² |

² Measured while a second Claude session was also using the same Resolve instance (see "Measurement caveats"); first-run values may be inflated, second-run values are probably fine. The `cards only` row and the 10× Relief were re-run alone.

Cost per effect instance (second run, effect − cards only, ÷ N): **Look 2.9 (×5) / 2.4 (×10) ms, Relief 2.9 / 1.8 ms, Bloom 2.4 / 2.1 ms, LongShadow 2.5 / 2.4 ms.** All below the 5 ms flag, and scaling is linear (no super-linear growth to 10 instances). These match the Phase 8–10 numbers (≈ 2.6–3 ms each).

### Surprise: the cost depends on the source's data window
The first multi-instance run fed the Fuses from small Text+ nodes: Relief, Bloom and LongShadow ×5 and ×10 then cost **5.0–5.7 ms/frame, the same as no effect** (`H9I_*` dirs, `h9i_a.json`). Look ×10 was 95 / 70 ms in the same setup (Look's shine/outline passes span the frame). Not a bug (a Fuse only processes its input's DoD), but any "cost per Fuse" taken with a small source under-reports what a card or full-frame layer costs. Use section 2.

## 3. Many instances (H10, 1080p, 60 fps, 300 frames)

| Scenario | ms/frame first | ms/frame second | Resolve |
|---|---|---|---|
| 20 × `SMK2_TextLetter` (12 letters each) | 408.2 | 279.6 | built, rendered, responsive |
| 20 × `SMK2_UIBlock` | 108.2 | 107.3 | built, rendered, responsive |
| 10 × `SMK2_StatCard` | 184.5 | 75.3 | built, rendered, responsive |
| 10 × `SMK2_CardStack` | 232.7 | 225.7 | built, rendered, responsive |
| 5 × Bloom (frame-filling cards) | 69.2 | 30.2 | built, rendered, responsive |

- 20 TextLetters = 14 ms warm per instance (single TextLetter: 14.5): linear.
- 10 CardStacks cost 22.6 ms each warm: the heaviest per-instance cost in the toolkit; with 10 of them the comp renders at ~4.4 fps through the PNG deliver path. An earlier run of the same comp while another session was rendering gave 820 ms/frame, which is why this scenario was repeated alone.
- "Responsive" = scripting calls kept being answered during and after the runs and the project saved; the UI itself and viewer fps were **NOT VERIFIED**.
- Memory: Resolve process after the whole H9/H10/H11 session (138 timelines in the project, many timelines opened): working set **8.6 GB**, private bytes **13.9 GB**. No per-scenario before/after numbers were taken: **a per-scenario memory figure is NOT VERIFIED**.

## Measurement caveats (read before quoting any number)
- First-run numbers include kernel compile and cache fill; use the **second** column for steady-state.
- Between roughly 17:55 and 18:45 a second Claude session (a fork of this one) was running its own benchmarks on the same Resolve. Items marked ² and the first CardStack ×10 run (820 ms) were affected; everything else was measured with Resolve otherwise idle.
- Some numbers are PNG-encode-bound (≈ 4.7 ms at 1080p, 18.4 ms at 4K); GPU time without PNG encoding was not separated (**NOT VERIFIED**).
- The Python-in-Resolve benchmark threads stalled several times (the script thread simply stopped; Resolve was fine). Items were re-run, not interpolated.
