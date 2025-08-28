from __future__ import annotations
from .extractor import ExtractorConfig
from .logger import logger
from .nav.navigator import Navigator

class LookerMetadataExtractor:
    """
    Extractor for Looker metadata
    """

    
    def __init__(self, navigator: Navigator):
        self.navigator = navigator

    def extract_explore_metadata(self, explore: str):
        self.navigator.navigate(f"/explore/{explore}")
        pass

    def extract_query_metadata(self, query: str):
        self.navigator.navigate(f"/queries/{query}")
        pass

    def extract_models_metadata(self):
        self.navigator.navigate(f"/models")
        pass