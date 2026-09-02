import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from selenium.common.exceptions import WebDriverException

from app.whatsapp_sender import WhatsAppSender
from app.main import WhatsAppSenderApp


class SenderStartupTests(unittest.TestCase):
    def test_profile_startup_failure_retries_with_temporary_profile(self) -> None:
        driver_path = Path("msedgedriver.exe")
        recovered_driver = MagicMock()

        with patch.object(Path, "is_file", return_value=True):
            with patch(
                "selenium.webdriver.Edge",
                side_effect=[
                    WebDriverException("DevToolsActivePort file doesn't exist"),
                    recovered_driver,
                ],
            ) as edge:
                sender = WhatsAppSender(
                    driver_path=driver_path,
                    profile_path=Path.cwd() / "whatsapp_edge_profile",
                )

            self.assertEqual(2, edge.call_count)
            first_options = edge.call_args_list[0].kwargs["options"]
            fallback_options = edge.call_args_list[1].kwargs["options"]
            self.assertTrue(
                any("--user-data-dir=" in arg for arg in first_options.arguments)
            )
            self.assertFalse(
                any("--user-data-dir=" in arg for arg in fallback_options.arguments)
            )
            recovered_driver.get.assert_called_once_with(WhatsAppSender.WHATSAPP_URL)
            sender.close()

    def test_cached_compatible_driver_avoids_network_download(self) -> None:
        cached_driver = Path("cached") / "msedgedriver.exe"
        driver = MagicMock()

        with (
            patch.object(
                WhatsAppSender,
                "_find_cached_compatible_driver",
                return_value=cached_driver,
            ),
            patch("webdriver_manager.microsoft.EdgeChromiumDriverManager.install")
            as download,
            patch("selenium.webdriver.Edge", return_value=driver),
        ):
            sender = WhatsAppSender(driver_path=None)

        download.assert_not_called()
        driver.get.assert_called_once_with(WhatsAppSender.WHATSAPP_URL)
        sender.close()

    def test_profile_error_detection(self) -> None:
        self.assertTrue(
            WhatsAppSender._is_profile_startup_error(
                RuntimeError("Microsoft Edge failed to start: crashed")
            )
        )
        self.assertTrue(
            WhatsAppSender._is_profile_startup_error(
                RuntimeError("failed to write prefs file")
            )
        )
        self.assertFalse(
            WhatsAppSender._is_profile_startup_error(RuntimeError("invalid argument"))
        )

    def test_technical_edge_error_is_hidden_from_interface(self) -> None:
        technical_error = RuntimeError(
            "session not created: DevToolsActivePort file doesn't exist\nStacktrace:"
        )

        result = WhatsAppSenderApp._friendly_error_message(technical_error)

        self.assertIn("Feche as outras janelas", result)
        self.assertNotIn("Stacktrace", result)

    def test_close_releases_driver(self) -> None:
        sender = object.__new__(WhatsAppSender)
        sender._attached = False
        sender._driver = MagicMock()

        sender.close()

        sender._driver.quit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
