# Docker for Codex

A focused Codex plugin for building, running, debugging, reviewing, and securing Docker containers and Docker Compose applications.

## Capabilities

- Create and improve `Dockerfile`, `.dockerignore`, and Compose configurations
- Design cache-efficient multi-stage builds
- Diagnose build, startup, networking, storage, and health-check failures
- Verify images and local Compose stacks
- Review container configuration for common security and secret-handling risks
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
- `Debug this Docker build or Compose stack.`
- `Review these Docker files for security and image size.`

## Plugin structure

```text
.
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── docker-workflows/
│       ├── agents/
│       │   └── openai.yaml
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
