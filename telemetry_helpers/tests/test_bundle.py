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


class MultiRootBundleTests(unittest.TestCase):
    def export(self, source_root: Path, source_child: Path, output: Path, root_id: str):
        return subprocess.run([
            sys.executable, "-m", "telemetry_helpers.exporter",
            "--source", str(source_root), "--source", str(source_child),
            "--output", str(output), "--run-id", "RUN-BUNDLE-001",
            "--trajectory-id", "trajb_lite", "--root-session-id", root_id,
            "--redaction-salt", "fixture-salt",
        ], env=ENV, text=True, capture_output=True)

    def test_bundle__two_disjoint_phase_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = root / "implement"
            second = root / "verify"
            self.assertEqual(self.export(FIXTURES / "root.jsonl", FIXTURES / "child.jsonl", first, "root-fixture").returncode, 0)
            second_root = root / "root-second.jsonl"
            second_child = root / "child-second.jsonl"
            second_root.write_text((FIXTURES / "root.jsonl").read_text().replace("root-fixture", "root-second"))
            second_child.write_text(
                (FIXTURES / "child.jsonl").read_text()
                .replace("root-fixture", "root-second")
                .replace("child-fixture", "child-second")
            )
            self.assertEqual(self.export(second_root, second_child, second, "root-second").returncode, 0)
            bundled = subprocess.run([
                sys.executable, "-m", "telemetry_helpers.bundle",
                "--output", str(root / "bundle"), "--run-id", "RUN-BUNDLE-001",
                "--trajectory-id", "trajb_lite",
                "--phase-export", f"implement={first}",
                "--phase-export", f"verify={second}",
            ], env=ENV, text=True, capture_output=True)
            self.assertEqual(bundled.returncode, 0, bundled.stderr)
            manifest = json.loads((root / "bundle" / "bundle_manifest.json").read_text())
            self.assertEqual(len(manifest["phase_exports"]), 2)
            self.assertEqual(manifest["aggregate_usage"]["total"], 32)
            self.assertEqual(len(manifest["selected_sessions"]), 4)

    def test_bundle_rejects_overlap__same_export_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            phase = root / "phase"
            self.assertEqual(self.export(FIXTURES / "root.jsonl", FIXTURES / "child.jsonl", phase, "root-fixture").returncode, 0)
            result = subprocess.run([
                sys.executable, "-m", "telemetry_helpers.bundle",
                "--output", str(root / "bundle"), "--run-id", "RUN-BUNDLE-001",
                "--trajectory-id", "trajb_lite",
                "--phase-export", f"one={phase}", "--phase-export", f"two={phase}",
            ], env=ENV, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("reuses sessions", result.stderr)


if __name__ == "__main__":
    unittest.main()
