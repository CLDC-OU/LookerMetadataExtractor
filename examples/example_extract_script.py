from looker_metadata_extractor.looker_metadata_extractor import LookerMetadataExtractor

kwargs = {
    "type": "handshake",
    "context": {
        "headless": False,
        "reuse_context": True,
        "user_data_directory": "./user_data",
        "cookie_url": "https://school.joinhandshake.com",
        "required_cookies": ["session_id"],
    },
    "auth": {
        "handler": "general",
        "auth_url": "https://school.joinhandshake.com/login",
        "successful_login_url": "**/edu",
    },
    "extract_timeout": 30_000,
    "extractors": [
        {
            "metadata_download_directory": "./metadata",
            "url": "https://school.joinhandshake.com/edu/analytics/reports/12345",
            "custom_timeout": 60_000,
            "extracts": [
                {"type": "query"},
                {"type": "explore", "prefix": "generated_handshake_production::", "explore_name": "students"},
                {"type": "model"}
            ]
        }
    ]
}
extractor = LookerMetadataExtractor(**kwargs)
extractor.extract_metadata()
extractor.save_extracted_data()