import tempfile
import unittest
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_ota_zip import validate


class ValidateOtaZipTests(unittest.TestCase):
    def make_zip(self, root: Path, name: str, entries: dict[str, str]) -> Path:
        path = root / name
        with zipfile.ZipFile(path, "w") as archive:
            for member, content in entries.items():
                archive.writestr(member, content)
        return path

    def test_accepts_payload_ota_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_zip(Path(tmp), "ota.zip", {"payload.bin": "payload"})
            validate(path)

    def test_accepts_recovery_update_binary_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_zip(
                Path(tmp), "ota.zip",
                {"META-INF/com/google/android/update-binary": "script"},
            )
            validate(path)

    def test_rejects_non_ota_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.make_zip(Path(tmp), "other.zip", {"readme.txt": "text"})
            with self.assertRaisesRegex(ValueError, "OTA marker"):
                validate(path)

    def test_rejects_non_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.zip"
            path.write_text("not a zip")
            with self.assertRaisesRegex(ValueError, "valid ZIP"):
                validate(path)


if __name__ == "__main__":
    unittest.main()
