from __future__ import annotations
from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.logger import logger
from playwright.sync_api import BrowserContext
import os
import time
import random

class HandshakeAuthHandler(AuthHandler):
    """
    Handles authentication for Handshake (joinhandshake.com), which exposes a page for their Looker explores
    """

    _login_button_selector = 'text="Continue with email"'
    _login_2_button_selector = 'text="Log in another way"'
    _username_input_selector = 'input[name="identifier"]'
    _password_input_selector = 'input[name="password"]'
    _successful_login_url = "**/edu"

    def __init__(self, **kwargs):
        auth_url = kwargs.get('auth_url')
        if not isinstance(auth_url, str):
            raise ValueError("Missing or invalid required argument `auth_url`")
        self.auth_url = auth_url

    def authenticate(self, context: BrowserContext):
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME'):
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`")
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD'):
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`")

        logger.info(f"Logging in to Handshake... ({self.auth_url})")

        page = context.new_page()
        page.goto(f"{self.auth_url}")
        page.wait_for_selector(self._login_button_selector)
        page.click(self._login_button_selector)

        # Insert username
        page.wait_for_selector(self._username_input_selector)
        HandshakeAuthHandler._random_wait(1000, 2000)
        username = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME')
        if username is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`")
        page.fill(self._username_input_selector, username)
        username = None
        HandshakeAuthHandler._random_wait()
        page.press(self._username_input_selector, "Enter")

        # Wait for the (second) login button to appear because Handshake is silly and requires an extra click (for no reason)
        page.wait_for_selector(self._login_2_button_selector)
        HandshakeAuthHandler._random_wait()
        page.click(self._login_2_button_selector)

        # Insert password
        page.wait_for_selector(self._password_input_selector)
        HandshakeAuthHandler._random_wait(1000, 2000)
        password = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD')
        if password is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`")
        page.fill(self._password_input_selector, password)
        password = None
        HandshakeAuthHandler._random_wait()
        page.press(self._password_input_selector, "Enter")

        page.wait_for_url("**/edu")
        logger.info(f"Successfully logged in to Handshake")
        page.close()
        HandshakeAuthHandler._random_wait(500, 1500)

    @staticmethod
    def _random_wait(min_time: int = 100, max_time: int = 1000):
            wait_time = random.randint(min_time, max_time)
            logger.info(f"Waiting for {wait_time}ms...")
            time.sleep(wait_time / 1000)