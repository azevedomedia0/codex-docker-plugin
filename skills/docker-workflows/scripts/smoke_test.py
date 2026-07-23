#!/usr/bin/env python3
"""Plan or execute an isolated Docker Compose smoke test without deleting volumes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def run(command: list[str], cwd: Path, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=capture)


def service_ready(output: str) -> bool:
    try:
        parsed = json.loads(output)
        rows = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        rows = []
        for line in output.splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not rows:
        return False
    for row in rows:
        state = str(row.get("State", "")).lower()
        health = str(row.get("Health", "")).lower()
        if state != "running" or (health and health != "healthy"):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--service", required=True)
    parser.add_argument("--url")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")
    if not 5 <= args.timeout <= 600:
        parser.error("--timeout must be between 5 and 600 seconds")

    project_name = f"codex-smoke-{hashlib.sha256(str(root).encode()).hexdigest()[:10]}"
    compose = ["docker", "compose", "--project-name", project_name]
    plan = {
        "project": str(root),
        "compose_project": project_name,
        "service": args.service,
        "url": args.url,
        "commands": [
            compose + ["config", "--quiet"],
            compose + ["up", "--detach", args.service],
            compose + ["ps", args.service],
            compose + ["down", "--remove-orphans"],
        ],
        "removes_volumes": False,
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return 0

    if run(compose + ["config", "--quiet"], root).returncode:
        return 1

    started = False
    try:
        started = True
        if run(compose + ["up", "--detach", args.service], root).returncode:
            return 1
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            if args.url:
                try:
                    with urllib.request.urlopen(args.url, timeout=3) as response:
                        if 200 <= response.status < 400:
                            print(f"Smoke test passed: HTTP {response.status}")
                            return 0
                except (urllib.error.URLError, TimeoutError):
                    pass
            else:
                result = run(compose + ["ps", "--format", "json", args.service], root, capture=True)
                if result.returncode == 0 and service_ready(result.stdout):
                    print("Smoke test passed: service is running")
                    return 0
            time.sleep(2)

        print("Smoke test timed out.", file=sys.stderr)
        run(compose + ["ps"], root)
        run(compose + ["logs", "--no-color", "--tail", "200", args.service], root)
        return 1
    finally:
        if started:
            run(compose + ["down", "--remove-orphans"], root)


if __name__ == "__main__":
    raise SystemExit(main())
