#!/usr/bin/env python3
"""Validate the repository's Codex plugin and bundled skills."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing manifest: {MANIFEST.relative_to(ROOT)}")
    except json.JSONDecodeError as error:
        fail(f"Invalid plugin JSON: {error}")


def validate_manifest(data: dict) -> None:
    required = ("name", "version", "description", "author", "interface")
    for key in required:
        if not data.get(key):
            fail(f"Manifest field '{key}' is required")

    if data["name"] != "docker":
        fail("Manifest name must remain 'docker'")
    if not SEMVER.fullmatch(data["version"]):
        fail("Manifest version must be semantic versioning")
    if not data["author"].get("name"):
        fail("Manifest author.name is required")

    interface = data["interface"]
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not interface.get(key):
            fail(f"Manifest interface.{key} is required")

    prompts = interface.get("defaultPrompt", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        fail("Manifest interface.defaultPrompt must contain one to three prompts")
    if any(not isinstance(prompt, str) or len(prompt) > 128 for prompt in prompts):
        fail("Every default prompt must be a string of at most 128 characters")

    for field in ("skills", "mcpServers", "apps"):
        value = data.get(field)
        if isinstance(value, str):
            target = (ROOT / value).resolve()
            if ROOT not in target.parents and target != ROOT:
                fail(f"Manifest path '{field}' escapes the repository")
            if not target.exists():
                fail(f"Manifest path '{field}' does not exist: {value}")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if "[TODO:" in text:
        fail(f"Placeholder remains in {path.relative_to(ROOT)}")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(f"Missing YAML frontmatter in {path.relative_to(ROOT)}")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"Unclosed YAML frontmatter in {path.relative_to(ROOT)}")

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if not separator:
            fail(f"Invalid frontmatter line in {path.relative_to(ROOT)}: {line}")
        metadata[key.strip()] = value.strip().strip("\"'")
    return metadata


def validate_skills(data: dict) -> None:
    skills_dir = ROOT / data.get("skills", "./skills/")
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        fail("No skills were found")

    for skill_file in skill_files:
        metadata = parse_frontmatter(skill_file)
        name = metadata.get("name", "")
        if not SKILL_NAME.fullmatch(name):
            fail(f"Invalid skill name in {skill_file.relative_to(ROOT)}")
        if skill_file.parent.name != name:
            fail(f"Skill folder must match its name: {name}")
        if not metadata.get("description"):
            fail(f"Skill description is required in {skill_file.relative_to(ROOT)}")

        agent_metadata = skill_file.parent / "agents" / "openai.yaml"
        if not agent_metadata.is_file():
            fail(f"Missing agent metadata: {agent_metadata.relative_to(ROOT)}")
        if f"${name}" not in agent_metadata.read_text(encoding="utf-8"):
            fail(f"Default prompt must reference ${name} in {agent_metadata.relative_to(ROOT)}")

        skill_text = skill_file.read_text(encoding="utf-8")
        for linked_path in re.findall(r"\]\(([^)]+)\)", skill_text):
            if "://" in linked_path or linked_path.startswith("#"):
                continue
            target = (skill_file.parent / linked_path).resolve()
            if skill_file.parent not in target.parents:
                fail(f"Skill link escapes its directory: {linked_path}")
            if not target.is_file():
                fail(f"Broken skill resource link: {skill_file.relative_to(ROOT)} -> {linked_path}")
        for reference in sorted((skill_file.parent / "references").glob("*.md")):
            relative_reference = reference.relative_to(skill_file.parent).as_posix()
            if relative_reference not in skill_text:
                fail(f"Bundled reference is not linked by the skill: {relative_reference}")
        for script in sorted((skill_file.parent / "scripts").glob("*.py")):
            relative_script = script.relative_to(skill_file.parent).as_posix()
            if relative_script not in skill_text:
                fail(f"Bundled script is not referenced by the skill: {relative_script}")
            try:
                ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            except SyntaxError as error:
                fail(f"Invalid Python in {script.relative_to(ROOT)}: {error}")


def main() -> int:
    try:
        manifest = load_manifest()
        validate_manifest(manifest)
        validate_skills(manifest)
    except ValueError as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1

    print("Plugin validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
