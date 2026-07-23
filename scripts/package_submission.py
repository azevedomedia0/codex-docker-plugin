#!/usr/bin/env python3
"""Build the skills-only marketplace submission ZIP."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "docker-plugin-1.0.0.zip"
INCLUDE = (
    ".codex-plugin",
    "assets",
    "skills",
    "LICENSE",
    "README.md",
    "PRIVACY.md",
    "TERMS.md",
)


def main() -> int:
    manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest["name"] != "docker" or manifest["version"] != "1.0.0":
        raise SystemExit("Expected docker plugin version 1.0.0")

    DIST.mkdir(exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in INCLUDE:
            path = ROOT / item
            if path.is_dir():
                for file in sorted(path.rglob("*")):
                    if file.is_file() and "__pycache__" not in file.parts:
                        archive.write(file, Path("docker") / file.relative_to(ROOT))
            elif path.is_file():
                archive.write(path, Path("docker") / path.relative_to(ROOT))
            else:
                raise SystemExit(f"Missing submission file: {item}")

    if OUTPUT.stat().st_size > 100 * 1024 * 1024:
        raise SystemExit("Submission ZIP exceeds 100 MB")
    if shutil.which("unzip"):
        print(f"Created {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
