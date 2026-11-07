"""WTF-P's eleven roles as CLIO subagents.

Each role's prompt is its WTF-P role text. A read-only role (it reads and judges,
and never writes) runs under CLIO's read-only profile. Writing roles get the
workspace and LaTeX tools; the write guard confines their manuscript writes.
"""

from clio_agent.sdk import PromptFile, Subagent

wtfp_argument_verifier = Subagent(
    "wtfp-argument-verifier",
    prompt=PromptFile("prompt/subagents/wtfp_argument_verifier.md"),
    description="Verify that completed section text actually delivers the claims, evidence, constraints, and connections promised by its plan. Execution summaries are navigation aids, not proof; verdicts must be grounded in the manuscript itself.",
    plugins=["workspace"],
    effects="read",
    max_iters=40,
)

wtfp_citation_expert = Subagent(
    "wtfp-citation-expert",
    prompt=PromptFile("prompt/subagents/wtfp_citation_expert.md"),
    description="Find a precise, defensible set of sources for explicit manuscript claims and analyze whether the existing bibliography covers the approved argument. Every recommendation must be grounded in resolvable scholarly metadata and its relevance must be explained at claim level.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_citation_formatter = Subagent(
    "wtfp-citation-formatter",
    prompt=PromptFile("prompt/subagents/wtfp_citation_formatter.md"),
    description="Audit bibliography integrity and produce deterministic corrections without touching the primary bibliography. The role cross-references manuscript citation keys, detects missing and unused entries, identifies likely duplicates, and normalizes records while preserving meaning and capitalization.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_coherence_checker = Subagent(
    "wtfp-coherence-checker",
    prompt=PromptFile("prompt/subagents/wtfp_coherence_checker.md"),
    description="Evaluate the manuscript as a connected argument rather than a set of individually acceptable sections. Detect terminology drift, orphan or unsupported claims, broken narrative transitions, invalid cross-references, and contradictions across the document.",
    plugins=["workspace"],
    effects="read",
    max_iters=40,
)

wtfp_outliner = Subagent(
    "wtfp-outliner",
    prompt=PromptFile("prompt/subagents/wtfp_outliner.md"),
    description="Turn the approved project brief into the structural foundation for an academic document. The role defines what each section must accomplish, how claims depend on one another, where evidence is needed, and which sections can be developed concurrently.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_plan_checker = Subagent(
    "wtfp-plan-checker",
    prompt=PromptFile("prompt/subagents/wtfp_plan_checker.md"),
    description="Determine whether proposed section plans are likely to produce the intended academic outcome. Verification is goal-backward: a syntactically complete plan still fails if it omits a claim, lacks usable evidence, contradicts an author decision, or cannot fit its budget.",
    plugins=["workspace"],
    effects="read",
    max_iters=40,
)

wtfp_prose_polisher = Subagent(
    "wtfp-prose-polisher",
    prompt=PromptFile("prompt/subagents/wtfp_prose_polisher.md"),
    description="Improve clarity, rhythm, concision, and authorial voice without changing technical meaning, evidence, citation placement, or argumentative direction. Polishing is a constrained transformation, not a substantive rewrite.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_research_synthesizer = Subagent(
    "wtfp-research-synthesizer",
    prompt=PromptFile("prompt/subagents/wtfp_research_synthesizer.md"),
    description="Investigate the literature needed to plan and write a specific section well. The output is an evidence-traceable synthesis of foundational and recent work, standard approaches, genuine gaps, positioning options, and concrete writing guidance—not a search-result dump.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_section_planner = Subagent(
    "wtfp-section-planner",
    prompt=PromptFile("prompt/subagents/wtfp_section_planner.md"),
    description="Convert one approved section goal into small, executable writing plans. A plan is a precise writing contract: it connects claims, evidence, word budgets, sequencing, author decisions, and measurable completion criteria without pre-writing the section.",
    plugins=["workspace", "latex"],
    max_iters=40,
)

wtfp_section_reviewer = Subagent(
    "wtfp-section-reviewer",
    prompt=PromptFile("prompt/subagents/wtfp_section_reviewer.md"),
    description="Review a section as an academic evaluator and produce prioritized, actionable feedback. The invocation may select a review lens—adversarial peer, significance-focused chair, production editor, or constructive mentor—without changing the underlying evidence standard.",
    plugins=["workspace"],
    effects="read",
    max_iters=40,
)

wtfp_section_writer = Subagent(
    "wtfp-section-writer",
    prompt=PromptFile("prompt/subagents/wtfp_section_writer.md"),
    description="Execute an approved section plan into evidence-grounded academic prose or the explicitly requested scaffold. Preserve the author’s epistemic authority, make only supported claims, and leave an auditable account of what was produced and what remains unresolved.",
    plugins=["workspace", "latex"],
    max_iters=40,
)
