#!/usr/bin/env python3
"""Generate minimal devcontainer or Kubernetes starter assets to stdout."""

from __future__ import annotations

import argparse
import json
import re


def devcontainer(name: str, image: str) -> str:
    data = {
        "name": name,
        "image": image,
        "remoteUser": "vscode",
        "customizations": {"vscode": {"extensions": []}},
    }
    return json.dumps(data, indent=2) + "\n"


def kubernetes(name: str, image: str, port: int, health_path: str | None) -> str:
    probes = ""
    if health_path:
        probes = f"""
          startupProbe:
            httpGet:
              path: {health_path}
              port: http
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet:
              path: {health_path}
              port: http
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: {health_path}
              port: http
            periodSeconds: 10"""
    return f"""# REVIEW: confirm resources, writable paths, service account, rollout policy, and probes.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: {name}
          image: {image}
          ports:
            - name: http
              containerPort: {port}
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              memory: 256Mi{probes}
---
apiVersion: v1
kind: Service
metadata:
  name: {name}
spec:
  selector:
    app: {name}
  ports:
    - name: http
      port: {port}
      targetPort: {port}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="asset", required=True)
    dev = sub.add_parser("devcontainer")
    dev.add_argument("--name", required=True)
    dev.add_argument("--image", default="mcr.microsoft.com/devcontainers/base:ubuntu-24.04")
    dev.add_argument("--port", type=int)
    kube = sub.add_parser("kubernetes")
    kube.add_argument("--name", required=True)
    kube.add_argument("--image", required=True)
    kube.add_argument("--port", type=int, required=True)
    kube.add_argument("--health-path")
    kube.add_argument("--allow-tag", action="store_true")
    args = parser.parse_args()

    if args.asset == "devcontainer":
        content = json.loads(devcontainer(args.name, args.image))
        if args.port:
            if not 1 <= args.port <= 65535:
                parser.error("--port must be between 1 and 65535")
            content["forwardPorts"] = [args.port]
        print(json.dumps(content, indent=2))
    else:
        if not re.fullmatch(r"[a-z0-9](?:[-a-z0-9]*[a-z0-9])?", args.name) or len(args.name) > 63:
            parser.error("--name must be a valid Kubernetes DNS label")
        if "\n" in args.image or "\r" in args.image or not args.image.strip():
            parser.error("--image must be a single non-empty reference")
        canonical_digest = re.search(r"@sha256:[0-9a-fA-F]{64}$", args.image)
        if "@" in args.image and not canonical_digest:
            parser.error("only canonical sha256 image digests are supported")
        if not canonical_digest and not args.allow_tag:
            parser.error("production Kubernetes assets require image@sha256:<64 hex>; use --allow-tag only for a draft")
        if args.health_path and (not args.health_path.startswith("/") or "\n" in args.health_path or "\r" in args.health_path):
            parser.error("--health-path must be a single absolute URL path")
        if not 1 <= args.port <= 65535:
            parser.error("--port must be between 1 and 65535")
        print(kubernetes(args.name, args.image, args.port, args.health_path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
