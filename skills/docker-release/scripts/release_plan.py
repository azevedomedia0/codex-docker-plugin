#!/usr/bin/env python3
"""Print a non-executing Buildx release plan."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--platforms", default="linux/amd64,linux/arm64")
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--context", default=".")
    parser.add_argument("--cache-ref")
    parser.add_argument("--validation-cache-ref")
    parser.add_argument("--release-cache-ref")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    base_command = [
        "docker", "buildx", "build",
        "--platform", args.platforms,
        "--file", args.dockerfile,
        "--tag", args.image,
        "--provenance=true",
        "--sbom=true",
    ]
    validation_cache = args.validation_cache_ref or args.cache_ref
    release_cache = args.release_cache_ref or args.cache_ref
    if validation_cache:
        base_command += ["--cache-from", f"type=registry,ref={validation_cache}"]
    validation_command = [*base_command]
    warnings = []
    if "," in args.platforms:
        validation_command += ["--output", "type=oci,dest=image.oci.tar", args.context]
        warnings.append("The dry-run uses an OCI archive because a multi-platform manifest cannot be loaded into the classic local image store.")
    else:
        validation_command += ["--load", args.context]
    publish_command = None
    if args.publish:
        publish_command = [part for part in base_command]
        if validation_cache and release_cache != validation_cache:
            index = publish_command.index(f"type=registry,ref={validation_cache}")
            publish_command[index] = f"type=registry,ref={release_cache}"
        if release_cache:
            publish_command += ["--cache-to", f"type=registry,ref={release_cache},mode=max"]
        publish_command += ["--push", args.context]
        if validation_cache and release_cache == validation_cache:
            warnings.append("Validation and release use the same cache reference; isolate untrusted and protected cache scopes.")
        warnings.append("Validation and publication rebuild separately; pin every input and compare the published digest with the validated artifact.")
    print(json.dumps({
        "dry_run": True,
        "image": args.image,
        "platforms": args.platforms.split(","),
        "publishes": args.publish,
        "requires_authorization": args.publish,
        "validation_command": validation_command,
        "validation_mutates_local": True,
        "validation_output_artifact": "image.oci.tar" if "," in args.platforms else "local Docker image store",
        "publish_command": publish_command,
        "post_publish": [
            ["docker", "buildx", "imagetools", "inspect", "--format", "{{json .Manifest.Digest}}", args.image],
            ["required_manual_step", "feed the resolved digest into supply-chain scans, signing, verification, and tag promotion"],
        ] if args.publish else [],
        "warnings": warnings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
