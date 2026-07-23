# SBOM and secret workflows

## SBOM

Choose SPDX JSON when interoperability and license tooling favor SPDX. Choose CycloneDX JSON when dependency and vulnerability platforms favor CycloneDX.

Examples:

```bash
syft IMAGE@DIGEST -o spdx-json=sbom.spdx.json
syft IMAGE@DIGEST -o cyclonedx-json=sbom.cdx.json
trivy image --format cyclonedx --output sbom.cdx.json IMAGE@DIGEST
```

Record generator version, image digest, timestamp, and format. Validate that the SBOM describes the final runtime image.

## Secrets

Scan before build and after build:

```bash
trivy fs --scanners secret .
trivy image --scanners secret IMAGE@DIGEST
```

Also inspect `.dockerignore`, Docker history, build arguments, environment declarations, Compose interpolation, CI logs, and copied configuration.

If a credential is found:

1. Stop distribution.
2. Revoke or rotate it.
3. Remove it from source history and every affected image layer.
4. Rebuild from a clean context without reusing contaminated layers.
5. Verify with a second scan.
