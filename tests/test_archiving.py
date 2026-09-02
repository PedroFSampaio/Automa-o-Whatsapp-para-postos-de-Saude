import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app.main import WhatsAppSenderApp


class ArchivingTests(unittest.TestCase):
    def test_pdf_is_archived_beside_executable_by_month(self) -> None:
        source = Path("C:/imports/agenda.pdf")
        executable = Path("C:/app/dist/WhatsApp Message Sender.exe")

        with (
            patch.object(Path, "resolve", lambda path: path),
            patch.object(Path, "mkdir"),
            patch.object(Path, "exists", return_value=False),
            patch("app.main.sys.frozen", True, create=True),
            patch("app.main.sys.executable", str(executable)),
            patch("app.main.datetime") as mocked_datetime,
            patch("app.main.shutil.copy2") as copy_file,
        ):
            mocked_datetime.now.return_value = datetime(2026, 9, 2)
            destination = WhatsAppSenderApp._archive_batch_file(source)

        expected = Path("C:/app/dist/documentos/pdf/Setembro/agenda.pdf")
        self.assertEqual(expected, destination)
        copy_file.assert_called_once_with(source, expected)

    def test_csv_is_not_archived(self) -> None:
        with patch.object(Path, "resolve", lambda path: path):
            destination = WhatsAppSenderApp._archive_batch_file(
                Path("C:/imports/lista.csv")
            )

        self.assertIsNone(destination)


if __name__ == "__main__":
    unittest.main()
