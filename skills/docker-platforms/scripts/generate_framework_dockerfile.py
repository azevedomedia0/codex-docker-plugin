#!/usr/bin/env python3
"""Generate reviewable production Dockerfile starters for common frameworks."""

from __future__ import annotations

import argparse


TEMPLATES = {
    "nextjs": """# REVIEW: enable Next.js output: "standalone" and pin every FROM image to an approved digest.
FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN mkdir -p public && npm run build

FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build --chown=app:app /app/.next/standalone ./
COPY --from=build --chown=app:app /app/.next/static ./.next/static
COPY --from=build --chown=app:app /app/public ./public
USER 10001
EXPOSE {port}
ENV PORT={port} HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
""",
    "django": """# REVIEW: pin every FROM image to an approved digest and replace config.wsgi with the real module.
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY --chown=app:app . .
USER 10001
EXPOSE {port}
CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "config.wsgi:application"]
""",
    "fastapi": """# REVIEW: pin every FROM image to an approved digest and replace app:app with the real module.
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY --chown=app:app . .
USER 10001
EXPOSE {port}
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{port}"]
""",
    "rails": """# REVIEW: pin every FROM image to an approved digest.
FROM ruby:3.4-slim AS build
WORKDIR /app
COPY Gemfile Gemfile.lock ./
RUN bundle config set without 'development test' && bundle install
COPY . .
RUN SECRET_KEY_BASE_DUMMY=1 bundle exec rails assets:precompile

FROM ruby:3.4-slim
ENV RAILS_ENV=production
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build --chown=app:app /usr/local/bundle /usr/local/bundle
COPY --from=build --chown=app:app /app /app
USER 10001
EXPOSE {port}
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]
""",
    "spring": """# REVIEW: pin every FROM image to an approved digest and confirm Maven versus Gradle.
FROM eclipse-temurin:21-jdk AS build
WORKDIR /app
COPY . .
RUN ./gradlew --no-daemon bootJar

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build --chown=app:app /app/build/libs/*.jar app.jar
USER 10001
EXPOSE {port}
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
""",
    "go": """# REVIEW: pin every FROM image to an approved digest and replace ./cmd/app if needed.
FROM golang:1.24-bookworm AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
USER nonroot:nonroot
EXPOSE {port}
ENTRYPOINT ["/app"]
""",
    "rust": """# REVIEW: pin every FROM image to an approved digest and replace the binary name.
FROM rust:1.85-bookworm AS build
WORKDIR /src
COPY . .
RUN cargo build --locked --release

FROM debian:bookworm-slim
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build --chown=app:app /src/target/release/app /app/app
USER 10001
EXPOSE {port}
ENTRYPOINT ["/app/app"]
""",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", choices=tuple(TEMPLATES), required=True)
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--package-manager", choices=("npm", "pnpm", "yarn"), default="npm", help="Used for Next.js starters")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    template = TEMPLATES[args.framework]
    if args.framework == "nextjs" and args.package_manager == "pnpm":
        template = template.replace("package-lock.json", "pnpm-lock.yaml")
        template = template.replace("RUN npm ci", "RUN corepack enable && pnpm install --frozen-lockfile")
        template = template.replace("RUN npm run build", "RUN corepack enable && pnpm build")
    elif args.framework == "nextjs" and args.package_manager == "yarn":
        template = template.replace("package-lock.json", "yarn.lock")
        template = template.replace("RUN npm ci", "RUN corepack enable && yarn install --immutable")
        template = template.replace("RUN npm run build", "RUN corepack enable && yarn build")
    print(template.format(port=args.port), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
