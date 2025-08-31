from __future__ import annotations
from looker_metadata_extractor.utils.logger import logger
from playwright.sync_api import Page
from typing import Callable
from enum import Enum

from looker_metadata_extractor.extractor_context import ExtractorContext
from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.extract.extract import Extract, ExtractType

class NavigatorType(Enum):
    UNKNOWN = "unknown"
    HANDSHAKE = "handshake"

    @staticmethod
    def from_string(type_str: str) -> NavigatorType:
        try:
            return NavigatorType[type_str.upper()]
        except KeyError:
            return NavigatorType.UNKNOWN

class Navigator:
    """
    Base class for all navigators
    """

    def __init__(self, **kwargs):
        self.context = ExtractorContext(AuthHandler(**kwargs), '', [], True, False)

    def set_context(self, context: ExtractorContext):
        self.context = context

    def navigate_and_extract(self, url: str, extracts: list[Extract], reuse_context: bool = True) -> list[Extract]:
        logger.info(f"Navigating to: {url}")
        def handle_responses(response):
            pass
        page = self.context.open_page_with_response_handler(url, handle_responses, reuse_context=reuse_context)
        return extracts