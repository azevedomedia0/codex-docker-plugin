# Container release CI

Use separate phases:

1. Pull request: lint, test, build without push, scan.
2. Protected branch/tag: rebuild reproducibly or promote a verified digest, publish immutable tags.
3. Release: generate SBOM/provenance, sign, verify, and record digest.
4. Deployment: enforce signature/policy independently.

Use concurrency controls to prevent racing the same tag. Prefer OIDC federation over stored cloud credentials. Restrict secrets and write permissions to protected events and environments.

Never run pull-request code from forks with privileged runners, registry credentials, Docker socket access, or production secrets.
