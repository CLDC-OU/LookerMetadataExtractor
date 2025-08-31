from .navigator import Navigator
from ..logger import logger
from ..extractor_context import ExtractorContext
from playwright.sync_api import Page
from ..auth.handshake_authenticator import HandshakeAuthenticator
import os

class HandshakeNavigator(Navigator):
    """
    Navigator for Handshake (joinhandshake.com) Looker explores
    """

    def __init__(self, **kwargs):
        cookie_url = kwargs.get('cookie_url')
        required_cookies = kwargs.get('required_cookies', [])
        if not cookie_url:
            raise ValueError("Missing required argument `cookie_url`")
        self.context = ExtractorContext(
            auth=GeneralAuthHandler(**kwargs), 
            cookie_url=cookie_url, 
            required_cookies=required_cookies,
        )
    
    def navigate_and_extract(self, url: str, extract_types: list[str], reuse_context: bool = True) -> Page:
        logger.info(f"Navigating to: {url}")
        self.queries = []
        self.status = {}
        for item in extract_types:
            self.status[item] = "idle"

        def handle_responses(response):
            if "queries" in extract_types and "/queries" in response.url and response.request.method == "POST":
                try:
                    response_json = response.json()
                    # Only accept responses that are a list of JSON objects with the "id" field. This is how all Handshake reports should be structured
                    if not isinstance(response_json, list) or not all(
                        isinstance(item, dict) and "id" in item.keys()
                        for item in response_json if isinstance(item, dict)
                    ):
                        logger.info(f"Skipping response from {response.url}... not the expected report structure")
                        return

                    logger.info(f"Intercepted query response from {response.url}")

                    # Remove the "data" field from the "data" object if it exists, as it includes way more data than we need
                    if isinstance(response_json, list):
                        for item in response_json:
                            if isinstance(item, dict) and "data" in item and isinstance(item["data"], dict):
                                item["data"].pop("data", None)
                            self.queries.append(item)
                    else:
                        self.queries.append(response_json)
                    self.status["queries"] = "complete"
                except Exception:
                    logger.warning(f"Failed to parse JSON from {response.url}")
                    logger.debug(f"Response headers: {response.headers}")
                    logger.debug(f"Response content: {response.text}")
                    logger.debug(f"Response status: {response.status}")
                    self.status["queries"] = "failed"

            if "explore" in extract_types:
                pass
            if "models" in extract_types:
                pass

        page = self.context.open_page_with_response_handler(url, handle_responses, reuse_context=reuse_context)
        logger.info(f"Successfully navigated to: {url}")

        def wait_for_extractions_to_load():
            # Wait for all status to be updated to "complete"
            timeout = 30_000
            start_time = page.evaluate("performance.now()")
            while not all(status == "complete" for status in self.status.values()) and (page.evaluate("performance.now()") - start_time) < timeout:
                page.wait_for_timeout(100)
            if (page.evaluate("performance.now()") - start_time) >= timeout:
                logger.warning(f"Timed out waiting for queries to load")
        logger.info(f"Waiting for extractions to load...")
        wait_for_extractions_to_load()
        if all(status == "complete" for status in self.status.values()):
            logger.info(f"All extractions loaded successfully")
        else:
            logger.warning(f"One or more extractions failed to load")
        return page
