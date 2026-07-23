---
name: docker-operations
description: Plan and troubleshoot container database migrations, backups, restores, resource limits, health checks, logging, metrics, OpenTelemetry, Prometheus/Grafana stacks, and Docker environment health. Use when Codex needs PostgreSQL/MySQL/Redis volume protection, one-off migration jobs, operational runbooks, CPU or memory tuning, restart policies, log rotation, observability configuration, daemon inventory, disk usage analysis, or safe cleanup previews.
---

# Docker operations

Prefer read-only inspection and reversible actions. Identify the exact Compose project, service, container, volume, database, and environment before operational changes.

## Environment report

Run `python3 scripts/environment_report.py` from this skill directory for a read-only tool inventory. Add `--docker` only when Docker CLI inspection is allowed.

Report client/server versions separately, daemon availability, Compose/buildx support, architecture, active context, disk usage, and relevant optional tools. Redact registry usernames and environment values.

## Database migrations

Read [references/data-operations.md](references/data-operations.md).

- Use a one-off job with the same immutable application image.
- Wait for database readiness, acquire the framework's migration lock when available, and make retries safe.
- Back up before destructive or irreversible schema changes.
- Do not run migrations concurrently from every application replica.

## Backup and restore

Run `python3 scripts/data_plan.py --engine <postgres|mysql|redis> --action <backup|restore|migrate> --service <name>` to print a non-executing plan.

- Prefer logical, application-consistent backups for portability.
- Record image/database versions and encryption/storage destinations.
- Test restoration into an isolated target.
- Never overwrite a live database or remove a volume without explicit authorization and a verified backup.

## Resource tuning

Read [references/resources.md](references/resources.md).

Run `python3 scripts/generate_ops_overlay.py --service <name>` to print a conservative Compose override with bounded logging, graceful shutdown, placeholder CPU/memory settings, and hardened runtime defaults. Add `--otel-endpoint` to wire an existing collector; the generator does not expose or deploy dashboards.

- Measure peak and steady-state usage before setting limits.
- Reserve headroom for runtime overhead, native allocations, and burst behavior.
- Diagnose OOM kills, CPU throttling, restart loops, and disk pressure from evidence.
- Configure bounded log rotation and intentional restart policies.

## Observability

Read [references/observability.md](references/observability.md).

- Emit structured logs to stdout/stderr without secrets.
- Expose metrics and traces on internal networks unless public access is required.
- Add OpenTelemetry collectors, Prometheus, and Grafana with pinned versions, health checks, and persistent storage.
- Separate readiness from liveness and avoid probes that cause load or mutate state.
