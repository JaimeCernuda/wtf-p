---
description: "Plan one section from the project's evidence and have an independent checker review the plan (WTF-P's plan-section playbook)."
argument-hint: "<section>"
---
Run WTF-P's plan-and-check playbook for section `$1` with `run_workflow`, using these
arguments:

```json
{
  "workflow": {
    "steps": [
      {
        "id": "plan",
        "target": "wtfp-section-planner",
        "input": "Create one contained, immutable plan for section $1 from the portable project state. Write only the plan artifact under .planning/sections/$1/plans/. $task"
      },
      {
        "id": "check",
        "target": "wtfp-plan-checker",
        "after": ["plan"],
        "input": "Independently check the plan for section $1: traceability, support for every claim, and fit to the outline and venue. Do not change it. The planner reported: $plan"
      }
    ]
  },
  "task": "Section $1. Its records are under .planning/sections/$1/."
}
```

Then report the checker's verdict. The plan is approved only when the author says so;
record that with `wtfp_record`.
