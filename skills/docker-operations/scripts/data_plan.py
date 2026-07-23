#!/usr/bin/env python3
"""Print non-executing database operation plans for Compose services."""

from __future__ import annotations

import argparse
import json


COMMANDS = {
    ("postgres", "backup"): ["sh", "-c", 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump --host=127.0.0.1 --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --format=custom'],
    ("postgres", "restore"): ["sh", "-c", 'PGPASSWORD="$POSTGRES_PASSWORD" pg_restore --host=127.0.0.1 --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --clean --if-exists'],
    ("mysql", "backup"): ["sh", "-c", 'mysqldump --single-transaction --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" "$MYSQL_DATABASE"'],
    ("mysql", "restore"): ["sh", "-c", 'mysql --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" "$MYSQL_DATABASE"'],
    ("redis", "backup"): ["redis-cli", "BGSAVE"],
    ("redis", "restore"): ["manual", "restore validated RDB/AOF into an isolated stopped target"],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=("postgres", "mysql", "redis"), required=True)
    parser.add_argument("--action", choices=("backup", "restore", "migrate"), required=True)
    parser.add_argument("--service", required=True)
    args = parser.parse_args()

    if args.action == "migrate":
        inner = ["APPLICATION_MIGRATION_COMMAND"]
    else:
        inner = COMMANDS[(args.engine, args.action)]
    compose_action = "run" if args.action == "migrate" else "exec"
    compose = ["docker", "compose", compose_action]
    compose += ["--rm"] if compose_action == "run" else ["-T"]
    compose += [args.service, *inner]
    print(json.dumps({
        "dry_run": True,
        "engine": args.engine,
        "action": args.action,
        "service": args.service,
        "command_template": compose,
        "requires_authorization": True,
        "stream_direction": "stdout-to-explicit-backup-file" if args.action == "backup" else ("stdin-from-verified-backup-file" if args.action == "restore" else None),
        "preconditions": [
            "Resolve exact project, service, database, and backup destination.",
            "Verify credentials are injected without printing them.",
            "For restore or destructive migration, verify a restorable backup and isolated target first.",
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
