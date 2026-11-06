# WTF-P for CLIO

WTF-P's method as a CLIO plugin: its project records, its 36 actions as `/wtfp:*`
commands, its 7 skills, its 11 roles as subagents, and its write guard. "How to use
LaTeX" stays in CLIO's `latex` plugin, which this one requires: the manuscript is the
paper's LaTeX source under `paper/`, built with `latex_build` and its venue checks.

This folder is maintained by hand and is not emitted by `scripts/build-adapters.js`.
It started from `vendors/claude/` at `eff98baf` and replaces the Clio Coder pieces:

| WTF-P (Clio Coder) | Here |
| --- | --- |
| desk extension (`clio/`, `vendors/clio-extension/`) | not used |
| `extension_wtfp__record`, `extension_wtfp__measure_section` | `wtfp_record`, `wtfp_measure_section` (`ai.iowarp.clio/tools/records.py`) |
| playbooks `wtfp-draft-review`, `wtfp-plan-section` | declared workflows `draft-review` and `plan-section` (`ai.iowarp.clio/workflows/`), each with a `section` input; `@draft-review` and `/wtfp:draft-and-review <section>` reach the same declaration |
| roles (`agents/*.md`) | `ai.iowarp.clio/subagents/roles.py`; checker, reviewer and verifier roles run read-only |
| `export-latex` | builds the paper with `latex_build` |
| write guard (`hooks/hooks.json`, `scripts/`) | the same files, run on CLIO's Claude Code hook wire |

Install it from a CLIO marketplace that pins this repository, or directly:

```bash
clio-agent plugin check clio-plugin
```
