#!/usr/bin/env python3
"""Print a non-executing container supply-chain plan."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--compose")
    parser.add_argument("--context", default=".")
    parser.add_argument("--scanner", choices=("trivy", "grype", "scout"), default="trivy")
    parser.add_argument("--sbom", choices=("syft-spdx", "syft-cyclonedx", "trivy-cyclonedx"), default="syft-spdx")
    parser.add_argument("--sign", action="store_true")
    parser.add_argument("--verify-identity")
    parser.add_argument("--verify-issuer")
    args = parser.parse_args()
    security_target = args.image if "@sha256:" in args.image else "<resolved-image@sha256:digest>"

    scan = {
        "trivy": ["trivy", "image", "--severity", "HIGH,CRITICAL", "--exit-code", "1", security_target],
        "grype": ["grype", security_target, "--fail-on", "high"],
        "scout": ["docker", "scout", "cves", security_target],
    }[args.scanner]
    sbom = {
        "syft-spdx": ["syft", security_target, "-o", "spdx-json=sbom.spdx.json"],
        "syft-cyclonedx": ["syft", security_target, "-o", "cyclonedx-json=sbom.cdx.json"],
        "trivy-cyclonedx": ["trivy", "image", "--format", "cyclonedx", "--output", "sbom.cdx.json", security_target],
    }[args.sbom]
    steps = [
        {"operation": "dockerfile-lint", "command": ["hadolint", args.dockerfile], "mutates_remote": False},
        {"operation": "secret-scan", "command": ["trivy", "fs", "--scanners", "secret", "--exit-code", "1", args.context], "mutates_remote": False},
        {"operation": "misconfiguration-scan", "command": ["trivy", "config", "--severity", "HIGH,CRITICAL", "--exit-code", "1", args.context], "mutates_remote": False},
        {"operation": "scan", "command": scan, "mutates_remote": False, "blocked_by": None if "@sha256:" in args.image else "Resolve the published image digest."},
        {"operation": "image-secret-scan", "command": ["trivy", "image", "--scanners", "secret", "--exit-code", "1", security_target], "mutates_remote": False, "blocked_by": None if "@sha256:" in args.image else "Resolve the published image digest."},
        {"operation": "sbom", "command": sbom, "mutates_local": True, "output_artifact": "sbom.spdx.json or sbom.cdx.json", "blocked_by": None if "@sha256:" in args.image else "Resolve the published image digest."},
    ]
    if args.compose:
        steps.insert(1, {"operation": "compose-validation", "command": ["docker", "compose", "--file", args.compose, "config", "--quiet"], "mutates_remote": False})
    if args.sign:
        sign_target = security_target
        steps.append({
            "operation": "sign",
            "command": ["cosign", "sign", sign_target],
            "mutates_remote": True,
            "requires_authorization": True,
            "blocked_by": None if "@sha256:" in args.image else "Resolve the published image digest.",
        })
    if args.verify_identity or args.verify_issuer:
        if not args.verify_identity or not args.verify_issuer:
            parser.error("--verify-identity and --verify-issuer must be supplied together")
        verify_target = security_target
        steps.append({
            "operation": "verify-signature",
            "command": [
                "cosign", "verify", verify_target,
                "--certificate-identity", args.verify_identity,
                "--certificate-oidc-issuer", args.verify_issuer,
            ],
            "mutates_remote": False,
        })
        for predicate_type in ("slsaprovenance", "spdxjson"):
            steps.append({
                "operation": f"verify-{predicate_type}-attestation",
                "command": [
                    "cosign", "verify-attestation", verify_target,
                    "--type", predicate_type,
                    "--certificate-identity", args.verify_identity,
                    "--certificate-oidc-issuer", args.verify_issuer,
                ],
                "mutates_remote": False,
            })
    warnings = []
    if args.sign and "@sha256:" not in args.image:
        warnings.append("Resolve the image to an immutable sha256 digest before signing.")
    print(json.dumps({"image": args.image, "dry_run": True, "steps": steps, "warnings": warnings}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
