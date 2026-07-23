---
name: docker-workflows
description: Build, run, debug, review, and secure Docker containers and Docker Compose applications. Use when Codex needs to create or edit Dockerfiles, .dockerignore files, compose.yaml/docker-compose.yml files, container entrypoints, health checks, multi-stage builds, local development stacks, image builds, container tests, registry workflows, or diagnose Docker daemon, networking, volume, build-cache, and service startup failures.
---

# Docker workflows

Work from evidence in the repository and the local Docker environment. Preserve the project's existing package manager, runtime conventions, ports, commands, and deployment assumptions.

## Inspect

1. Read repository instructions and relevant manifests before changing files.
2. Locate existing Dockerfiles, Compose files, ignore files, entrypoints, environment examples, and CI workflows.
3. Check `docker version` and `docker compose version` before relying on local execution. If the daemon is unavailable, continue with static validation and report the limitation.
4. Determine the requested mode:
   - For review or diagnosis, inspect and explain without editing.
   - For implementation, make the smallest coherent set of changes and verify it.

## Author

- Pin base images to an explicit version appropriate to the project. Preserve digest pinning when already used.
- Prefer multi-stage builds when they materially reduce the runtime image or keep build tools out of production.
- Order copy and install steps to preserve dependency caching.
- Use exec-form `ENTRYPOINT` and `CMD` when signal handling matters.
- Run the final process as a non-root user unless the workload requires otherwise.
- Add a health check only when there is a reliable, lightweight readiness signal.
- Put irrelevant or sensitive paths in `.dockerignore`; never bake credentials, private keys, `.env` files, or local caches into an image.
- In Compose, use service names for inter-service networking and avoid `localhost` between containers.
- Use environment-variable substitution and example env files for configuration; never invent or print secrets.
- Avoid obsolete Compose `version` keys in new files.

## Verify

Use checks proportional to the change:

- Run `docker compose config` for Compose changes.
- Build the affected target with plain progress when useful: `docker build --progress=plain ...` or `docker compose build`.
- Start only the services needed for verification, preferably detached.
- Inspect `docker compose ps`, health status, and bounded logs.
- Exercise the relevant endpoint, command, or test inside the container.
- Stop resources created for testing when they are no longer needed. Do not remove named volumes unless the user requested data deletion.
- If execution is unavailable or too expensive, validate syntax and explain exactly what remains unverified.

## Diagnose

Start with the failing command and its complete error. Then narrow the issue:

- Build failures: inspect build context, ignored files, stage names, architecture, network access, and cache behavior.
- Startup failures: inspect the resolved command, entrypoint permissions and line endings, environment, mounts, working directory, and logs.
- Networking failures: inspect published versus exposed ports, bind addresses, Compose networks, DNS service names, and host access.
- Storage failures: inspect mount type, target path, ownership, SELinux labeling where relevant, and whether old named-volume data is masking a change.
- Resource failures: inspect container state, exit code, health status, memory limits, and daemon disk usage.

Prefer the smallest reproducible command. Do not recommend broad cache or data deletion as a first step.

## Safety

- Treat `docker system prune`, `docker builder prune`, image removal, volume removal, and Compose `down -v` as destructive. Resolve exact targets and obtain explicit user authorization before deleting material data or broad sets of resources.
- Do not stop, restart, or replace unrelated running containers.
- Do not push images, log in to registries, or alter remote deployments unless explicitly requested.
- Avoid privileged containers, host networking, Docker socket mounts, unrestricted capabilities, and writable host-root mounts unless required and clearly justified.
- Redact secrets from logs and final responses.
