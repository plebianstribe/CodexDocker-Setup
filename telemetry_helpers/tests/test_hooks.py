import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


class LifecycleHookTests(unittest.TestCase):
    def run_hook(self, *args: str):
        return subprocess.run(
            [sys.executable, "-m", "telemetry_helpers.hooks", *args],
            env=ENV, text=True, capture_output=True,
        )

    def test_hash_chain_and_artifact_binding__two_events(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root / "telemetry"
            artifact = root / "checkpoint.json"
            artifact.write_text('{"status":"pass"}\n')
            init = self.run_hook(
                "init", "--run-dir", str(run), "--run-id", "RUN-001",
                "--trajectory-id", "trajb_lite", "--artifact-root", str(root),
                "--created-at-utc", "2026-08-03T12:00:00Z",
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            first = self.run_hook(
                "record", "--run-dir", str(run), "--event-type", "phase_started",
                "--phase", "implement", "--status", "started",
                "--timestamp-utc", "2026-08-03T12:01:00Z",
                "--root-session-id", "root-1",
            )
            second = self.run_hook(
                "record", "--run-dir", str(run), "--event-type", "checkpoint_frozen",
                "--phase", "implement", "--status", "completed",
                "--timestamp-utc", "2026-08-03T12:02:00Z",
                "--root-session-id", "root-1", "--artifact", str(artifact),
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            verified = self.run_hook("verify", "--run-dir", str(run))
            self.assertEqual(verified.returncode, 0, verified.stderr)
            value = json.loads(verified.stdout)
            self.assertEqual(value["event_count"], 2)
            self.assertEqual(value["root_session_ids"], ["root-1"])

    def test_verify_rejects_tamper__artifact_changed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root / "telemetry"
            artifact = root / "checkpoint.json"
            artifact.write_text("before\n")
            self.assertEqual(self.run_hook(
                "init", "--run-dir", str(run), "--run-id", "RUN-002",
                "--trajectory-id", "trajb", "--artifact-root", str(root),
                "--created-at-utc", "2026-08-03T12:00:00Z",
            ).returncode, 0)
            self.assertEqual(self.run_hook(
                "record", "--run-dir", str(run), "--event-type", "checkpoint_frozen",
                "--phase", "join", "--status", "completed",
                "--timestamp-utc", "2026-08-03T12:01:00Z", "--artifact", str(artifact),
            ).returncode, 0)
            artifact.write_text("after\n")
            checked = self.run_hook("verify", "--run-dir", str(run))
            self.assertEqual(checked.returncode, 2)
            self.assertIn("artifact hash mismatch", checked.stderr)

    def test_init_refuses_overwrite__existing_log(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "telemetry"
            args = (
                "init", "--run-dir", str(run), "--run-id", "RUN-003",
                "--trajectory-id", "trajb", "--artifact-root", temp,
                "--created-at-utc", "2026-08-03T12:00:00Z",
            )
            self.assertEqual(self.run_hook(*args).returncode, 0)
            repeated = self.run_hook(*args)
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("refusing to overwrite", repeated.stderr)

    def test_concurrent_records__serialized_hash_chain(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "telemetry"
            self.assertEqual(self.run_hook(
                "init", "--run-dir", str(run), "--run-id", "RUN-004",
                "--trajectory-id", "trajb", "--artifact-root", temp,
                "--created-at-utc", "2026-08-03T12:00:00Z",
            ).returncode, 0)
            commands = []
            for index in range(8):
                commands.append([
                    sys.executable, "-m", "telemetry_helpers.hooks", "record",
                    "--run-dir", str(run), "--event-type", "phase_started",
                    "--phase", f"worker_{index}", "--status", "started",
                    "--timestamp-utc", "2026-08-03T12:01:00Z",
                    "--agent-session-id", f"agent-{index}",
                ])
            processes = [subprocess.Popen(command, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for command in commands]
            results = [process.communicate() + (process.returncode,) for process in processes]
            self.assertTrue(all(code == 0 for _, _, code in results), results)
            verified = self.run_hook("verify", "--run-dir", str(run))
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertEqual(json.loads(verified.stdout)["event_count"], 8)


if __name__ == "__main__":
    unittest.main()
