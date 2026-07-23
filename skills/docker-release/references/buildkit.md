# BuildKit and multi-platform builds

Use Dockerfile syntax and features supported by the selected builder.

## Secure inputs

Use `RUN --mount=type=secret` for build secrets and `RUN --mount=type=ssh` only for narrowly scoped private-source access. Do not copy mounted values into layers.

## Caches

- Use cache mounts for package-manager downloads.
- Use registry or GitHub Actions caches for distributed CI.
- Separate untrusted pull-request cache writes from protected release cache writes.
- Include architecture, runtime version, and lockfile-sensitive inputs in cache scope.

## Multi-platform

Common targets are `linux/amd64` and `linux/arm64`. Confirm base images and native dependencies support each target. Prefer native builders for runtime tests; emulation can build successfully while hiding runtime failures.

Generate provenance and SBOM attestations only when the registry and downstream verifier retain them.
