---
description: "Draft one approved section and have an independent reviewer check it (WTF-P's draft-review playbook)."
argument-hint: "<section>"
---
Run WTF-P's draft-and-review playbook for section `$1` with `run_workflow`, using these
arguments (the task is section `$1` and where its approved plan is):

```json
{
  "workflow": {
    "steps": [
      {
        "id": "draft",
        "target": "wtfp-section-writer",
        "input": "Draft section $1 from its explicitly approved plan into its declared paper artifact (paper/sections/$1.tex) and update only its declared summary. $task"
      },
      {
        "id": "review",
        "target": "wtfp-section-reviewer",
        "after": ["draft"],
        "input": "Independently review section $1 as drafted against its plan, sources, decisions and venue constraints. Do not claim or make any change. The draft step reported: $draft"
      }
    ]
  },
  "task": "Section $1. Its plan and records are under .planning/sections/$1/."
}
```

If the section has no approved plan yet, say so and stop: run `/wtfp:plan-section $1` first.
After the run, report the reviewer's findings by priority and reconcile the section and
state records with `wtfp_record`.
