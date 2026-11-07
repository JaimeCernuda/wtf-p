---
description: "Draft one approved section and have an independent reviewer check it (WTF-P's draft-review workflow)."
argument-hint: "<section>"
workflow: draft-review
---
Draft and review section `$1` with WTF-P's draft-review workflow (input `section`: `$1`).
Its plan and records are under `.planning/sections/$1/`.

If the section has no approved plan yet, say so and stop: run `/wtfp:plan-section $1` first.
After the run, report the reviewer's findings by priority and reconcile the section and
state records with `wtfp_record`.
