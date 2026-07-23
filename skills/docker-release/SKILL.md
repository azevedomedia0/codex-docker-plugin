---
name: docker-release
description: Build and publish Docker images with BuildKit, buildx, multi-platform manifests, registry tagging, remote caches, provenance, SBOM attestations, and CI/CD. Use when Codex needs Docker Hub, GHCR, ECR, GCR/Artifact Registry, ACR, registry authentication, image promotion, AMD64/ARM64 builds, release tags, cache configuration, or container publishing workflows.
---

# Docker release

Resolve the target registry, repository, immutable version, platforms, credentials source, and promotion policy before changing state.

## Plan a release

Run `python3 scripts/release_plan.py --image <registry/repository:tag>` from this skill directory. It prints a dry-run plan. Add `--publish` only to describe a push-capable plan; the script never logs in, builds, or pushes.

Use the sequence:

1. Validate the Dockerfile and tests.
2. Confirm BuildKit/buildx availability.
3. Resolve platforms and native dependency support.
4. Choose local or remote cache scopes.
5. Build without publishing.
6. Scan the resulting digest.
7. Publish immutable version and digest.
8. Attach SBOM/provenance and sign when requested.
9. Promote tags by digest rather than rebuilding.

## BuildKit and multi-platform

Read [references/buildkit.md](references/buildkit.md) for secret mounts, SSH forwarding, cache mounts, remote caches, provenance, and multi-platform constraints.

- Use `--platform` explicitly and avoid claiming a platform was tested when it was only cross-built.
- Keep credentials out of build arguments and layers.
- Scope remote caches to prevent untrusted pull requests from poisoning release caches.
- Prefer reproducible inputs and pinned base images.

## Registries and tags

Read [references/registries.md](references/registries.md) for Docker Hub, GHCR, ECR, Artifact Registry, and ACR.

- Preview exact login host, repository, tags, and digest before publishing.
- Use credential helpers or short-lived identity tokens.
- Never echo tokens or pass secrets directly on a command line when stdin or native auth is available.
- Publish immutable semantic-version and SHA tags; treat `latest` as an optional pointer.

## CI/CD

Use the core `generate_ci.py` for a starter workflow, then apply [references/ci-release.md](references/ci-release.md).

- Build and test on pull requests without logging in or pushing.
- Publish only from protected branches or release tags.
- Use least-privilege permissions and environment protections.
- Separate build verification from production promotion when approval is required.
