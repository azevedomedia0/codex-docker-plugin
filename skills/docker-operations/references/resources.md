# Resource and runtime tuning

- Inspect `docker stats`, cgroup limits, container exit/OOM state, and application metrics.
- Set memory limits above measured working-set peaks plus native/runtime headroom.
- Set CPU limits only after observing latency under throttling.
- Configure stop grace periods to match application shutdown.
- Choose restart policies intentionally; avoid hiding crash loops with unconditional restarts.
- Bound Docker log files with size and file-count rotation.
- Watch writable-layer growth, inode exhaustion, image/cache usage, and volume capacity.
- Separate health failures from process crashes in alerts.

Change one constraint at a time and compare before/after behavior.
