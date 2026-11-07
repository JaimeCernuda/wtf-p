"""WTF-P's project records, written and measured by CLIO tools.

`wtfp_record` is the one writer of a portable `.planning/` record: the record's type and
id must match its logical URI, the revision the caller read must still be current, and
the record must validate against the plugin's own schema before it replaces the file.
`wtfp_measure_section` counts a section's words in its manuscript file (LaTeX or
Markdown) and records the count on the section and on the project state.

Both take the project root, the folder that holds `.planning/`, normally the workspace.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clio_agent.sdk import tool

SCHEMAS = Path(__file__).resolve().parents[2] / "project" / "schemas"
_ID = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
#: Logical URI -> record type and project-relative file (the adapter mapping of project/README.md).
ROUTES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"^project://manifest$"), "manifest", ".planning/project.json"),
    (re.compile(r"^project://config$"), "config", ".planning/config.json"),
    (re.compile(r"^project://state$"), "state", ".planning/state.json"),
    (re.compile(r"^project://decisions$"), "decisions", ".planning/decisions.json"),
    (re.compile(r"^project://structure/outline$"), "outline", ".planning/structure/outline.json"),
    (re.compile(rf"^project://sections/({_ID})$"), "section", ".planning/sections/{}/section.json"),
    (re.compile(rf"^project://sources/({_ID})$"), "source", ".planning/sources/{}.json"),
    (re.compile(rf"^project://evidence/({_ID})$"), "evidence", ".planning/evidence/{}.json"),
    (
        re.compile(rf"^project://checkpoints/({_ID})$"),
        "checkpoint",
        ".planning/checkpoints/{}.json",
    ),
    (
        re.compile(rf"^project://validations/({_ID})$"),
        "validation",
        ".planning/validations/{}.json",
    ),
]
REVISIONED = {"state", "outline", "decisions"}
STAMPED = {"state", "outline", "decisions", "manifest", "section"}


class RecordError(ValueError):
    """A record that cannot be written as asked, with the reason the agent can act on."""


def _root(project_root: str) -> Path:
    root = Path(project_root).expanduser().resolve()
    if not root.is_dir():
        raise RecordError(f"{project_root} is not a folder")
    return root


def _read(root: Path, relative: str) -> dict[str, Any] | None:
    try:
        value = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _schema_errors(record: dict[str, Any], record_type: str) -> list[str]:
    from jsonschema import Draft202012Validator  # noqa: PLC0415
    from referencing import Registry, Resource  # noqa: PLC0415

    resources = []
    for path in SCHEMAS.glob("*.schema.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(schema)
        resources += [(path.name, resource), (str(schema.get("$id") or path.name), resource)]
    registry = Registry().with_resources(resources)
    schema = json.loads((SCHEMAS / f"{record_type}.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, registry=registry)
    return [
        f"{'/'.join(str(p) for p in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
    ]


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_atomic(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def _route(uri: str) -> tuple[str, str, re.Match[str]]:
    for pattern, record_type, template in ROUTES:
        match = pattern.match(uri)
        if match:
            return record_type, template, match
    raise RecordError(f"{uri} is not a logical record URI this plugin maps")


def write_record(
    project_root: str, uri: str, record: dict[str, Any], expect_revision: int | None = None
) -> tuple[str, int | None]:
    """Validate and write one record; return its project-relative file and revision."""

    root = _root(project_root)
    record_type, template, match = _route(uri)
    ident = match.group(1) if match.groups() else ""
    if record.get("schema") != f"wtfp.project.{record_type}/v1":
        raise RecordError(f"{uri} holds wtfp.project.{record_type}/v1 records")
    if ident and record.get("id") != ident:
        raise RecordError(f"{uri} must hold the record whose id is {ident}")
    relative = template.format(ident)
    manifest = _read(root, ".planning/project.json")
    project_id = record.get("id") if record_type == "manifest" else record.get("project_id")
    if manifest and isinstance(manifest.get("id"), str) and project_id != manifest["id"]:
        raise RecordError(f"{uri} belongs to project {project_id}, not {manifest['id']}")
    existing = _read(root, relative)
    out = dict(record)
    revision: int | None = None
    if record_type in REVISIONED:
        current = existing.get("revision") if existing else None
        current = current if isinstance(current, int) else None
        if current is not None and expect_revision is not None and expect_revision != current:
            raise RecordError(
                f"{uri} is at revision {current}, not {expect_revision}; read it again before writing"
            )
        given = record.get("revision")
        revision = (given if isinstance(given, int) else 0) if current is None else current + 1
        out["revision"] = revision
    if record_type in STAMPED:
        out["updated_at"] = _now()
    errors = _schema_errors(out, record_type)
    if errors:
        raise RecordError(f"{uri} does not validate: " + "; ".join(errors[:8]))
    _write_atomic(root / relative, out)
    return relative, revision


@tool(name="wtfp_record")
def wtfp_record(
    project_root: str, uri: str, record_json: str, expect_revision: int | None = None
) -> str:
    """Write one WTF-P project record (project://manifest, project://sections/<id>, ...).

    `record_json` is the whole record as JSON. It must carry its `schema`
    (`wtfp.project.<type>/v1`) and, for an identified record, the id in the URI. For
    state, outline and decisions, pass the revision you read as `expect_revision`; a
    newer revision on disk refuses the write. The record is schema-validated before it
    replaces the file, and its revision and `updated_at` follow from the write.
    """

    try:
        record = json.loads(record_json)
    except ValueError as exc:
        return f"Not written: record_json is not JSON ({exc})."
    if not isinstance(record, dict):
        return "Not written: record_json must be a JSON object."
    try:
        relative, revision = write_record(project_root, uri, record, expect_revision)
    except RecordError as exc:
        return f"Not written: {exc}."
    at = f", revision {revision}" if revision is not None else ""
    return f"Wrote {uri} to {relative}{at}; it validates against its schema."


_TEX_DROP = re.compile(r"\\(?:begin|end)\{[^}]*\}|\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?|[{}$~^_&#]")


def count_words(text: str, *, latex: bool) -> int:
    """Words a reader sees: LaTeX comments, commands and markup do not count."""

    if latex:
        text = re.sub(r"(?<!\\)%.*", "", text)
        text = re.sub(r"\\(?:cite|ref|label|eqref|autoref|cref)\*?\{[^}]*\}", "", text)
        text = _TEX_DROP.sub(" ", text)
    else:
        text = re.sub(r"\[@[^\]]*\]", "", text)
        text = re.sub(r"[#*_`>|]", " ", text)
    return len([w for w in text.split() if re.search(r"\w", w)])


@tool(name="wtfp_measure_section")
def wtfp_measure_section(project_root: str, section: str, manuscript: str = "") -> str:
    """Count a section's words in its manuscript file and record the count.

    `manuscript` is the section's file relative to the project root (for example
    `paper/sections/introduction.tex`); when omitted it is read from the section
    record's manuscript artifact. The count goes on the section record's `word_count`
    and the project state's `progress.word_count` (the sum over measured sections).
    """

    try:
        root = _root(project_root)
    except RecordError as exc:
        return f"Not measured: {exc}."
    uri = f"project://sections/{section}"
    record = _read(root, f".planning/sections/{section}/section.json")
    if record is None:
        return f"Not measured: .planning/sections/{section}/section.json does not exist yet."
    artifacts = record.get("artifacts") if isinstance(record.get("artifacts"), dict) else {}
    target = manuscript or str(artifacts.get("manuscript") or "").removeprefix("project://")
    if not target:
        return f"Not measured: name the manuscript file; {uri} records none."
    path = (root / target).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return f"Not measured: {target} is not a file in the project."
    words = count_words(path.read_text(encoding="utf-8"), latex=path.suffix == ".tex")
    try:
        write_record(project_root, uri, {**record, "word_count": words})
        total = 0
        for other in (root / ".planning" / "sections").glob("*/section.json"):
            value = _read(root, str(other.relative_to(root)))
            total += int((value or {}).get("word_count") or 0)
        state = _read(root, ".planning/state.json")
        if state and isinstance(state.get("progress"), dict):
            write_record(
                project_root,
                "project://state",
                {**state, "progress": {**state["progress"], "word_count": total}},
            )
    except RecordError as exc:
        return f"Counted {words} words in {target}, but the count was not recorded: {exc}."
    goal = record.get("word_target")
    of = f" of a {goal}-word target" if isinstance(goal, int) and goal else ""
    return f"{section}: {words} words{of} in {target}; the paper's measured sections total {total}."
