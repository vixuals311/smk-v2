# Clean-room and licence review

**Scope:** every file shipped in the release zip (Fuses, macros, installer, manual).

| Area | Finding |
|---|---|
| Origin of code | All Lua, GPU kernels, reference pixel functions, generators and tests were written for this repo. The v1 repo's code is not reused in v2 Fuses. |
| NeoEdit bundle | Studied only as black-box behaviour (control list, look of the result) for ideas: bevel/emboss, reflection, paper curl, glow. No node graph, expression, code, control wording/layout, icon, link or asset was copied. The only source with an embedded external URL/button code in the studied files (tutorial / contact buttons) is deliberately **not** reproduced. |
| Algorithms | Relief: Gaussian-derivative gradient gather. Reflection: mirror + distance-growing blur + sine ripple. Page Curl: analytic cylinder-roll model with four layers. Bloom: 4x4 tent pyramid + bilinear sum. All are textbook techniques written from first principles. |
| Names | Product names are `SMK2 …`; none uses the "Neo" name or branding. A test (`tests/test_release.py`) fails the build if "Neo" appears in shipped files. |
| Third-party runtime code | None is bundled. The release is plain `.fuse` / `.setting` text plus a Python installer using only the standard library. |
| Trademarks | "DaVinci Resolve" / "Fusion" are Blackmagic Design marks, used descriptively; `NOTICE` states there is no affiliation. |
| Open items | Choose and add a licence (`LICENSE`) before public distribution: the owner decides (proprietary EULA vs. permissive). Until then `NOTICE` says "all rights reserved". |
