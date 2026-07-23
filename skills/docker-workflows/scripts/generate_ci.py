#!/usr/bin/env python3
"""Generate a conservative GitHub Actions workflow for Docker builds."""

from __future__ import annotations

import argparse
from pathlib import Path


def workflow(image_name: str, dockerfile: str, context: str, branch: str, publish: bool) -> str:
    permissions = "  contents: read\n  packages: write\n" if publish else "  contents: read\n"
    push = "${{ github.event_name == 'push' }}" if publish else "false"
    tags = f"ghcr.io/${{{{ github.repository_owner }}}}/{image_name}:sha-${{{{ github.sha }}}}"
    login = """
      - name: Log in to GHCR
        if: github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
""" if publish else ""
    return f"""name: Docker

on:
  pull_request:
  push:
    branches: ["{branch}"]

permissions:
{permissions}
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: docker/setup-buildx-action@v3
{login}      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: {context}
          file: {dockerfile}
          push: {push}
          tags: {tags}
          cache-from: type=gha
          cache-to: type=gha,mode=max
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-name", required=True)
    parser.add_argument("--project", default=".")
    parser.add_argument("--dockerfile", default="./Dockerfile")
    parser.add_argument("--context", default=".")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--publish-ghcr", action="store_true")
    parser.add_argument("--allow-missing", action="store_true", help="Generate even when the Dockerfile or context does not exist")
    parser.add_argument("--output")
    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()
    dockerfile = project / args.dockerfile
    context = project / args.context
    if not args.allow_missing:
        if not dockerfile.is_file():
            parser.error(f"Dockerfile does not exist: {dockerfile}")
        if not context.is_dir():
            parser.error(f"build context does not exist: {context}")
    content = workflow(args.image_name, args.dockerfile, args.context, args.branch, args.publish_ghcr)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(output)
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
