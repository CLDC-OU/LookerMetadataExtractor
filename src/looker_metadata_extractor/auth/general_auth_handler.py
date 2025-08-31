from looker_metadata_extractor.auth.auth_handler import AuthHandler
from looker_metadata_extractor.utils.logger import logger
from playwright.sync_api import BrowserContext


class GeneralAuthHandler(AuthHandler):
    """
    General authentication handler that simply waits for manual authentication
    """

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
        logger.info(f"Waiting for authentication... ({self.auth_url})")

        page = context.new_page()
        page.goto(f"{self.auth_url}")
        logger.info(f"Please authenticate in the opened browser window...")
        page.wait_for_url(self._successful_login_url, timeout=120_000)  # Wait up to 2 minutes for manual login
        logger.info(f"Successfully authenticated")
        page.close()