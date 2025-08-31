from __future__ import annotations
import os
import time

from looker_metadata_extractor.nav.extractor_context import ExtractorContext
from looker_metadata_extractor.extract.extract import Extract
from looker_metadata_extractor.utils.logger import logger
from looker_metadata_extractor.nav.navigator import Navigator

class Extractor:
    def __init__(self, url: str, extracts: list[Extract], metadata_download_dir: str):
        self.context = None
        self.extracts = extracts
        self.url = url
        self.extractor_name = url.split("/")[-1] if url else "default_extractor"
        if metadata_download_dir:
            self.metadata_download_dir = metadata_download_dir
        else:
            raise ValueError("Missing required argument `metadata_download_dir`")

    def save_data(self):
        full_download_directory = os.path.join(os.path.join(self.metadata_download_dir, self.extractor_name), self.extract_timestamp)
        self._ensure_directory(full_download_directory)
        logger.info(f"[Extractor:{self.extractor_name}] Saving extracted data to {full_download_directory}...")
        for extract in self.extracts:
            extract.save_data(f"{full_download_directory}/{extract.type}.json")
        self.clear_data()

    def clear_data(self):
        logger.info(f"[Extractor:{self.extractor_name}] Clearing cached extracted data...")
        for extract in self.extracts:
            extract.clear_data()

    def extract(self, navigator: Navigator, context: ExtractorContext | None = None):
        self.clear_data()
        self.extract_timestamp = time.strftime("%Y-%m-%d_%H-%M")
        if context:
            navigator.set_context(context)
        logger.info(f"[Extractor:{self.extractor_name}] Starting extraction...")
        navigator.navigate_and_extract(self.url, self.extracts, False if context else True)

    def _ensure_directory(self, full_download_directory: str):
        if not os.path.exists(full_download_directory):
            os.makedirs(full_download_directory)