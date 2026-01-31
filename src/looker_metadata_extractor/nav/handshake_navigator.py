from __future__ import annotations
import random

from looker_metadata_extractor.nav.navigator import Navigator
from looker_metadata_extractor.utils.logger import logger
from looker_metadata_extractor.nav.extractor_context import ExtractorContext
from looker_metadata_extractor.auth.auth_handler import AuthHandlerType
from looker_metadata_extractor.auth.general_auth_handler import GeneralAuthHandler
from looker_metadata_extractor.auth.handshake_auth_handler import HandshakeAuthHandler
from looker_metadata_extractor.auth.no_auth_handler import NoAuthHandler
from looker_metadata_extractor.extract.extract import Extract


class HandshakeNavigator(Navigator):
    """
    Navigator for Handshake (joinhandshake.com) Looker explores
    """

    def __init__(self, **kwargs):
        auth_kwargs = kwargs.get("auth")
        context_kwargs = kwargs.get("context")

        if not auth_kwargs:
            raise ValueError("Missing required argument `auth`")
        if not context_kwargs:
            raise ValueError("Missing required argument `context`")
        if not context_kwargs.get("cookie_url"):
            raise ValueError("Missing required argument `cookie_url` in `context`")
        
        auth_handler_type = AuthHandlerType.from_string(auth_kwargs.get("handler", "general"))
        if auth_handler_type == AuthHandlerType.HANDSHAKE:
            auth_handler = HandshakeAuthHandler(**auth_kwargs)
        elif auth_handler_type == AuthHandlerType.NONE:
            auth_handler = NoAuthHandler()
        else:
            auth_handler = GeneralAuthHandler(**auth_kwargs)

        self._context = ExtractorContext(auth=auth_handler, **context_kwargs)
        self._extract_timeout = kwargs.get("extract_timeout", HandshakeNavigator.DEFAULT_TIMEOUT_MS)

    @property
    def context(self) -> ExtractorContext:
        return self._context
    @property
    def extract_timeout(self) -> int:
        return self._extract_timeout

    def set_context(self, context: ExtractorContext):
        self._context = context

    def navigate_and_extract(self, url: str, extracts: list[Extract], custom_timeout: int | None = None) -> list[Extract]:
        logger.info(f"Navigating to: {url}")
        for item in extracts:
            item.status = "idle"

        def handle_responses(response):
            for extract in extracts:
                try:
                    if not extract.meets_conditions(response):
                        continue
                    response_json = response.json()
                    if not extract.json_meets_conditions(response_json):
                        continue
                    
                    logger.info(f"Intercepted query response from {response.url}")
                    extract.status = "processing"
                    data_items = extract.extract_data(response_json)

                    if data_items is None or len(data_items) == 0:
                        logger.warning(f"No data items extracted from response {response.url}")
                        return
                    logger.info(f"Extracted {len(data_items)} items from response {response.url}")
                    extract.status = "success"

                    for item in data_items:
                        extract.add_data_item(item)
                    logger.info(f"Finished processing response {response.url}")
                except Exception:
                    logger.warning(f"Failed to handle query response from {response.url}")
                    logger.debug(f"Response headers: {response.headers}")
                    logger.debug(f"Response content: {response.text}")
                    logger.debug(f"Response status: {response.status}")
                    extract.status = "failed"
                    return

        page = self.context.open_page_with_response_handler(url, handle_responses)
        logger.info(f"Waiting for navigation to URL: {url}. Current URL: {page.url}")
        try:
            page.wait_for_url(url, timeout=custom_timeout if custom_timeout is not None else self.extract_timeout)
            logger.info(f"Successfully navigated to: {url}")
        except Exception:
            logger.warning(f"Timeout waiting for navigation to URL: {url}. Current URL: {page.url}")

        def wait_for_extractions_to_load():
            # Wait for all status to be updated to "success" or "failed"
            timeout = custom_timeout if custom_timeout is not None else self.extract_timeout
            start_time = page.evaluate("performance.now()")
            while not all(extract.status in ["success", "failed"] for extract in extracts) and (page.evaluate("performance.now()") - start_time) < timeout:
                page.wait_for_timeout(HandshakeNavigator.POLLING_INTERVAL_MS)
            if (page.evaluate("performance.now()") - start_time) >= timeout:
                logger.warning(f"Timed out waiting for extractions to load")
        logger.info(f"Waiting for extractions to load...")
        for item in extracts:
            item.status = "waiting"
        wait_for_extractions_to_load()
        HandshakeNavigator._close_page_after_random_wait(page)

        for item in extracts:
            if item.status == "waiting":
                item.status = "timed_out"

        extract_statuses = {extract.type.value: extract.status for extract in extracts}
        if all(item.status == "success" for item in extracts):
            logger.info(f"All extractions loaded successfully. {extract_statuses}")
        else:
            logger.warning(f"One or more extractions failed to load. {extract_statuses}")
        return extracts

    @staticmethod
    def _close_page_after_random_wait(page):
        wait_time = random.randint(1000, 5000)
        logger.info(f"Waiting for {wait_time}ms before closing page...")
        page.wait_for_timeout(wait_time)
        page.close()