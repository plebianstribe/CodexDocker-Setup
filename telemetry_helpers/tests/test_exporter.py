import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


class PortableExporterTests(unittest.TestCase):
    def export(self, output: Path):
        return subprocess.run(
            [
                sys.executable, "-m", "telemetry_helpers.exporter",
                "--source", str(FIXTURES / "root.jsonl"),
                "--source", str(FIXTURES / "child.jsonl"),
                "--output", str(output),
                "--run-id", "S0-DRYRUN-001",
                "--trajectory-id", "portable_fixture",
                "--root-session-id", "root-fixture",
                "--redaction-salt", "fixture-salt",
                "--requested-role", "primary",
                "--requested-model", "gpt-test",
                "--requested-effort", "high",
                "--requested-sandbox", "workspace-write",
            ],
            env=ENV, text=True, capture_output=True,
        )

    def test_export_and_verify__explicit_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "export"
            result = self.export(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            verify = subprocess.run(
                [
                    sys.executable, "-m", "telemetry_helpers.verify",
                    "--export-dir", str(output),
                    "--require-session-id", "root-fixture",
                    "--require-session-id", "child-fixture",
                ],
                env=ENV, text=True, capture_output=True,
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)
            self.assertTrue(json.loads(verify.stdout)["valid"])
            self.assertNotIn("secret-value", (output / "events.jsonl").read_text())

    def test_verify_rejects_tamper__event_changed(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "export"
            self.assertEqual(self.export(output).returncode, 0)
            events = output / "events.jsonl"
            events.write_text(events.read_text().replace("root-fixture", "tampered", 1))
            verify = subprocess.run(
                [sys.executable, "-m", "telemetry_helpers.verify", "--export-dir", str(output)],
                env=ENV, text=True, capture_output=True,
            )
            self.assertEqual(verify.returncode, 2)
            self.assertIn("event hash mismatch", verify.stderr)


if __name__ == "__main__":
    unittest.main()
