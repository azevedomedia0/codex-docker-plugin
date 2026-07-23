---
name: docker-platforms
description: Generate framework-specific Docker recipes, development containers, and Kubernetes or Helm migration assets. Use when Codex needs production Dockerfiles for Next.js, Django, FastAPI, Rails, Spring Boot, Go, Rust, or other runtimes; .devcontainer configuration for VS Code/Codespaces; or conversion of Docker Compose services into Kubernetes manifests, Deployments, Services, ConfigMaps, Secrets guidance, PersistentVolumeClaims, or Helm values.
---

# Docker platforms

Inspect the application and existing deployment conventions first. Generate an explicit draft, then adapt it to the repository rather than overwriting established assets.

## Framework recipes

Read [references/frameworks.md](references/frameworks.md) for runtime-specific build, process, health, and non-root patterns.

Run `python3 scripts/generate_framework_dockerfile.py --framework <nextjs|django|fastapi|rails|spring|go|rust>` to print a reviewable production starter. Supply the real application port and package manager where applicable. The generator never writes files.

- Preserve lockfiles and framework production modes.
- Copy only runtime artifacts into the final stage.
- Use the framework's real production server, not a development server.
- Verify static assets, migrations, writable directories, signal handling, and graceful shutdown.

## Development containers

Run `python3 scripts/generate_platform_asset.py devcontainer --name <name> --port <port>` from this skill directory to print a minimal `.devcontainer/devcontainer.json`.

Read [references/devcontainers.md](references/devcontainers.md) before adding features, mounts, forwarded ports, host credentials, or Docker socket access.

- Keep the development user non-root and align file ownership.
- Do not mount host credentials or the Docker socket by default.
- Pin image/features versions and preserve the repository's setup commands.

## Kubernetes and Helm migration

Run `python3 scripts/generate_platform_asset.py kubernetes --name <name> --image <image@sha256:digest> --port <port>` to print a starter Deployment and Service. Add `--health-path` only when a real non-mutating endpoint is known. Tag-only images are rejected unless `--allow-tag` is explicitly supplied for a non-production draft.

Read [references/kubernetes.md](references/kubernetes.md) before converting Compose.

- Map health checks to startup, readiness, and liveness probes deliberately.
- Convert named volumes only after choosing a storage class and access mode.
- Replace `depends_on` with readiness, retries, init jobs, or orchestration.
- Keep secrets out of generated manifests.
- Explain behavior that cannot be translated directly.
