from __future__ import annotations

from looker_metadata_extractor.nav.navigator import Navigator, NavigatorType
from looker_metadata_extractor.nav.handshake_navigator import HandshakeNavigator
from looker_metadata_extractor.extract.extract import QueryExtract, ExploreExtract, ModelExtract
from looker_metadata_extractor.extract.extractor import Extractor


class LookerMetadataExtractor:
    """
    Extractor for Looker metadata
    """

    def __init__(self, **kwargs):
        self.extractors = []
        self.type = NavigatorType.from_string(kwargs.get("type", "unknown"))
        self.reuse_context = kwargs.get("reuse_context", True)

        # Factory
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

            # TODO: Add checking for empty extracts and other edge validation

            self.extractors.append(Extractor(
                url=extractor_kwargs.get("url", None), 
                extracts=extracts, 
                metadata_download_directory=extractor_kwargs.get("metadata_download_directory", None)
            ))

        # Context
        if self.type == NavigatorType.HANDSHAKE:
            self.navigator = HandshakeNavigator(**kwargs)
        else:
            self.navigator = Navigator(**kwargs)

    def extract_metadata(self):
        for extractor in self.extractors:
            extractor.extract(self.navigator, None if self.reuse_context else self.navigator.context) # NOTE: consider resetting context if not reuse_context. This does nothing right now

    def save_extracted_data(self):
        for extractor in self.extractors:
            extractor.save_data()
