import os
from looker_metadata_extractor.extractor_context import ExtractorContext

class Authenticator:
    """
    Base class for all authenticators
    """

    def __init__(self):
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME'):
            raise ValueError("Missing required environment variables")
        if not os.getenv('LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD'):
            raise ValueError("Missing required environment variables")

    def authenticate(self, context: ExtractorContext):
        raise NotImplementedError
