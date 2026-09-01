from pathlib import Path
from urllib.parse import quote


class WhatsAppSender:
    """Controls WhatsApp Web through Microsoft Edge only."""

    WHATSAPP_URL = "https://web.whatsapp.com"
    CHAT_TIMEOUT = 45

    def __init__(
        self,
        driver_path: Path | None = None,
        profile_path: Path | None = None,
        debugger_address: str | None = None,
    ) -> None:
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.edge.options import Options
            from selenium.webdriver.edge.service import Service
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support import expected_conditions as expected
            from selenium.webdriver.support.ui import WebDriverWait
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
        except ImportError as error:
            raise RuntimeError(
                "Para enviar pelo WhatsApp Web, instale as dependencias com: "
                "pip install -r requirements.txt"
            ) from error

        if driver_path is not None:
            if not driver_path.is_file() or driver_path.name.lower() != "msedgedriver.exe":
                raise RuntimeError(
                    "Microsoft Edge WebDriver nao encontrado. "
                    f"Esperado: {driver_path}"
                )
            resolved_driver_path = driver_path
        else:
            try:
                resolved_driver_path = Path(EdgeChromiumDriverManager().install())
            except Exception as error:
                raise RuntimeError(
                    "Nao foi possivel baixar o Microsoft Edge WebDriver automaticamente. "
                    "Verifique a conexao com a internet ou instale o msedgedriver.exe "
                    "manualmente em Downloads\\edgedriver_win64."
                ) from error

        self._by = By
        self._keys = Keys
        self._expected = expected
        self._wait = WebDriverWait
        options = Options()
        self._profile_path = profile_path or Path.home() / "whatsapp_edge_profile"
        self._profile_path.mkdir(parents=True, exist_ok=True)
        self._attached = bool(debugger_address)
        if debugger_address:
            # Attach to an Edge instance started with --remote-debugging-port.
            options.add_experimental_option("debuggerAddress", debugger_address)
        else:
            options.add_argument(f"--user-data-dir={self._profile_path}")
            options.add_argument("--profile-directory=Default")
            options.add_argument("--start-maximized")
        self._driver = webdriver.Edge(
            service=Service(str(resolved_driver_path)),
            options=options,
        )
        self._driver.set_page_load_timeout(self.CHAT_TIMEOUT)
        self._driver.get(self.WHATSAPP_URL)

    def check_connection(self) -> bool:
        try:
            return "web.whatsapp.com" in self._driver.current_url
        except Exception:
            return False

    def send(self, phone: str, message: str) -> None:
        if not phone or not phone.isdigit():
            raise ValueError("Telefone invalido")

        # Build the URL
        url = f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}"
        
        # Use the most direct approach - navigate to the URL
        # This is necessary to open the chat window
        self._driver.get(url)
        
        # Wait for the message box to be interactive (handles page load)
        message_box = self._wait(self._driver, self.CHAT_TIMEOUT).until(
            self._expected.element_to_be_clickable(
                (
                    self._by.XPATH,
                    "//div[@contenteditable='true' and @role='textbox']",
                )
            )
        )
        message_box.send_keys(self._keys.RETURN)

    def close(self) -> None:
        if self._driver and not self._attached:
            self._driver.quit()
