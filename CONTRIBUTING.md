# Contributing

Thanks for helping improve Docker for Codex.

## Development

1. Fork and clone the repository.
2. Create a focused branch.
3. Update the plugin or skill instructions.
4. Run `python3 scripts/validate.py`.
5. Open a pull request describing the behavior change and validation performed.

Keep skill instructions concise, imperative, and grounded in safe Docker workflows. Do not add credentials, generated secrets, machine-specific paths, or destructive cleanup defaults.

## Pull requests

- Keep each pull request focused on one coherent change.
- Update starter prompts or metadata when behavior changes materially.
- Preserve the plugin name `docker` and the `docker-workflows` skill namespace.
- Include a realistic example prompt when introducing a new workflow.
- Confirm that no broad prune, volume deletion, registry push, or remote deployment occurs without explicit user authorization.
