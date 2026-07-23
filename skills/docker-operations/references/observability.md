# Container observability

## Logs

Emit structured application logs to stdout/stderr. Include service, environment, version, request/trace ID, and severity. Exclude credentials, tokens, and personal data.

## Metrics

Expose a bounded metrics endpoint on an internal network. Use Prometheus labels with controlled cardinality. Track traffic, errors, latency, saturation, restarts, OOM events, and health.

## Traces

Send OTLP to an OpenTelemetry Collector rather than embedding vendor credentials in applications. Configure batching, retry limits, sampling, and memory protection.

## Local stack

Pin Prometheus, Grafana, and Collector images. Add health checks, named volumes, read-only configuration mounts, and internal networks. Do not expose dashboards publicly without authentication.
