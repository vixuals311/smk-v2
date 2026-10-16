# SMK v2 manual (v2.0.0-rc2)

_Generated from the sources by `tools/gen_manual.py` — do not edit by hand._

## Install

Windows: run `install.bat`. macOS: run `install.command`. Any OS: `python3 install.py` (`--dry-run`, `--uninstall`, `--target <Fusion folder>`). Restart Resolve.
Fuses: Effects ▸ Fuses ▸ SMK v2. Macros: Effects ▸ Tools ▸ Macros ▸ SMK2. Edit-page titles (optional): double-click `SMK2_Titles_*.drfx` and confirm; they appear under Effects ▸ Titles ▸ SMK2.

> **Install the Fuses first** (`install.py`), then the titles. Without the Fuses every title and macro opens with *Warning: Unknown tool found … Fuse.SMK2_Shape*; install the Fuses and restart Resolve. Do not keep old spike Fuses in `Fuses/`: Resolve loads every sub-folder.

## Conventions

- **Seconds, clip-relative** timing: everything starts at the clip's first frame and ends with it; frame rate does not change the look.
- **Sizes are px @1920**: the same value looks identical at 1080p, vertical and 4K.
- **Angles:** positive = counter-clockwise. **Colours** are straight RGBA pickers.
- **In / Hold / Out:** each phase has its own engine (Ease, Spring, Bounce, Elastic, Overshoot, Inertia) and its own timing; Index × Stagger delays each copy.

## Fuses

### SMK2 Animator

Seconds-based In/Hold/Out animator (fade, slide, scale, rotate).

> SMK2_Animator — image tool. One GPU pass: In/Hold/Out move (fade, slide, scale, rotate), seconds-based,
> clip-relative, own engine per phase, Index x Stagger. Full-frame output (S4: DoD shrink unsupported).
> Motion blur: use a native Transform (S6). Core is inlined at build time.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| In Delay (s) | slider | 0 | 0 .. 10 |
| In Duration (s) | slider | 0.5 | 0 .. 10 |
| Out Offset (s) | slider | 0 | 0 .. 10 |
| Out Duration (s) | slider | 0.5 | 0 .. 10 |
| Index | slider | 0 | 0 .. 500 |
| Stagger (s) | slider | 0 | 0 .. 1 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |
| Pivot X | slider | 0.5 | 0 .. 1 |
| Pivot Y | slider | 0.5 | 0 .. 1 |
| In / Hold / Out motion | group |  | timing, engine and amount controls per phase (see the motion reference) |

### SMK2 Bloom

Pyramid (multi-pass) glow with a large soft radius at fixed cost.

> SMK2_Bloom — pyramid glow in 8 GPU passes (extract+downsample, 5 more downsamples, one composite). Cost is nearly independent of the radius, so big soft glows stay cheap.
> Glow from Alpha or Brightness; colour, intensity, spread (gamma), behind/additive/glow-only. Output window is padded by the glow reach (IMG_DataWindow). Sizes px @1920.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Radius (px @1920) | slider | 120 | 4 .. 400 |
| Intensity (Bloom is softer than Look: ~4x Look) | slider | 4 | 0 .. 20 |
| Brightness Threshold | slider | 0.6 | 0 .. 0.99 |
| Spread (gamma; below 1 = wider, brighter tails) | slider | 1 | 0.3 .. 3 |
| Opacity | slider | 1 | 0 .. 1 |
| Glow From | choice | 0 | Alpha / Brightness |
| Glow Behind Object (off = additive) | checkbox | 1 | on/off |
| Glow Only (no object) | checkbox | 0 | on/off |
| Glow Colour | colour | 0.45, 0.65, 1, 1 | RGBA |

### SMK2 Connector

Editable connector (handles, points, magnets, dashes, arrows, pulses) with draw-on motion.

> SMK2_Connector — connector line between two points / boxes. One Fuse: Curve, Straight, Elbow, Bezier (two draggable handles) or Spline
> (through up to 6 draggable points); magnetic ends that snap to a box edge or a side port; dashes, gradient, dot/arrow ends, travelling pulses;
> built-in draw-on / un-draw motion with Index x Stagger. Seconds-based, clip-relative.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Start Box Width (frac of frame width) | slider | 0.2 | 0.005 .. 1 |
| Start Box Height (frac of frame width) | slider | 0.1 | 0.005 .. 1 |
| End Box Width (frac of frame width) | slider | 0.2 | 0.005 .. 1 |
| End Box Height (frac of frame width) | slider | 0.1 | 0.005 .. 1 |
| Magnet Gap (px @1920) | slider | 6 | 0 .. 60 |
| Curve Bend | slider | 0.45 | 0 .. 1.5 |
| Elbow Corner Radius (px @1920) | slider | 24 | 0 .. 200 |
| Spline Points (0-6) | slider | 2 | 0 .. 6 |
| Spline Tension (0 = polyline, 1 = smooth) | slider | 1 | 0 .. 2 |
| Line Thickness (px @1920) | slider | 4 | 0.5 .. 60 |
| Dash Length (px @1920, 0 = solid) | slider | 0 | 0 .. 200 |
| Dash Gap (px @1920) | slider | 12 | 0 .. 200 |
| End-Mark Size (px @1920) | slider | 18 | 2 .. 100 |
| Pulse Speed (cycles per second) | slider | 0.4 | 0.05 .. 4 |
| Pulse Count (1-3) | slider | 2 | 1 .. 3 |
| Pulse Size (px @1920) | slider | 12 | 2 .. 80 |
| Draw Delay (s) | slider | 0 | 0 .. 10 |
| Draw Time (s) | slider | 0.7 | 0 .. 10 |
| Out Offset (s) | slider | 0 | 0 .. 10 |
| Out Duration (s) | slider | 0.5 | 0 .. 10 |
| Index | slider | 0 | 0 .. 500 |
| Stagger (s) | slider | 0 | 0 .. 1 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |
| Spring Stiffness | slider | 180 | 1 .. 1000 |
| Spring Damping | slider | 18 | 0 .. 100 |
| Overshoot | slider | 1.70158 | 0 .. 5 |
| Path Style | choice | 0 | Curve / Straight / Elbow / Bezier (handles) / Spline (through points) |
| Start Magnet | choice | 1 | Off / Auto (edge toward target) / Top / Right / Bottom / Left |
| End Magnet | choice | 1 | Off / Auto (edge toward target) / Top / Right / Bottom / Left |
| Start End-Mark | choice | 1 | None / Dot / Arrow |
| End End-Mark | choice | 2 | None / Dot / Arrow |
| Draw Engine | choice | 0 |  |
| Out Engine | choice | 0 |  |
| Gradient Along Line | checkbox | 0 | on/off |
| Travelling Pulses | checkbox | 0 | on/off |
| Enable Out (un-draw) | checkbox | 1 | on/off |
| Line Color | colour | 0.3, 0.55, 1, 1 | RGBA |
| End Color (gradient) | colour | 0.7, 0.4, 1, 1 | RGBA |
| Pulse Color | colour | 1, 1, 1, 0.95 | RGBA |

### SMK2 Cursor

Cursor path with waypoints, press and click ripples.

> SMK2_Cursor — cursor + click generator. One Fuse: anti-aliased pointer (polygon SDF, no image file), waypoints with move / hold /
> click, a gentle arc, press dip, up to 3 simultaneous click ripples, fade in/out. Seconds-based and clip-relative.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Waypoints (2-8) | slider | 3 | 2 .. 8 |
| Path Arc | slider | 0.12 | -0.5 .. 0.5 |
| Start Delay (s) | slider | 0.4 | 0 .. 10 |
| Fade In (s) | slider | 0.25 | 0 .. 3 |
| Fade Out (s) | slider | 0.3 | 0 .. 3 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |
| Cursor Size (frac of frame width) | slider | 0.03 | 0.005 .. 0.2 |
| Outline Width (px @1920) | slider | 2 | 0 .. 20 |
| Shadow X (px @1920) | slider | 2 | -50 .. 50 |
| Shadow Y, down (px @1920) | slider | 4 | -50 .. 50 |
| Shadow Blur (px @1920) | slider | 6 | 0 .. 50 |
| Click Delay After Arrival (s) | slider | 0.12 | 0 .. 2 |
| Press Duration (s) | slider | 0.18 | 0.02 .. 1 |
| Press Depth | slider | 0.14 | 0 .. 0.5 |
| Ripple Radius (frac of frame width) | slider | 0.04 | 0.005 .. 0.3 |
| Ripple Thickness (px @1920) | slider | 5 | 0.5 .. 40 |
| Ripple Duration (s) | slider | 0.6 | 0.05 .. 3 |
|   Move to " .. i .. " (s) | slider | d[3] > 0 and d[3] or 1 | 0 .. 10 |
|   Hold at " .. i .. " (s) | slider | d[4] or 0.3 | 0 .. 10 |
| Move Style | choice | 0 | Smooth / Snappy / Spring |
| Cursor Color | colour | 1, 1, 1, 1 | RGBA |
| Outline Color | colour | 0.05, 0.05, 0.08, 1 | RGBA |
| Shadow Color | colour | 0, 0, 0, 0.35 | RGBA |
| Ripple Color | colour | 0.25, 0.55, 1, 0.9 | RGBA |

### SMK2 Long Shadow

Long flat shadow with distance fade, multi-pass GPU.

> SMK2_LongShadow — flat "long shadow" behind any element, multi-pass GPU (init + log2(length) doubling passes + one composite). Cost grows with log(length), not length.
> The shadow falls in the chosen direction (deg, positive = counter-clockwise; -45 = down-right) and fades linearly to nothing at Length (px @1920).
> The output window is padded only on the shadow's side. Shadow alpha comes from the element's alpha; colour and opacity are controls.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Shadow Direction (deg: 0 = right, 90 = up, -45 = down-right) | slider | -45 | -360 .. 360 |
| Length (px @1920) | slider | 400 | 5 .. 1500 |
| Fade Curve (1 = linear, <1 = longer, brighter) | slider | 1 | 0.3 .. 3 |
| Opacity | slider | 1 | 0 .. 1 |
| Shadow Colour | colour | 0, 0, 0, 0.5 | RGBA |

### SMK2 Look

Glow, outline, shine sweep and gradient overlay in one GPU pass.

> SMK2_Look — finishing pass for any image: glow, outline, shine sweep, gradient overlay. One Fuse, one GPU pass (bounded sample counts).
> Premultiplied-correct; sizes in px @1920 so it looks the same at any resolution. Shine can auto-sweep (seconds, clip-relative).

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Glow Radius (px @1920) | slider | 40 | 1 .. 300 |
| Glow Intensity | slider | 1.2 | 0 .. 6 |
| Brightness Threshold | slider | 0.6 | 0 .. 0.99 |
| Glow Spread (gamma; below 1 = wider, brighter tails) | slider | 1 | 0.3 .. 3 |
| Outline Width (px @1920) | slider | 6 | 0.5 .. 60 |
| Shine Angle (deg) | slider | 25 | -180 .. 180 |
| Shine Half-Width (frac of frame width) | slider | 0.04 | 0.002 .. 0.5 |
| Shine Softness (frac of frame width) | slider | 0.03 | 0 .. 0.3 |
| Shine Intensity | slider | 0.8 | 0 .. 3 |
| Shine Position (manual, -1..1) | slider | -1 | -1.5 .. 1.5 |
| Sweep Delay (s) | slider | 0.4 | 0 .. 10 |
| Sweep Duration (s) | slider | 0.9 | 0.05 .. 10 |
| Repeat Every (s, 0 = once) | slider | 0 | 0 .. 20 |
| Gradient Angle (deg) | slider | 90 | -360 .. 360 |
| Gradient Amount | slider | 1 | 0 .. 1 |
| Opacity | slider | 1 | 0 .. 1 |
| Glow From | choice | 0 | Alpha / Brightness |
| Glow Quality | choice | 1 | Draft (24) / Normal (48) / High (96) / Max (160) |
| Glow | checkbox | 1 | on/off |
| Glow Only (no object) | checkbox | 0 | on/off |
| Glow Behind Object (off = additive) | checkbox | 1 | on/off |
| Outline | checkbox | 0 | on/off |
| Shine | checkbox | 0 | on/off |
| Shine Auto Sweep (seconds, clip-relative) | checkbox | 1 | on/off |
| Gradient Overlay | checkbox | 0 | on/off |
| Glow Color | colour | 0.45, 0.65, 1, 1 | RGBA |
| Outline Color | colour | 1, 1, 1, 1 | RGBA |
| Shine Color | colour | 1, 1, 1, 1 | RGBA |
| Gradient Color A | colour | 1, 0.5, 0.2, 1 | RGBA |
| Gradient Color B | colour | 0.4, 0.3, 1, 1 | RGBA |

### SMK2 Motion

Seconds-based In/Hold/Out motion modifier (Ease, Spring, Bounce, Elastic, Overshoot, Inertia).

> SMK2_Motion — Number modifier. One engine dropdown, seconds-based, clip-relative, In/Hold/Out.
> Only the active phase's engine is evaluated. Core is inlined at build time (see build/build.py).

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| From | slider | 0 | -10 .. 10 |
| Rest | slider | 1 | -10 .. 10 |
| To | slider | 0 | -10 .. 10 |
| In Delay (s) | slider | 0 | 0 .. 10 |
| In Duration (s) | slider | 0.5 | 0 .. 10 |
| Out Offset (s) | slider | 0 | 0 .. 10 |
| Out Duration (s) | slider | 0.5 | 0 .. 10 |
| Index | slider | 0 | 0 .. 200 |
| Stagger (s) | slider | 0 | 0 .. 1 |
| Spring Stiffness | slider | 180 | 1 .. 1000 |
| Spring Damping | slider | 18 | 0 .. 100 |
| Spring Mass | slider | 1 | 0.1 .. 10 |
| Elastic Amplitude | slider | 1 | 1 .. 4 |
| Elastic Period | slider | 0.3 | 0.05 .. 1 |
| Overshoot | slider | 1.70158 | 0 .. 5 |
| Inertia Decay | slider | 4 | 0.5 .. 12 |
| Bezier x1 | slider | 0.25 | 0 .. 1 |
| Bezier y1 | slider | 0.1 | -1 .. 2 |
| Bezier x2 | slider | 0.25 | 0 .. 1 |
| Bezier y2 | slider | 1 | -1 .. 2 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |

### SMK2 Motion Rig

Seconds-based In/Hold/Out rig: Opacity, Scale, Angle, Offset and Center outputs for an existing Merge.

> SMK2_MotionRig — modifier with several outputs. Attach ONE rig to an existing Merge (or Transform) and wire its
> outputs to Blend / Size / Angle / Center. Zero extra nodes per element (Phase 1 G10: every extra node costs ms).
> Same In/Hold/Out model as SMK2_Animator. Core is inlined at build time.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| In Delay (s) | slider | 0 | 0 .. 10 |
| In Duration (s) | slider | 0.5 | 0 .. 10 |
| Out Offset (s) | slider | 0 | 0 .. 10 |
| Out Duration (s) | slider | 0.5 | 0 .. 10 |
| Index | slider | 0 | 0 .. 500 |
| Stagger (s) | slider | 0 | 0 .. 1 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |
| Base Center X | slider | 0.5 | -2 .. 3 |
| Base Center Y | slider | 0.5 | -2 .. 3 |
| In / Hold / Out motion | group |  | timing, engine and amount controls per phase (see the motion reference) |

### SMK2 Page Curl

Page curl reveal with shaded cylinder, paper back and shadow, one GPU pass.

> SMK2_PageCurl — page-curl transition / reveal in ONE GPU pass. The page rolls over a cylinder; the back of the paper (tinted, dimmed) lies over the front.
> Input = the page; optional Reveal input = what shows underneath (transparent if not connected). Auto In/Out in seconds (clip-relative) or a manual Progress.
> Curl direction = the direction the curl travels (deg, positive = counter-clockwise; 180 = right to left, peeling from the right edge). Sizes are px @1920.

**Inputs:** Image (main image), Reveal (optional) (what shows under the page)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Progress (manual) | slider | 0.5 | 0 .. 1 |
| Delay (s) | slider | 0.2 | 0 .. 20 |
| Duration (s) | slider | 1.2 | 0.05 .. 20 |
| Curl Direction (deg, 180 = right to left) | slider | 180 | -360 .. 360 |
| Roll Radius (px @1920) | slider | 70 | 8 .. 400 |
| Shadow Strength | slider | 0.55 | 0 .. 1 |
| Shadow Length (px @1920) | slider | 120 | 5 .. 600 |
| Ambient Light (0 = deep shading) | slider | 0.45 | 0 .. 1 |
| Light Angle (deg from the viewer) | slider | 35 | -80 .. 80 |
| Paper Back Tint Amount | slider | 0.55 | 0 .. 1 |
| Paper Back Brightness | slider | 0.85 | 0 .. 1.5 |
| Opacity | slider | 1 | 0 .. 1 |
| Mode | choice | 0 | Auto Out (page peels away) / Auto In (page rolls back on) / Manual (use Progress) |
| Paper Back Tint | colour | 0.93, 0.9, 0.82, 1 | RGBA |

### SMK2 Reflection

Floor reflection with distance blur, fade and ripple, one GPU pass.

> SMK2_Reflection — mirror reflection about a horizontal baseline, one GPU pass: blur that GROWS with distance, distance fade, optional animated ripple, tint.
> Baseline is a fraction of the frame height from the bottom. Sizes are px @1920. Ripple animates in seconds (clip-relative).

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Baseline (frac of height from the bottom) | slider | 0.4 | 0 .. 1 |
| Gap (px @1920; + moves the reflection further down) | slider | 0 | -200 .. 400 |
| Reflection Length (px @1920) | slider | 400 | 10 .. 2000 |
| Fade Curve (1 = linear) | slider | 1.5 | 0.3 .. 4 |
| Reflection Opacity | slider | 0.5 | 0 .. 1 |
| Blur at Baseline (px @1920) | slider | 0 | 0 .. 40 |
| Blur Growth (px per 100 px) | slider | 4 | 0 .. 30 |
| Ripple Amount (px @1920) | slider | 0 | 0 .. 40 |
| Ripple Frequency (per 100 px) | slider | 6 | 0.5 .. 40 |
| Ripple Speed (cycles per second) | slider | 0.5 | -5 .. 5 |
| Quality | slider | 1 | 0 .. 2 |
| Opacity | slider | 1 | 0 .. 1 |
| Keep Original (off = reflection only) | checkbox | 1 | on/off |
| Tint (alpha = strength) | colour | 1, 1, 1, 1 | RGBA |

### SMK2 Relief

Bevel and emboss from alpha or brightness, one GPU pass.

> SMK2_Relief — bevel / emboss for any image in ONE GPU pass. Height = alpha or brightness; the slope comes from a single Gaussian-derivative gather
> (no repeated blurs). Light is a direction (deg, positive = counter-clockwise) plus an elevation. Sizes are px @1920.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Size (px @1920) | slider | 8 | 0.5 .. 80 |
| Depth | slider | 2 | 0 .. 12 |
| Light Direction (deg: 0 = from the right, 90 = from the top, 135 = upper left) | slider | 135 | -360 .. 360 |
| Light Elevation (deg) | slider | 45 | 5 .. 89 |
| Highlight Amount | slider | 1.5 | 0 .. 5 |
| Shadow Amount | slider | 1.5 | 0 .. 5 |
| Blend | slider | 1 | 0 .. 1 |
| Opacity | slider | 1 | 0 .. 1 |
| Mode | choice | 0 | Bevel (coloured highlight + shadow) / Relief Map (grey) |
| Height From | choice | 0 | Alpha / Brightness |
| Quality | choice | 1 | Draft (24) / Normal (48) / High (96) |
| Highlight Colour | colour | 1, 1, 1, 1 | RGBA |
| Shadow Colour | colour | 0, 0, 0, 1 | RGBA |

### SMK2 Shape

Rect / rounded / pill / ellipse / ring / line with fill, border, shadow, trim and built-in motion.

> SMK2_Shape — SDF shape generator with built-in In/Hold/Out motion. One Fuse per element (Phase 1: each Fuse
> instance costs ~3 ms/frame, so shape + motion live in the same node). Anti-aliased, resolution-independent.

**Inputs:** Image (main image)

| Control | Type | Default | Range / options |
|---|---|---|---|
| Width (frac of frame width) | slider | 0.3 | 0.001 .. 2 |
| Height (frac of frame width) | slider | 0.15 | 0.001 .. 2 |
| Corner Radius (0.5 = pill) | slider | 0.15 | 0 .. 0.5 |
| Ring / Line Thickness (px @1920) | slider | 24 | 0.5 .. 400 |
| Trim / Sweep | slider | 1 | 0 .. 1 |
| Trim Start | slider | 0 | 0 .. 1 |
| Line End Dot Radius (px @1920) | slider | 0 | 0 .. 60 |
| Angle (deg, CCW) | slider | 0 | -360 .. 360 |
| Center X | slider | 0.5 | -2 .. 3 |
| Center Y | slider | 0.5 | -2 .. 3 |
| Gradient Angle (deg) | slider | 90 | -360 .. 360 |
| Border Width (px @1920) | slider | 0 | 0 .. 100 |
| Shadow X (px @1920) | slider | 0 | -200 .. 200 |
| Shadow Y, down (px @1920) | slider | 12 | -200 .. 200 |
| Shadow Blur (px @1920) | slider | 16 | 0 .. 200 |
| In Delay (s) | slider | 0 | 0 .. 10 |
| In Duration (s) | slider | 0.5 | 0 .. 10 |
| Out Offset (s) | slider | 0 | 0 .. 10 |
| Out Duration (s) | slider | 0.5 | 0 .. 10 |
| Index | slider | 0 | 0 .. 500 |
| Stagger (s) | slider | 0 | 0 .. 1 |
| Clip Length (s, 0=auto) | slider | 0 | 0 .. 600 |
| Shape | choice | 0 | Rectangle / Ellipse / Ring / Arc / Line |
| Fill | choice | 0 | Solid / Linear Gradient / Radial Gradient |
| Border Position | choice | 0 | Inside / Center / Outside |
| Fill Color | colour | 1, 1, 1, 1 | RGBA |
| Fill Color B | colour | 0.4, 0.6, 1, 1 | RGBA |
| Border Color | colour | 1, 1, 1, 1 | RGBA |
| Shadow Color | colour | 0, 0, 0, 0.35 | RGBA |
| Track Color (Trim remainder) | colour | 1, 1, 1, 0 | RGBA |
| Draw On With Motion | checkbox | 0 |  |
| Line Uses End Points | checkbox | 0 |  |
| Line From | slider |  |  |
| Line To | slider |  |  |
| In / Hold / Out motion | group |  | timing, engine and amount controls per phase (see the motion reference) |

## Macros

### SMK2_Callout

65 published controls.

- **Callout:** Text, Font, Text Size, Text Color, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Angle, Card Color, Border Color, Border Width (px @1920), Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Leader:** Line Start (drag in viewer), Target Point (drag in viewer), Line Thickness (px @1920), Target Dot Radius (px @1920), Line Color, Line Draw Time (s)
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_CardStack

66 published controls.

- **Cards:** Text 1, Text 2, Text 3, Text 4, Font, Weight, Text Size, Text Color, Card Width (frac of frame width), Card Height (frac of frame width), Corner Radius, Stack Center X, First Card Y, Shape, Fill, Gap Between Cards (frac of frame width), Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Stagger Between Cards (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_CardStack_Glass

66 published controls.

- **Cards:** Text 1, Text 2, Text 3, Text 4, Font, Weight, Text Size, Text Color, Card Width (frac of frame width), Card Height (frac of frame width), Corner Radius, Stack Center X, First Card Y, Shape, Fill, Gap Between Cards (frac of frame width), Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Stagger Between Cards (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_CardStack_Neon

66 published controls.

- **Cards:** Text 1, Text 2, Text 3, Text 4, Font, Weight, Text Size, Text Color, Card Width (frac of frame width), Card Height (frac of frame width), Corner Radius, Stack Center X, First Card Y, Shape, Fill, Gap Between Cards (frac of frame width), Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Stagger Between Cards (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_CardStack_Soft

66 published controls.

- **Cards:** Text 1, Text 2, Text 3, Text 4, Font, Weight, Text Size, Text Color, Card Width (frac of frame width), Card Height (frac of frame width), Corner Radius, Stack Center X, First Card Y, Shape, Fill, Gap Between Cards (frac of frame width), Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Stagger Between Cards (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ClickDemo

73 published controls.

- **Button:** Button Text, Font, Weight, Text Size, Text Color, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Button Color, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Cursor:** Cursor Start (drag in viewer), Cursor Start Delay (s), Time To Reach The Button (s), Hold On The Button (s), Click Delay After Arrival (s), Move Style, Path Arc, Cursor Size, Ripple Radius, Ripple Duration (s), Cursor Fade In (s), Cursor Fade Out (s), Cursor Color, Ripple Color
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ClickDemo_Glass

73 published controls.

- **Button:** Button Text, Font, Weight, Text Size, Text Color, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Button Color, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Cursor:** Cursor Start (drag in viewer), Cursor Start Delay (s), Time To Reach The Button (s), Hold On The Button (s), Click Delay After Arrival (s), Move Style, Path Arc, Cursor Size, Ripple Radius, Ripple Duration (s), Cursor Fade In (s), Cursor Fade Out (s), Cursor Color, Ripple Color
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ClickDemo_Neon

73 published controls.

- **Button:** Button Text, Font, Weight, Text Size, Text Color, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Button Color, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Cursor:** Cursor Start (drag in viewer), Cursor Start Delay (s), Time To Reach The Button (s), Hold On The Button (s), Click Delay After Arrival (s), Move Style, Path Arc, Cursor Size, Ripple Radius, Ripple Duration (s), Cursor Fade In (s), Cursor Fade Out (s), Cursor Color, Ripple Color
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ClickDemo_Soft

73 published controls.

- **Button:** Button Text, Font, Weight, Text Size, Text Color, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Button Color, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Cursor:** Cursor Start (drag in viewer), Cursor Start Delay (s), Time To Reach The Button (s), Hold On The Button (s), Click Delay After Arrival (s), Move Style, Path Arc, Cursor Size, Ripple Radius, Ripple Duration (s), Cursor Fade In (s), Cursor Fade Out (s), Cursor Color, Ripple Color
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ProgressBar

53 published controls.

- **Progress:** Progress (0-1), Font, Label Size, Label Color, Length, Thickness (px @1920), Center X, Center Y, Angle, Progress Color, Track Color
- **Motion:** In Delay (s), In Duration (s), Index, Stagger (s), Clip Length (s, 0=auto), In Engine, In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay, Enable Out, Out Offset (s), Out Duration (s)
- **In Motion:** In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg)
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_ProgressRing

53 published controls.

- **Progress:** Progress (0-1), Font, Label Size, Label Color, Diameter, Thickness (px @1920), Center X, Center Y, Angle, Progress Color, Track Color
- **Motion:** In Delay (s), In Duration (s), Index, Stagger (s), Clip Length (s, 0=auto), In Engine, In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay, Enable Out, Out Offset (s), Out Duration (s)
- **In Motion:** In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg)
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_StatCard

75 published controls.

- **Number:** Target Value, Decimals, Thousands Separator, Prefix (e.g. $), Suffix (e.g. % or K), Weight, Number Font, Number Size, Number Color
- **Count:** Count Delay (s), Count Duration (s), Count Engine, Spring Stiffness, Spring Damping, Overshoot
- **Caption:** Caption, Caption Size, Caption Color
- **Card:** Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_StatCard_Glass

75 published controls.

- **Number:** Target Value, Decimals, Thousands Separator, Prefix (e.g. $), Suffix (e.g. % or K), Weight, Number Font, Number Size, Number Color
- **Count:** Count Delay (s), Count Duration (s), Count Engine, Spring Stiffness, Spring Damping, Overshoot
- **Caption:** Caption, Caption Size, Caption Color
- **Card:** Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_StatCard_Neon

75 published controls.

- **Number:** Target Value, Decimals, Thousands Separator, Prefix (e.g. $), Suffix (e.g. % or K), Weight, Number Font, Number Size, Number Color
- **Count:** Count Delay (s), Count Duration (s), Count Engine, Spring Stiffness, Spring Damping, Overshoot
- **Caption:** Caption, Caption Size, Caption Color
- **Card:** Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_StatCard_Soft

75 published controls.

- **Number:** Target Value, Decimals, Thousands Separator, Prefix (e.g. $), Suffix (e.g. % or K), Weight, Number Font, Number Size, Number Color
- **Count:** Count Delay (s), Count Duration (s), Count Engine, Spring Stiffness, Spring Damping, Overshoot
- **Caption:** Caption, Caption Size, Caption Color
- **Card:** Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_TextLetter

23 published controls.

- **Text:** Text, Font, Weight, Size, Text Color, Position
- **Motion:** Order, In Delay (s), In Duration (s), Stagger (s per letter / word / line), Engine, Spring Stiffness, Spring Damping, Overshoot
- **Look:** Opacity At Start, Slide Distance (frac of width), Slide Angle (direction of start offset), Scale At Start, Rotation At Start (deg), Blur At Start
- **Out:** Enable Out, Out Offset (s), Out Duration (s)

### SMK2_TextLine

23 published controls.

- **Text:** Text, Font, Weight, Size, Text Color, Position
- **Motion:** Order, In Delay (s), In Duration (s), Stagger (s per letter / word / line), Engine, Spring Stiffness, Spring Damping, Overshoot
- **Look:** Opacity At Start, Slide Distance (frac of width), Slide Angle (direction of start offset), Scale At Start, Rotation At Start (deg), Blur At Start
- **Out:** Enable Out, Out Offset (s), Out Duration (s)

### SMK2_TextWord

23 published controls.

- **Text:** Text, Font, Weight, Size, Text Color, Position
- **Motion:** Order, In Delay (s), In Duration (s), Stagger (s per letter / word / line), Engine, Spring Stiffness, Spring Damping, Overshoot
- **Look:** Opacity At Start, Slide Distance (frac of width), Slide Angle (direction of start offset), Scale At Start, Rotation At Start (deg), Blur At Start
- **Out:** Enable Out, Out Offset (s), Out Duration (s)

### SMK2_UIBlock

65 published controls.

- **Card:** Text, Font, Weight, Text Size, Text Color, Shape, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Angle, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Position, Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_UIBlock_Glass

65 published controls.

- **Card:** Text, Font, Weight, Text Size, Text Color, Shape, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Angle, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Position, Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_UIBlock_Neon

65 published controls.

- **Card:** Text, Font, Weight, Text Size, Text Color, Shape, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Angle, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Position, Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

### SMK2_UIBlock_Soft

65 published controls.

- **Card:** Text, Font, Weight, Text Size, Text Color, Shape, Width (frac of frame width), Height (frac of frame width), Corner Radius, Center X, Center Y, Angle, Fill, Fill Color, Fill Color B, Gradient Angle, Border Width (px @1920), Border Position, Border Color, Shadow Color, Shadow X, Shadow Y (down), Shadow Blur
- **Motion:** In Delay (s), In Duration (s), Enable Out, Out Offset (s), Out Duration (s), Index, Stagger (s), Clip Length (s, 0=auto)
- **In Motion:** In Engine, In Opacity At Offset, In Slide Distance, In Slide Angle, In Scale At Offset, In Rotation At Offset (deg), In Spring Stiffness, In Spring Damping, In Spring Mass, In Bezier x1, In Bezier y1, In Bezier x2, In Bezier y2, In Elastic Amplitude, In Elastic Period, In Overshoot, In Inertia Decay
- **Out Motion:** Out Engine, Out Opacity At Offset, Out Slide Distance, Out Slide Angle, Out Scale At Offset, Out Rotation At Offset (deg), Out Spring Stiffness, Out Spring Damping, Out Spring Mass, Out Bezier x1, Out Bezier y1, Out Bezier x2, Out Bezier y2, Out Elastic Amplitude, Out Elastic Period, Out Overshoot, Out Inertia Decay

## Playback speed

Fusion plays complex comps from its cache: the first pass is slower (each card is a GPU Fuse plus Text+, roughly 10-15 ms per card; a letter-by-letter title adds ~3 ms per letter), cached playback runs at full speed.
- **Edit page:** right-click the clip ▸ *Render Cache Fusion Output* ▸ *On*, and set *Playback ▸ Render Cache ▸ Smart*. Edit freely, play back smoothly.
- **Fusion page:** play once to fill the cache (or use proxy / lower display quality while building).
- Prefer the **Word** or **Line** text variants over **Letter** for long text; avoid many Look/Bloom/Reflection instances on frame-filling sources.
- Measured costs per tool: `docs/PERFORMANCE.md`.

## Known limits

See `docs/DEFERRED_WORK.md` in the repository. Viewer playback speed on the first (uncached) pass depends on your GPU; cached playback is much faster.
