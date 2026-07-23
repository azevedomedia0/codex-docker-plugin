# Docker for Codex

A focused Codex plugin for detecting, containerizing, testing, optimizing, and securing Docker projects and Docker Compose applications.

## Capabilities

- Detect runtimes, frameworks, lockfiles, Docker assets, and CI configuration
- Create and improve `Dockerfile`, `.dockerignore`, and Compose configurations
- Audit common Docker security risks and secret-handling mistakes
- Design cache-efficient, size-conscious multi-stage builds
- Plan or execute isolated Compose smoke tests with safe cleanup
- Generate GitHub Actions workflows for image validation and optional GHCR publishing
- Diagnose build, startup, networking, storage, and health-check failures
- Apply conservative cleanup practices that protect unrelated containers and persistent data

## Installation

### From GitHub

Clone the repository into a local plugin directory:

```bash
git clone https://github.com/azevedomedia0/codex-docker-plugin.git
```

Then add the plugin through Codex using the cloned directory.

### Local development

The plugin manifest is located at `.codex-plugin/plugin.json`. Its skill is discovered from `skills/docker-workflows/`.

Example prompts:

- `Containerize this project with Docker.`
- `Audit and optimize this Docker configuration.`
- `Create a safe container smoke test and CI workflow.`

## Plugin structure

```text
.
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── docker-workflows/
│       ├── agents/
│       │   └── openai.yaml
│       ├── scripts/
│       │   ├── audit_docker.py
│       │   ├── generate_ci.py
│       │   ├── inspect_project.py
│       │   └── smoke_test.py
│       └── SKILL.md
└── scripts/
    └── validate.py
```

## Validation

Run the repository validator before submitting changes:

```bash
python3 scripts/validate.py
```

The validator checks the manifest, semantic version, required interface metadata, referenced paths, skill frontmatter, and placeholder content.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Security issues should follow [SECURITY.md](SECURITY.md).

## License

Licensed under the [MIT License](LICENSE).
