#!/usr/bin/env python3
"""Perform a conservative static audit of Docker and Compose text files."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


DOCKER_NAMES = {"dockerfile", "compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"}
RULES = (
    ("high", "privileged-container", re.compile(r"^\s*privileged\s*:\s*true\b", re.I), "Avoid privileged mode unless explicitly required."),
    ("high", "docker-socket-mount", re.compile(r"/var/run/docker\.sock"), "Avoid granting access to the Docker daemon."),
    ("high", "possible-secret", re.compile(r"^\s*(?:ARG|ENV)\s+.*(?:PASSWORD|SECRET|TOKEN|PRIVATE_KEY)", re.I), "Do not persist secrets in image metadata."),
    ("high", "copied-env-file", re.compile(r"^\s*(?:ADD|COPY)\s+.*(?:/)?\.env(?:\s|$)", re.I), "Do not copy environment secret files into images."),
    ("high", "compose-secret-literal", re.compile(r"^\s*(?:password|secret|token|api_key)\s*:\s*(?!\s*(?:\$\{|$))", re.I), "Inject secrets at runtime instead of committing literals."),
    ("medium", "root-runtime", re.compile(r"^\s*USER\s+(?:root|0)\s*$", re.I), "Use a non-root runtime user when possible."),
    ("medium", "latest-tag", re.compile(r"^\s*FROM\s+\S+:latest(?:\s|$)", re.I), "Pin an explicit base-image version."),
    ("medium", "host-network", re.compile(r"^\s*network_mode\s*:\s*[\"']?host", re.I), "Avoid host networking unless required."),
    ("medium", "broad-capabilities", re.compile(r"^\s*cap_add\s*:\s*(?:\[)?\s*(?:ALL|SYS_ADMIN)", re.I), "Grant only the minimum Linux capabilities."),
    ("low", "shell-form-cmd", re.compile(r"^\s*(?:CMD|ENTRYPOINT)\s+(?!\[)", re.I), "Prefer exec form for predictable signal handling."),
    ("low", "remote-add", re.compile(r"^\s*ADD\s+https?://", re.I), "Prefer an explicit download with integrity verification."),
)


def candidates(root: Path) -> list[Path]:
    paths: list[Path] = []
    skipped = {".git", "node_modules", ".venv", "vendor", "dist", "build", "target"}
    for current, dirs, names in os.walk(root):
        dirs[:] = [directory for directory in dirs if directory not in skipped]
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.name.lower() in DOCKER_NAMES or path.name.lower().startswith("dockerfile."):
                paths.append(path)
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")

    docker_files = candidates(root)
    findings = []
    for path in docker_files:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for severity, rule, pattern, guidance in RULES:
                if pattern.search(line):
                    findings.append({
                        "severity": severity,
                        "rule": rule,
                        "file": path.relative_to(root).as_posix(),
                        "line": number,
                        "guidance": guidance,
                    })

    if args.as_json:
        print(json.dumps({
            "files_scanned": [path.relative_to(root).as_posix() for path in docker_files],
            "findings": findings,
        }, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding['severity'].upper():6} {finding['file']}:{finding['line']} {finding['rule']} — {finding['guidance']}")
    elif docker_files:
        print("No heuristic findings.")
    else:
        print("No Docker configuration found; nothing audited.")
    return 1 if any(item["severity"] == "high" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
