from __future__ import annotations
from playwright.sync_api import sync_playwright, BrowserContext, Page
from typing import Callable

from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.utils.logger import logger

class ExtractorContext:
    """
    Holds the context for the extractor, including authentication and browser instance
    """

    def __init__(self, auth: AuthHandler, cookie_url: str, required_cookies: list[str], run_headless: bool, reuse_context: bool):
        self.auth = auth
        self.cookie_url = cookie_url
        self.required_cookies = required_cookies
        self.current_page = None
        self.run_headless = run_headless
        self.reuse_context = reuse_context
        self.context = None

    def _get_context(self) -> BrowserContext | None:
        if self.context:
            return self.context
        return None

    def _new_context(self) -> BrowserContext:
        if not self.context:
            logger.info("Starting new browser instance...")
            if self.reuse_context:
                self.context = sync_playwright().start().chromium.launch_persistent_context(user_data_dir="./user_data", headless=self.run_headless)
            else:
                logger.info("Creating new browser context...")
                browser = sync_playwright().start().chromium.launch(headless=self.run_headless)
                self.context = browser.new_context()
        return self.context


    def cleanup(self) -> None:
        if self.context:
            logger.info("Closing browser instance...")
            self.context.close()
            self.context = None

    def is_authenticated(self) -> bool:
        context = self._get_context()
        if context is None:
            return False
        cookies = context.cookies(self.cookie_url)
        return all(cookie in cookies for cookie in self.required_cookies)

    def open_page(self, url: str, reuse_context: bool = True) -> Page:
        logger.info(f"Opening page: {url}")
        page = self._get_or_load_authenticated_page(reuse_context=reuse_context)
        page.goto(url)
        self.current_page = page
        return page

    def open_page_with_response_handler(self, url: str, response_handler: Callable, reuse_context: bool = True):
        logger.info(f"Opening page with response handler: {url}")
        page = self._get_or_load_authenticated_page(reuse_context=reuse_context)
        if not self._get_context():
            raise ValueError("No browser context available")
        page.on("response", response_handler)
        page.goto(url)
        self.current_page = page
        return page

    def _get_authenticated_page(self) -> Page:
        context = self._get_context()
        if context is None:
            context = self._new_context()
        if not self.is_authenticated():
            self.auth.authenticate(context)
        page = context.new_page()
        return page

    def _get_or_load_authenticated_page(self, reuse_context: bool = True) -> Page:
        if not reuse_context:
            if self.current_page:
                self.current_page.close()
                self.current_page = None
            self._new_context()

        if reuse_context and self.current_page:
            return self.current_page
        else:
            return self._get_authenticated_page()
