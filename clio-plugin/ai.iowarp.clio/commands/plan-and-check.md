---
description: "Plan one section from the project's evidence and have an independent checker review the plan (WTF-P's plan-section workflow)."
argument-hint: "<section>"
workflow: plan-section
---
Plan section `$1` and have the plan checked with WTF-P's plan-section workflow (input
`section`: `$1`). Its records are under `.planning/sections/$1/`.

Then report the checker's verdict. The plan is approved only when the author says so;
record that with `wtfp_record`.
