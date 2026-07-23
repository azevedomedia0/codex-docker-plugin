---
name: docker-workflows
description: Detect, containerize, run, smoke-test, optimize, audit, and debug Docker projects and Docker Compose applications. Use when Codex needs to identify a project's runtime or framework; create or edit Dockerfiles, .dockerignore, Compose files, entrypoints, health checks, multi-stage builds, or container CI; inspect image security and size; run local container tests; or diagnose Docker daemon, networking, volume, build-cache, and startup failures.
---

# Docker workflows

Work from repository and runtime evidence. Preserve the project's package manager, lockfiles, commands, ports, deployment assumptions, and existing conventions.

## Inspect the project

1. Read repository instructions and relevant manifests.
2. Run `python3 scripts/inspect_project.py <project>` from this skill directory for a bounded, read-only stack inventory.
3. Inspect detected manifests, lockfiles, Docker files, CI, environment examples, and monorepo configuration.
4. Check `docker version` and `docker compose version` before relying on local execution. Continue with static validation if the daemon is unavailable.
5. For review or diagnosis, do not edit. For implementation, make the smallest coherent change and verify it.

Treat detection as evidence, not certainty. Reconcile conflicting markers with scripts, documentation, and CI.

## Containerize

- Pin an explicit base-image version suited to the detected runtime. Preserve digest pinning.
- Match the repository's lockfile and frozen-install command.
- Use multi-stage builds when they remove compilers, source, or development dependencies from runtime.
- Copy dependency manifests before source to preserve caching.
- Use exec-form `ENTRYPOINT` and `CMD` when signal handling matters.
- Run as a non-root user unless the workload requires otherwise.
- Add a health check only for a reliable, lightweight readiness signal.
- Exclude secrets, `.env` files, VCS data, local caches, dependencies, and build output not needed in the image.
- Use service names between Compose containers, not `localhost`.
- Avoid obsolete Compose `version` keys.

For a new local stack, run `python3 scripts/generate_compose.py --service <name> --port <port>` to print a starter Compose file. Add `--postgres` or `--redis` only when the application needs those services. Review generated commands, health checks, credentials, and persistence before writing the file.

## Audit and optimize

Run `python3 scripts/audit_docker.py <project>` from this skill directory before and after material Docker changes.

Review each finding in context:

- Remove privileged mode, Docker socket mounts, unrestricted capabilities, host networking, and writable host-root mounts unless explicitly required.
- Prevent secrets in `ARG`, `ENV`, `COPY`, Compose literals, logs, and image history. Prefer BuildKit secret mounts or runtime injection.
- Use a non-root runtime user and restrict unnecessary ports and writable paths.
- Reduce image size through smaller appropriate bases, multi-stage builds, dependency pruning, combined package-manager cleanup, and a narrow build context.
- Improve cache reuse without placing frequently changed source before dependency installation.
- Do not blindly replace a compatible base with Alpine; native dependencies, libc compatibility, and debugging needs matter.

The bundled audit is heuristic. Do not report it as a vulnerability scanner or substitute for Trivy, Docker Scout, Grype, Hadolint, or policy enforcement.

## Smoke-test

For Compose services, first run:

```bash
python3 scripts/smoke_test.py --project <project> --service <service> --url <health-url>
```

The default is a read-only plan. Add `--execute` only when local container execution is authorized. The runner:

- validates resolved Compose configuration;
- creates an isolated Compose project name;
- starts only the requested service and declared dependencies;
- waits for a URL or container health;
- captures bounded status and logs on failure; and
- runs `compose down` without `--volumes`.

Use the application's real test command when stronger verification is available. Never delete pre-existing volumes as part of a smoke test.

## Generate CI

Generate a starter GitHub Actions workflow:

```bash
python3 scripts/generate_ci.py --project <project> --image-name my-app
```

The generator requires an existing build context and Dockerfile, then prints YAML by default. Use `--output <project>/.github/workflows/docker.yml` only after reviewing repository conventions. Set `--branch` when the default branch is not `main`. Generated CI validates the build on pull requests and can publish to GHCR on the selected branch when `--publish-ghcr` is supplied.

Adapt generated CI to existing workflows, registry policy, platforms, tests, and required permissions. Do not add registry publishing unless requested.

## Diagnose

Start with the failing command and complete error:

- Build: inspect context, ignored files, stages, architecture, network, credentials, and cache.
- Startup: inspect command, entrypoint permissions and line endings, environment, mounts, workdir, exit code, and logs.
- Network: inspect bind address, published versus exposed ports, Compose DNS, network membership, and host access.
- Storage: inspect mount type, target, ownership, SELinux labeling, and stale named-volume data.
- Resources: inspect health, OOM state, limits, daemon capacity, and architecture.

Prefer the smallest reproduction. Do not recommend broad pruning as a first step.

## Safety

- Treat `docker system prune`, builder pruning, image removal, volume removal, and `compose down -v` as destructive. Resolve exact targets and obtain explicit authorization.
- Do not stop, restart, or replace unrelated containers.
- Do not log in, push images, sign artifacts, or alter remote deployments unless requested.
- Redact secrets from command output and responses.
