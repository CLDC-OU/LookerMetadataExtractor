from __future__ import annotations
from fnmatch import fnmatch
import os
import time
import random
from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeoutError

from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.utils.logger import logger


class HandshakeAuthHandler(AuthHandler):
    """
    Handles authentication for Handshake (joinhandshake.com), which exposes a page for their Looker explores
    """

    _login_button_selector = 'text="Continue with email"'
    _login_2_button_selector = 'text="Log in another way"'
    _username_input_selector = 'input[name="identifier"]'
    _password_input_selector = 'input[name="password"]'
    _successful_login_url = "**/edu"
    
    _poll_interval_ms = 250
    _max_wait_time_ms = 60_000

    def __init__(self, **kwargs):
        auth_url = kwargs.get('auth_url')
        if not isinstance(auth_url, str):
            raise ValueError("Missing or invalid required argument `auth_url`")
        self.auth_url = auth_url
        
        successful_login_url = kwargs.get('successful_login_url')
        if not isinstance(successful_login_url, str):
            raise ValueError("Missing or invalid required argument `successful_login_url`")
        self._successful_login_url = successful_login_url

    def authenticate(self, context: BrowserContext):
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME'):
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`")
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD'):
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`")

        logger.info("Starting Handshake authentication handler...")

        page = context.new_page()
        logged_in = {"value": False}
        
        def _on_frame_navigated(frame):
            try:
                if frame == page.main_frame and self._url_matches_success(page.url):
                    logged_in["value"] = True
            except Exception:
                pass

        page.on("framenavigated", _on_frame_navigated)

        def _terminate_successfully_if_logged_in():
            if logged_in["value"] or self._url_matches_success(page.url):
                logger.info("Detected successful login URL - terminating authentication successfully.")
                try:
                    page.close()
                except Exception:
                    pass
                HandshakeAuthHandler._random_wait(500, 1500)
                return True
            return False

        logger.info(f"Logging in to Handshake... ({self.auth_url})")
        page.goto(self.auth_url)
        if _terminate_successfully_if_logged_in():
            return
        
        HandshakeAuthHandler._random_wait()
        logger.info("Waiting for login button...")
        self._wait_for_selector_interruptible(page, self._login_button_selector, _terminate_successfully_if_logged_in)
        if _terminate_successfully_if_logged_in():
            return
        page.click(self._login_button_selector)
        logger.info("Login button clicked")
        if _terminate_successfully_if_logged_in():
            return

        # ===== Username =====
        logger.info("Waiting for username input...")
        self._wait_for_selector_interruptible(page, self._username_input_selector, _terminate_successfully_if_logged_in)
        if _terminate_successfully_if_logged_in():
            return
        
        HandshakeAuthHandler._random_wait(1000, 2000)
        if _terminate_successfully_if_logged_in():
            return
        
        username = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME')
        if username is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`")
        page.fill(self._username_input_selector, username)
        username = None
        logger.info("Username input filled")
        if _terminate_successfully_if_logged_in():
            return

        HandshakeAuthHandler._random_wait()
        if _terminate_successfully_if_logged_in():
            return
        page.press(self._username_input_selector, "Enter")
        logger.info("Username submitted")
        if _terminate_successfully_if_logged_in():
            return

        # Wait for the (second) login button to appear because Handshake is silly and requires an extra click (for no reason)
        logger.info("Waiting for second login button...")
        self._wait_for_selector_interruptible(page, self._login_2_button_selector, _terminate_successfully_if_logged_in)
        if _terminate_successfully_if_logged_in():
            return
        HandshakeAuthHandler._random_wait()
        if _terminate_successfully_if_logged_in():
            return
        page.click(self._login_2_button_selector)
        logger.info("Second login button clicked")
        if _terminate_successfully_if_logged_in():
            return

        # ===== Password =====
        logger.info("Waiting for password input...")
        self._wait_for_selector_interruptible(page, self._password_input_selector, _terminate_successfully_if_logged_in)
        if _terminate_successfully_if_logged_in():
            return
        
        HandshakeAuthHandler._random_wait(1000, 2000)
        if _terminate_successfully_if_logged_in():
            return

        password = os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD')
        if password is None:
            raise ValueError("Missing required environment variable `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`")
        
        # NOTE: Assumes password locator is focused. Since the input is of type password, we can't interact with it normally so we use hardcoded navigation and keyboard typing
        logger.info("Filling password input...")
        page.keyboard.type(password, delay=44)
        password = None
        logger.info("Password input filled")
        if _terminate_successfully_if_logged_in():
            return
        HandshakeAuthHandler._random_wait()
        if _terminate_successfully_if_logged_in():
            return

        logger.info("Submitting password...")
        page.keyboard.press("Enter")
        logger.info("Password submitted")
        if _terminate_successfully_if_logged_in():
            return

        logger.info(f"Waiting for successful login... Current URL: {page.url}")
        self._wait_for_url_interruptible(page, self._successful_login_url, _terminate_successfully_if_logged_in)
        if _terminate_successfully_if_logged_in():
            return

        logger.warning("Failed to complete login successfully - closing page")
        page.close()

    @staticmethod
    def _random_wait(min_time: int = 100, max_time: int = 1000):
            wait_time = random.randint(min_time, max_time)
            logger.info(f"Waiting for {wait_time}ms...")
            time.sleep(wait_time / 1000)

    def _url_matches_success(self, current_url: str) -> bool:
        pattern = self._successful_login_url or ""
        if "*" in pattern or "?" in pattern:
            glob_pattern = pattern.replace("**", "*")
            return fnmatch(current_url, glob_pattern)
        return current_url.startswith(pattern)

    def _wait_for_selector_interruptible(self, page, selector: str, should_stop) -> None:
        deadline = time.time() + (self._max_wait_time_ms / 1000)
        while True:
            if should_stop():
                return
            try:
                page.wait_for_selector(selector, timeout=self._poll_interval_ms)
                return
            except PlaywrightTimeoutError:
                if time.time() >= deadline:
                    raise

    def _wait_for_load_state_interruptible(self, page, state: str, should_stop) -> None:
        deadline = time.time() + (self._max_wait_time_ms / 1000)
        while True:
            if should_stop():
                return
            try:
                page.wait_for_load_state(state, timeout=self._poll_interval_ms)
                return
            except PlaywrightTimeoutError:
                if time.time() >= deadline:
                    raise

    def _wait_for_url_interruptible(self, page, url_pattern: str, should_stop) -> None:
        deadline = time.time() + (self._max_wait_time_ms / 1000)
        while True:
            if should_stop():
                return
            try:
                page.wait_for_url(url_pattern, timeout=self._poll_interval_ms)
                return
            except PlaywrightTimeoutError:
                if time.time() >= deadline:
                    raise
