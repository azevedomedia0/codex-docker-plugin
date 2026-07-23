# Production framework recipes

## Node.js and Next.js

Use the repository lockfile and frozen install. For Next.js, prefer standalone output when configured; copy `.next/standalone`, static assets, and public files. Run as a non-root Node user.

## Python, Django, and FastAPI

Install from pinned requirements or lockfiles in a builder. Use Gunicorn/Uvicorn workers appropriate to workload and CPU. For Django, collect static assets explicitly and run migrations as a separate job.

## Rails

Use Bundler deployment mode, precompile assets with controlled dummy secrets when supported, and keep database migration separate from web startup.

## Spring Boot

Build with Maven/Gradle caches, then copy only the runnable JAR or layered JAR output into a JRE image. Set JVM container-aware memory options based on limits.

## Go

Build a static or appropriately linked binary with explicit target OS/architecture. Use distroless or a minimal runtime only when CA certificates, timezone data, and debugging requirements are satisfied.

## Rust

Cache dependency compilation carefully, use locked Cargo resolution, and verify libc/OpenSSL compatibility between builder and runtime.

For every framework, identify the actual listening port, health endpoint, writable directories, shutdown behavior, and production command from repository evidence.
