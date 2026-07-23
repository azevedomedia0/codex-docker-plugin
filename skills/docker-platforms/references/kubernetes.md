# Compose to Kubernetes

Map concepts deliberately:

- service container → Deployment/StatefulSet/Job
- published port → Service and optionally Ingress/Gateway
- environment → ConfigMap plus Secret references
- named volume → PersistentVolumeClaim after storage design
- healthcheck → startup/readiness/liveness probes
- restart policy → controller behavior
- `depends_on` → retries, readiness, init containers, or jobs

Do not translate build contexts into production manifests; reference immutable published images. Add resource requests/limits, security contexts, service accounts, disruption behavior, and rollout strategy from deployment requirements.

Use Helm only when templating across environments is genuinely needed. Keep secret values outside committed `values.yaml`.
