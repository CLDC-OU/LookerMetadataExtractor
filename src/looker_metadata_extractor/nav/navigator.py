from ..extractor_context import ExtractorContext
from ..auth.authenticator import Authenticator
from ..logger import logger
from playwright.sync_api import Page
from typing import Callable

class Navigator:
    """
    Base class for all navigators
    """

    def __init__(self):
        self.context = ExtractorContext(Authenticator(), '', [])

    def navigate(self, url: str, reuse_context: bool = True):
        logger.info(f"Navigating to: {url}")
        def handle_responses(response):
            pass
        page = self.context.open_page_with_response_handler(url, handle_responses, reuse_context=reuse_context)
        return page