from __future__ import annotations
from playwright.sync_api import BrowserContext, Page
from enum import Enum

class AuthHandlerType(Enum):
    GENERAL = "general"
    HANDSHAKE = "handshake"
    NONE = "none"
    
    @staticmethod
    def from_string(type_str: str) -> AuthHandlerType:
        try:
            return AuthHandlerType[type_str.upper()]
        except KeyError:
            return AuthHandlerType.GENERAL

class AuthHandler:
    """
    Base class for all authenticators
    """

    def __init__(self, **kwargs):
        raise NotImplementedError

    def authenticate(self, context: BrowserContext) -> Page:
        raise NotImplementedError
