---
name: docker-supply-chain
description: Audit Docker security, lint Dockerfiles, scan images and secrets, generate SBOMs, assess vulnerabilities, and sign or verify container images. Use when Codex needs Hadolint, Trivy, Docker Scout, Grype, Syft, CycloneDX, SPDX, Cosign, provenance, attestations, secret detection, CVE remediation, or container policy guidance.
---

# Docker supply chain

Inspect before executing. Treat scanning, SBOM generation, and verification as read-only; treat signing, attestation publication, and registry changes as external writes requiring explicit authorization.

## Plan

Run `python3 scripts/supply_chain_plan.py --image <reference>` from this skill directory. Add requested tools and operations. The script emits commands without executing them.

Use the plan in this order:

1. Lint source configuration.
2. Scan the build context for secrets.
3. Build an immutable local image when needed.
4. Generate an SBOM.
5. Scan packages and vulnerabilities.
6. Apply and verify remediations.
7. Sign or attest only an immutable digest.
8. Verify signatures and provenance independently.

## Lint and audit

- Run Hadolint against Dockerfiles and `docker compose config --quiet` against Compose files.
- Use the core `audit_docker.py` heuristic as a fast preflight, not a security conclusion.
- Check non-root execution, capabilities, seccomp/AppArmor, privileged mode, socket mounts, host paths, secret handling, image pinning, and exposed services.
- Suppress a rule only with a documented, narrow justification.

## Scan

Read [references/scanners.md](references/scanners.md) before choosing Trivy, Docker Scout, or Grype.

- Record scanner name, version, database freshness, image digest, severity threshold, and ignored findings.
- Distinguish OS-package, application-package, configuration, license, and secret results.
- Prioritize reachable critical/high vulnerabilities with available fixes.
- Do not silently upgrade across breaking runtime or distribution versions.

## SBOM and secrets

Read [references/sbom-and-secrets.md](references/sbom-and-secrets.md) for SPDX, CycloneDX, Syft, Trivy, and secret-scanning workflows.

- Generate SBOMs from the final image digest, not only the source tree.
- Keep SBOMs free of credentials and sensitive environment values.
- Scan the build context, Git history when authorized, Docker layers, and image configuration.
- Revoke or rotate any exposed credential; deleting it from the latest commit or layer is insufficient.

## Sign and verify

Read [references/signing.md](references/signing.md) before using Cosign.

- Sign digests, not mutable tags.
- Prefer keyless signing where the identity and CI trust model support it.
- Verify issuer, subject, digest, certificate transparency evidence, and expected attestations.
- Never create keys, publish signatures, or change registry state without explicit authorization.
