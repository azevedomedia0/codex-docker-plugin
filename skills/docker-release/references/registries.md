# Registry workflows

## Docker Hub

Target `docker.io/OWNER/IMAGE`. Prefer access tokens and `docker login --password-stdin`.

## GitHub Container Registry

Target `ghcr.io/OWNER/IMAGE`. In Actions, grant `packages: write` only to publishing jobs and authenticate with `GITHUB_TOKEN` where policy permits.

## Amazon ECR

Resolve the account and region, then use short-lived AWS identity and the ECR credential helper or `aws ecr get-login-password`.

## Google Artifact Registry

Resolve project, region, and repository. Prefer workload identity federation and `gcloud auth configure-docker` for the exact host.

## Azure Container Registry

Resolve registry name and subscription. Prefer managed identity or federated credentials; avoid long-lived admin credentials.

For every registry, preview the fully qualified repository, tags, digest, and promotion target before pushing.
