# Development containers

Prefer a pinned base image or Dockerfile shared with development requirements.

- Set `remoteUser` to a non-root user.
- Align UID/GID when bind mounts require host compatibility.
- Forward only documented development ports.
- Use `postCreateCommand` for repeatable, non-secret setup.
- Pin features by version or digest.
- Keep cloud credentials, SSH agents, Git config, and Docker socket mounts opt-in.
- Use named volumes for large dependency caches when appropriate.

For Docker-from-Docker, prefer an isolated daemon. If Docker-outside-of-Docker is explicitly required, explain that mounting the host socket grants host-equivalent control.
