from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(relative: str, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["python3", str(ROOT / relative), *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result


def load_smoke_module():
    path = ROOT / "skills/docker-workflows/scripts/smoke_test.py"
    spec = importlib.util.spec_from_file_location("docker_smoke_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class HelperTests(unittest.TestCase):
    def test_smoke_health_semantics(self):
        smoke = load_smoke_module()
        self.assertTrue(smoke.service_ready('{"State":"running","Health":"healthy"}'))
        self.assertTrue(smoke.service_ready('{"State":"running","Health":""}'))
        self.assertFalse(smoke.service_ready('{"State":"running","Health":"unhealthy"}'))
        self.assertFalse(smoke.service_ready('{"State":"exited","Health":""}'))

    def test_compose_and_ops_overlay_validate(self):
        base = run_script(
            "skills/docker-workflows/scripts/generate_compose.py",
            "--service", "api", "--port", "8080", "--postgres", "--redis",
        ).stdout
        self.assertIn("redis-data:/data", base)
        self.assertIn("DATABASE_URL: ${DATABASE_URL:?", base)
        overlay = run_script(
            "skills/docker-operations/scripts/generate_ops_overlay.py",
            "--service", "api", "--otel-endpoint", "http://otel:4317",
        ).stdout
        if shutil.which("docker"):
            with tempfile.TemporaryDirectory() as directory:
                base_path = Path(directory) / "compose.yaml"
                overlay_path = Path(directory) / "ops.yaml"
                base_path.write_text(base, encoding="utf-8")
                overlay_path.write_text(overlay, encoding="utf-8")
                environment = os.environ | {
                    "POSTGRES_PASSWORD": "test-only",
                    "DATABASE_URL": "postgresql://app:test-only@db:5432/app",
                }
                result = subprocess.run(
                    ["docker", "compose", "-f", str(base_path), "-f", str(overlay_path), "config", "--quiet"],
                    check=False,
                    text=True,
                    capture_output=True,
                    env=environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_data_plans_expand_inside_container(self):
        result = run_script(
            "skills/docker-operations/scripts/data_plan.py",
            "--engine", "postgres", "--action", "backup", "--service", "db",
        )
        plan = json.loads(result.stdout)
        self.assertTrue(plan["requires_authorization"])
        self.assertEqual(plan["stream_direction"], "stdout-to-explicit-backup-file")
        self.assertIn("POSTGRES_PASSWORD", " ".join(plan["command_template"]))
        self.assertNotIn("$DATABASE_URL", " ".join(plan["command_template"]))

    def test_platform_generators(self):
        invalid = run_script(
            "skills/docker-platforms/scripts/generate_platform_asset.py",
            "kubernetes", "--name", "app", "--image", "example/app@sha256:deadbeef", "--port", "8080",
            check=False,
        )
        self.assertNotEqual(invalid.returncode, 0)
        dockerfile = run_script(
            "skills/docker-platforms/scripts/generate_framework_dockerfile.py",
            "--framework", "nextjs", "--package-manager", "pnpm", "--port", "3000",
        ).stdout
        self.assertIn("pnpm install --frozen-lockfile", dockerfile)
        self.assertIn("CMD [\"node\", \"server.js\"]", dockerfile)

    def test_supply_chain_requires_digest_for_signing(self):
        plan = json.loads(run_script(
            "skills/docker-supply-chain/scripts/supply_chain_plan.py",
            "--image", "ghcr.io/example/app:1.0.0", "--sign",
        ).stdout)
        sign = next(step for step in plan["steps"] if step["operation"] == "sign")
        self.assertTrue(sign["requires_authorization"])
        self.assertIsNotNone(sign["blocked_by"])
        scan = next(step for step in plan["steps"] if step["operation"] == "scan")
        self.assertIn("1", scan["command"])

    def test_release_separates_validation_and_publish(self):
        plan = json.loads(run_script(
            "skills/docker-release/scripts/release_plan.py",
            "--image", "ghcr.io/example/app:1.0.0", "--publish",
        ).stdout)
        self.assertTrue(plan["requires_authorization"])
        self.assertIn("--output", plan["validation_command"])
        self.assertNotIn("--push", plan["validation_command"])
        self.assertIn("--push", plan["publish_command"])


if __name__ == "__main__":
    unittest.main()
