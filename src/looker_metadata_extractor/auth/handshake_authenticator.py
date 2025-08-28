from looker_metadata_extractor.auth.authenticator import Authenticator
from looker_metadata_extractor.extractor_context import ExtractorContext
from ..logger import logger
import os

class HandshakeAuthenticator(Authenticator):
    """
    Handles authentication for Handshake (joinhandshake.com), which exposes a page for their Looker explores
    """

    _login_button_selector = 'text="Continue with email"'
    _username_input_selector = 'input[name="identifier"]'
    _password_input_selector = 'input[name="password"]'

    def __init__(self):
        super().__init__()
        self.auth_url = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_URL')
        if self.auth_url is None:
            raise ValueError("Missing required environment variables")

    def authenticate(self, context: ExtractorContext):
        logger.info(f"Logging in to Handshake... ({self.auth_url})")

        browser_context = context._get_context()
        if browser_context is None:
            context._new_context()
            browser_context = context._get_context()
        if browser_context is None:
            raise ValueError("Failed to create new browser context")

        page = browser_context.new_page()
        page.goto(f"{self.auth_url}")
        page.wait_for_selector(self._login_button_selector)
        page.click(self._login_button_selector)

        # Insert username
        page.wait_for_selector(self._username_input_selector)
        username = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME')
        if username is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`")
        page.fill(self._username_input_selector, username)
        username = None
        page.press(self._username_input_selector, "Enter")

        # Wait for the login button to appear again because Handshake is silly and requires an extra click (for no reason)
        page.wait_for_selector(self._login_button_selector)
        page.click(self._login_button_selector)

        # Insert password
        page.wait_for_selector(self._password_input_selector)
        password = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD')
        if password is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`")
        page.fill(self._password_input_selector, password)
        password = None
        page.press(self._password_input_selector, "Enter")

        page.wait_for_url("**/edu")
        logger.info(f"Successfully logged in to Handshake")
