# Scanner selection

## Trivy

Use for image, filesystem, IaC/misconfiguration, secret, license, and SBOM workflows. Pin the tool version in CI and cache only its vulnerability database.

Examples to adapt:

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 IMAGE@DIGEST
trivy config --severity HIGH,CRITICAL .
trivy fs --scanners secret,misconfig .
```

## Docker Scout

Use when Docker's registry and organization integrations are already part of the workflow. Confirm authentication and organization context before commands that upload metadata.

## Grype

Use for image or SBOM vulnerability analysis, especially with Syft-generated SBOMs:

```bash
grype IMAGE@DIGEST --fail-on high
grype sbom:sbom.spdx.json --fail-on high
```

## Policy

- Scan the immutable release digest.
- Preserve raw machine-readable output as a CI artifact when policy allows.
- Maintain time-bounded, justified ignore entries.
- Re-scan released images as vulnerability databases evolve.
