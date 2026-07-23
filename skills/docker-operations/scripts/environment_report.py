#!/usr/bin/env python3
"""Report local container tooling without exposing environment values."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess


TOOLS = ("docker", "hadolint", "trivy", "grype", "syft", "cosign", "kubectl", "helm")


def command(args: list[str]) -> dict:
    result = subprocess.run(args, check=False, text=True, capture_output=True, timeout=10)
    return {
        "available": result.returncode == 0,
        "exit_code": result.returncode,
        "output": (result.stdout or result.stderr).strip()[:2000],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docker", action="store_true", help="Run read-only Docker CLI inspection")
    args = parser.parse_args()
    report = {
        "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "tools": {tool: shutil.which(tool) for tool in TOOLS},
    }
    if args.docker:
        if not shutil.which("docker"):
            report["docker"] = {"available": False, "reason": "docker CLI not found"}
        else:
            report["docker"] = {
                "version": command(["docker", "version", "--format", "{{json .}}"]),
                "compose": command(["docker", "compose", "version", "--short"]),
                "buildx": command(["docker", "buildx", "version"]),
                "context": command(["docker", "context", "show"]),
                "disk_usage": command(["docker", "system", "df"]),
            }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
