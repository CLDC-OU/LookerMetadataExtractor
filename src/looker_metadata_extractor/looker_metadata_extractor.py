from __future__ import annotations

from looker_metadata_extractor.nav.navigator import Navigator, NavigatorType
from looker_metadata_extractor.nav.handshake_navigator import HandshakeNavigator
from looker_metadata_extractor.extract.extract import QueryExtract, ExploreExtract, ModelExtract
from looker_metadata_extractor.extract.extractor import Extractor
from looker_metadata_extractor.utils.logger import logger


class LookerMetadataExtractor:
    """
    Extractor for Looker metadata
    """

    def __init__(self, **kwargs):
        self.extractors = []
        self.type = NavigatorType.from_string(kwargs.get("type", "unknown"))
        self.reuse_context = kwargs.get("reuse_context", True)

        # Load extractors
        index = 0
        for extractor_kwargs in kwargs.get("extractors", []):
            extracts = []
            for extract in extractor_kwargs.get("extracts", []):
                if extract.get("type") == "query":
                    extracts.append(QueryExtract(**extract))
                elif extract.get("type") == "explore":
                    extracts.append(ExploreExtract(**extract))
                elif extract.get("type") == "model":
                    extracts.append(ModelExtract(**extract))
                else:
                    raise ValueError(f"Unknown extract type: {extract.get('type')}")

            def _is_valid_extractor(extractor_kwargs: dict) -> bool:
                return len(extracts) > 0 and "url" in extractor_kwargs and "metadata_download_directory" in extractor_kwargs

            if _is_valid_extractor(extractor_kwargs):
                self.extractors.append(Extractor(
                    url=extractor_kwargs.get("url"),
                    extracts=extracts, 
                    metadata_download_directory=extractor_kwargs.get("metadata_download_directory"),
                    custom_timeout=extractor_kwargs.get("custom_timeout", None)
                ))
                logger.info(f"Loaded extractor {index} for URL: {extractor_kwargs.get('url')}")
            else:
                logger.warning(f"Skipping extractor {index} (missing required fields or no extracts defined)")
            index += 1

        # Initialize navigator
        if self.type == NavigatorType.HANDSHAKE:
            self.navigator = HandshakeNavigator(**kwargs)
        else:
            self.navigator = Navigator(**kwargs)

    def extract_metadata(self):
        for extractor in self.extractors:
            extractor.extract(self.navigator, context=self.navigator.context if self.navigator.context.context else None)

    def save_extracted_data(self):
        for extractor in self.extractors:
            extractor.save_data()
