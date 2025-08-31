from __future__ import annotations
from playwright.sync_api import BrowserContext

class AuthHandler:
    """
    Base class for all authenticators
    """

    def __init__(self, **kwargs):
        raise NotImplementedError

    def authenticate(self, context: BrowserContext):
        raise NotImplementedError
