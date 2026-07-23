#!/usr/bin/env python3
"""Generate a conservative Compose operations overlay to stdout."""

from __future__ import annotations

import argparse
import re


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--cpus", default="0.50")
    parser.add_argument("--memory", default="512m")
    parser.add_argument("--otel-endpoint")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?", args.service):
        parser.error("--service must be a lowercase Compose service name")
    if any("\n" in value or "\r" in value for value in (args.cpus, args.memory)):
        parser.error("resource values must be single-line")

    environment = ""
    if args.otel_endpoint:
        if "\n" in args.otel_endpoint or "\r" in args.otel_endpoint:
            parser.error("--otel-endpoint must be single-line")
        environment = f"""
    environment:
      OTEL_EXPORTER_OTLP_ENDPOINT: {args.otel_endpoint}
      OTEL_RESOURCE_ATTRIBUTES: service.name={args.service}"""
    print(f"""services:
  {args.service}:
    cpus: "{args.cpus}"
    mem_limit: {args.memory}
    init: true
    stop_grace_period: 30s
    restart: unless-stopped
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"{environment}
""", end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
