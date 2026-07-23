#!/usr/bin/env python3
"""Generate a conservative local Docker Compose starter to stdout."""

from __future__ import annotations

import argparse
import re


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--container-port", type=int)
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument("--redis", action="store_true")
    args = parser.parse_args()
    container_port = args.container_port or args.port
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?", args.service):
        parser.error("--service must be a lowercase Compose service name")
    if not 1 <= args.port <= 65535 or not 1 <= container_port <= 65535:
        parser.error("ports must be between 1 and 65535")

    dependencies = []
    app_environment = ["      APP_ENV: development"]
    if args.postgres:
        app_environment.append("      DATABASE_URL: ${DATABASE_URL:?set a URL-encoded DATABASE_URL for the app}")
    if args.redis:
        app_environment.append("      REDIS_URL: redis://redis:6379/0")
    services = [
        f"""  {args.service}:
    build:
      context: .
    ports:
      - "${{APP_PORT:-{args.port}}}:{container_port}"
    environment:
{chr(10).join(app_environment)}
    init: true
    restart: unless-stopped"""
    ]
    volumes = []
    if args.postgres:
        dependencies.append("db")
        volumes.append("db-data")
        services.append("""  db:
    image: postgres:17
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-app}
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 3s
      retries: 20
    volumes:
      - db-data:/var/lib/postgresql/data""")
    if args.redis:
        dependencies.append("redis")
        volumes.append("redis-data")
        services.append("""  redis:
    image: redis:7
    command: ["redis-server", "--appendonly", "yes"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 20
    volumes:
      - redis-data:/data""")
    if dependencies:
        dependency_yaml = "\n    depends_on:" + "".join(
            f"\n      {dependency}:\n        condition: service_healthy" for dependency in dependencies
        )
        services[0] += dependency_yaml

    output = "services:\n" + "\n".join(services) + "\n"
    if volumes:
        output += "\nvolumes:\n" + "".join(f"  {volume}:\n" for volume in volumes)
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
