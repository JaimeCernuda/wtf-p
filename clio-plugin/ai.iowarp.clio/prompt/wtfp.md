---
id: wtfp.method
section: domain
---
WTF-P writes a paper from evidence. Its state is validated JSON under `.planning/`; the
manuscript is the paper's LaTeX under `paper/` (one `paper/sections/<section>.tex` per
section), built with `latex_build`. The `/wtfp:*` commands are its actions and its roles
are subagents. Write records only with `wtfp_record`; count a section with
`wtfp_measure_section`. While a writing action runs, file writes are confined to `paper/`
and `.planning/`.
