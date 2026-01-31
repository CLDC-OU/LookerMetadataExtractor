from __future__ import annotations
from playwright.sync_api import sync_playwright, BrowserContext, Page
from playwright_stealth import Stealth
from typing import Callable

from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.nav.context_injector import ContextInjector
from looker_metadata_extractor.utils.logger import logger


class ExtractorContext:
    """
    Holds the context for the extractor, including authentication and browser instance
    """

    def __init__(self, auth: AuthHandler, **kwargs):
        self.auth = auth
        self.cookie_url = kwargs.get("cookie_url")
        self.required_cookies = kwargs.get("required_cookies", [])
        self.headless = kwargs.get("headless", True)
        self.reuse_context = kwargs.get("reuse_context", False)
        self.user_data_directory = kwargs.get("user_data_directory")
        if self.reuse_context and not self.user_data_directory:
            raise ValueError("User data directory must be specified when reuse_context is True")
        
        self.injectors: list[ContextInjector] = []
        added_injectors = set()
        injectors_config = kwargs.get("injectors", [])
        for injector_config in injectors_config:
            if injector_config.get("type") == "flaresolverr" and "flaresolverr" not in added_injectors:
                from looker_metadata_extractor.nav.flaresolverr_injector import FlareSolverrInjector
                self.injectors.append(FlareSolverrInjector(**injector_config))
                added_injectors.add("flaresolverr")
        self.current_page = None
        self._context = None

    @property
    def context(self) -> BrowserContext | None:
        if self._context:
            return self._context
        return None

    def cleanup(self) -> None:
        if self.context:
            logger.info("Closing browser instance...")
            self.context.close()
            self._context = None

    def is_authenticated(self) -> bool:
        context = self.context
        if context is None:
            return False
        cookies = context.cookies(self.cookie_url)
        return all(cookie in cookies for cookie in self.required_cookies)

    def open_page(self, url: str) -> Page:
        page = self._get_or_load_authenticated_page()
        logger.info(f"Opening page: {url}")
        page.goto(url)
        self.current_page = page
        return page

    def open_page_with_response_handler(self, url: str, response_handler: Callable):
        page = self._get_or_load_authenticated_page()
        if not self.context:
            raise ValueError("No browser context available")
        page.on("response", response_handler)
        logger.info(f"Opening page with response handler: {url}")
        page.goto(url)
        self.current_page = page
        return page


    def _determine_user_agent(self) -> str | None:
        """
        Selects the highest priority user agent from the included context injectors

        Returns:
            str | None: The highest priority user agent string from the context injectors, or None if none are preferred
        """
        highest_priority = float('-inf')
        selected_user_agent = None
        for injector in self.injectors:
            ua = injector.user_agent
            if ua and injector.user_agent_priority > highest_priority:
                highest_priority = injector.user_agent_priority
                selected_user_agent = ua
        return selected_user_agent

    def _new_context(self) -> BrowserContext:
        if self.context:
            return self.context
        
        logger.info("Starting new browser instance...")
        user_agent = self._determine_user_agent()
        logger.info(f"Using User-Agent: {user_agent}")
        if self.reuse_context:
            if not self.user_data_directory:
                raise ValueError("User data directory must be specified when reuse_context is True")
            self._context = Stealth().use_sync(sync_playwright()).manager.start().chromium.launch_persistent_context(user_data_dir=self.user_data_directory, headless=self.headless, user_agent=user_agent)
        else:
            browser = Stealth().use_sync(sync_playwright()).manager.start().chromium.launch(headless=self.headless)
            logger.info("Creating new browser context...")
            self._context = browser.new_context(user_agent=user_agent)
        logger.info(f"Injecting context modifications for {len(self.injectors)} injectors...")
        for injector in self.injectors:
            injector.inject(self._context)
        return self._context

    def _get_authenticated_page(self) -> Page:
        context = self.context
        if context is None:
            context = self._new_context()
        if not self.is_authenticated():
            try:
                logger.info("Not authenticated - starting authentication process...")
                self.auth.authenticate(context)
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                raise e
        page = context.new_page()
        return page

    def _get_or_load_authenticated_page(self) -> Page:
        if not self.reuse_context:
            if self.current_page:
                self.current_page.close()
                self.current_page = None
            self._new_context()

        if self.reuse_context and self.current_page:
            return self.current_page
        else:
            return self._get_authenticated_page()
