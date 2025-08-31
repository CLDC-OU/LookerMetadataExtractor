from __future__ import annotations
from looker_metadata_extractor.auth.auth_handler import AuthHandler

class NoAuthHandler(AuthHandler):
    """
    No authentication handler that does nothing
    Used when no authentication is required or when authentication is handled externally
    """

    def __init__(self, **kwargs):
        pass

    def authenticate(self, context):
        pass