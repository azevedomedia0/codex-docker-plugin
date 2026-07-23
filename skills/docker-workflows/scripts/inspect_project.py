#!/usr/bin/env python3
"""Produce a bounded, read-only inventory of a project's containerization signals."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


MARKERS = {
    "node": ("package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json", "bun.lockb"),
    "python": ("pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock", "uv.lock"),
    "go": ("go.mod", "go.sum"),
    "rust": ("Cargo.toml", "Cargo.lock"),
    "java": ("pom.xml", "build.gradle", "build.gradle.kts", "gradlew"),
    "ruby": ("Gemfile", "Gemfile.lock"),
    "php": ("composer.json", "composer.lock"),
}
FRAMEWORK_MARKERS = {
    "nextjs": ("next.config.js", "next.config.mjs", "next.config.ts"),
    "django": ("manage.py",),
    "rails": ("config/application.rb",),
}
DOCKER_NAMES = {
    "dockerfile",
    "dockerfile.dev",
    "dockerfile.prod",
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
    ".dockerignore",
}
SOURCE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
}
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", ".venv", "venv", "dist", "build", "target", "__pycache__"}


def relative_files(root: Path, max_depth: int) -> list[str]:
    files: list[str] = []
    for current, dirs, names in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        dirs[:] = sorted(directory for directory in dirs if directory not in SKIP_DIRS and depth < max_depth)
        for name in sorted(names):
            path = current_path / name
            files.append(path.relative_to(root).as_posix())
    return files


def matches(files: list[str], markers: tuple[str, ...]) -> list[str]:
    marker_set = {marker.lower() for marker in markers}
    return [path for path in files if Path(path).name.lower() in marker_set]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--max-depth", type=int, default=4)
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")
    if not 1 <= args.max_depth <= 12:
        parser.error("--max-depth must be between 1 and 12")

    files = relative_files(root, args.max_depth)
    runtimes = {name: found for name, markers in MARKERS.items() if (found := matches(files, markers))}
    frameworks = {name: found for name, markers in FRAMEWORK_MARKERS.items() if (found := matches(files, markers))}
    docker = [path for path in files if Path(path).name.lower() in DOCKER_NAMES or Path(path).name.lower().startswith("dockerfile.")]
    ci = [path for path in files if path.startswith(".github/workflows/") or path in {".gitlab-ci.yml", "Jenkinsfile"}]
    source_languages: dict[str, int] = {}
    for path in files:
        language = SOURCE_EXTENSIONS.get(Path(path).suffix.lower())
        if language:
            source_languages[language] = source_languages.get(language, 0) + 1

    print(json.dumps({
        "project": str(root),
        "runtimes": runtimes,
        "frameworks": frameworks,
        "source_language_signals": source_languages,
        "docker_files": docker,
        "ci_files": ci,
        "environment_examples": [path for path in files if Path(path).name in {".env.example", ".env.sample", "example.env"}],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
