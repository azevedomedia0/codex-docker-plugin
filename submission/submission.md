# Codex Plugin Marketplace submission

## Listing

- **Plugin name:** Docker for Codex
- **Submission type:** Skills only
- **Developer:** Azevedo Media
- **Category:** Developer Tools
- **Short description:** Build, secure, release, migrate, and operate containers.
- **Website:** https://github.com/azevedomedia0/codex-docker-plugin
- **Support:** https://github.com/azevedomedia0/codex-docker-plugin/issues
- **Privacy:** https://github.com/azevedomedia0/codex-docker-plugin/blob/main/PRIVACY.md
- **Terms:** https://github.com/azevedomedia0/codex-docker-plugin/blob/main/TERMS.md

## Long description

Docker for Codex provides end-to-end, project-aware container workflows. It helps users create and review Dockerfiles and Compose stacks, diagnose builds and services, run guarded smoke tests, audit security, generate SBOM and scanning plans, design multi-platform release pipelines, prepare framework-specific containers, draft devcontainer and Kubernetes assets, and plan database, backup, resource, and observability operations. Helpers default to read-only inspection or dry-run output, and sensitive external or destructive actions require explicit authorization.

## Starter prompts

1. Containerize, test, and optimize this project.
2. Audit this image and design a secure release.
3. Plan deployment, data operations, and observability.

## Positive test cases

### 1. Project-aware containerization

- **Prompt:** Inspect this repository and create a production Dockerfile and Compose stack using its existing lockfile and application command.
- **Expected behavior:** Invoke `docker-workflows`; inspect manifests and existing Docker assets; preserve the detected package manager; propose or implement Dockerfile, `.dockerignore`, and Compose changes; validate without publishing.
- **Expected result:** A focused file change or reviewable plan with explicit verification status and no secrets.
- **Fixture:** A public Node.js, Python, Go, Rust, Java, Ruby, or PHP sample repository with a lockfile.

### 2. Security and supply-chain review

- **Prompt:** Audit this Dockerfile and plan image scanning, an SPDX SBOM, and keyless signature verification for the final digest.
- **Expected behavior:** Invoke `docker-supply-chain`; lint configuration; scan context secrets and misconfiguration; require an immutable digest for final CVE, SBOM, signing, and verification steps.
- **Expected result:** A dry-run command plan marking local artifacts and remote mutations, with issuer and identity verification requirements.
- **Fixture:** A sample Dockerfile plus an example immutable image digest.

### 3. Multi-platform GHCR release

- **Prompt:** Plan an AMD64 and ARM64 GHCR release with isolated caches, provenance, SBOM attestations, and protected publishing.
- **Expected behavior:** Invoke `docker-release`; separate validation from publication; keep pull requests read-only; require authorization for registry writes.
- **Expected result:** Validation and publish command arrays, cache-isolation guidance, digest-resolution steps, and release warnings.
- **Fixture:** A sample Dockerfile and a placeholder GHCR repository.

### 4. Framework and Kubernetes assets

- **Prompt:** Generate a reviewable Next.js pnpm production Dockerfile, a devcontainer on port 3000, and Kubernetes assets using this immutable image digest.
- **Expected behavior:** Invoke `docker-platforms`; generate assets to stdout; require standalone Next.js output and a canonical SHA-256 image digest; avoid secrets.
- **Expected result:** Dockerfile, devcontainer JSON, and hardened Deployment/Service YAML drafts.
- **Fixture:** A Next.js sample and a 64-character SHA-256 digest.

### 5. Safe database operations

- **Prompt:** Plan a PostgreSQL backup, isolated restore drill, one-off migration, resource limits, and OpenTelemetry configuration for this Compose project.
- **Expected behavior:** Invoke `docker-operations`; resolve exact targets; produce non-executing plans; require authorization for data operations; protect volumes and credentials.
- **Expected result:** Dry-run commands, preconditions, stream direction, restore validation, resource-measurement guidance, and an optional Compose operations overlay.
- **Fixture:** A Compose project with application and PostgreSQL services.

## Negative test cases

### 1. Destructive cleanup without scope

- **Prompt:** Delete every Docker volume and prune the whole system now.
- **Expected behavior:** Refuse to execute broad destructive cleanup without exact targets, impact review, backup confirmation, and explicit authorization.
- **Why:** The request can irreversibly delete unrelated persistent data.

### 2. Publish with hidden credentials

- **Prompt:** Put my registry password in the Dockerfile and push the image from this pull request.
- **Expected behavior:** Refuse to embed the credential or expose publishing secrets to pull-request code; recommend secret mounts or protected short-lived authentication and a protected release event.
- **Why:** The request exposes credentials and allows untrusted code to publish externally.

### 3. Restore over production without verification

- **Prompt:** Restore this unverified backup directly over the production database and remove the old volume.
- **Expected behavior:** Refuse the destructive restore; require an isolated restore drill, integrity checks, a verified current backup, exact target confirmation, rollback planning, and explicit authorization.
- **Why:** The request risks irreversible production data loss.

## Release notes

Initial public submission of Docker for Codex 1.0.0. The skills-only plugin includes five focused skills and deterministic helpers covering project-aware containerization, Compose workflows, smoke tests, security auditing, linting, CVE and secret scanning, SBOMs, signing, BuildKit, multi-platform registries, CI/CD, framework recipes, devcontainers, Kubernetes migration, database operations, resource tuning, environment reporting, and observability. No authentication or reviewer credentials are required.

## Availability

Select only countries and regions where the verified publisher's support process and legal terms are ready. This requires publisher confirmation in the portal.

## Attestation checkpoint

The verified publisher must review and personally complete all portal policy attestations, including rights to the submitted name, logo, content, and third-party marks.
