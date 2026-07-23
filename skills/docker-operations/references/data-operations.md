# Database operations

## PostgreSQL

Use `pg_dump`/`pg_restore` for logical backups and compatible major versions. Prefer custom format for selective restore. Use `pg_isready` for readiness.

## MySQL

Use `mysqldump` or a physical backup tool appropriate to scale and consistency needs. Record server SQL mode, character set, and version.

## Redis

Choose RDB/AOF handling based on durability settings. Coordinate persistence before copying data files; do not copy a live volume blindly.

## Migrations

Run one migration job per release with a lock and a timeout. Separate backward-compatible schema expansion from destructive contraction. Verify application rollback compatibility.

## Restore drills

Restore into an isolated service and volume, validate integrity and application behavior, then delete the drill resources only after confirming exact targets.
