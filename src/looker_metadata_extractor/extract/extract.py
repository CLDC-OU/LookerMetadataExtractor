from __future__ import annotations
import json
from enum import Enum

from looker_metadata_extractor.utils.logger import logger

class ExtractType(Enum):
    EXPLORE = "explore"
    QUERY = "query"
    MODEL = "model"

class Extract:
    def __init__(self, type: ExtractType, endpoint: str):
        self.type = type
        self._data = None
        self._status = "idle"
        self._endpoint = endpoint

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
    
    @property
    def data(self):
        return self._data

    def add_data_item(self, data_item):
        if self._data is None:
            self._data = []
        self._data.append(data_item)
    
    def clear_data(self):
        self._data = None
        self._status = "idle"

    def save_data(self, file_path: str):
        if not isinstance(self._data, list):
            logger.warning(f"Data for {self.type} is not a list")
            return
        if self._data is None or len(self._data) == 0:
            logger.warning(f"No data to save for {self.type}")
            return
        with open(file_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def meets_conditions(self, response) -> bool:
        return (
            self.status == "waiting"
            and self.endpoint in response.url
        )

    @staticmethod
    def json_meets_conditions(response_json: dict | list) -> bool:
        raise NotImplementedError("Subclasses must implement json_meets_conditions method")

    @staticmethod
    def extract_data(response_json: dict | list) -> list[dict]:
        raise NotImplementedError("Subclasses must implement extract_data method")

class QueryExtract(Extract):
    def __init__(self, **kwargs):
        super().__init__(ExtractType.QUERY, "queries")
        self.query = kwargs.get("query_url", None)

    def meets_conditions(self, response) -> bool:
        return super().meets_conditions(response) and response.request.method == "POST"

    @staticmethod
    def json_meets_conditions(response_json: dict | list) -> bool:
        return (
            isinstance(response_json, list)
            and all(isinstance(item, dict) and "id" in item.keys() for item in response_json)
        )

    @staticmethod
    def extract_data(response_json: dict | list) -> list[dict]:
        data_items = []

        # Remove the "data" field from the "data" object if it exists, as it includes way more data than we need
        if isinstance(response_json, list):
            for item in response_json:
                if isinstance(item, dict) and "data" in item and isinstance(item["data"], dict):
                    item["data"].pop("data", None)
                data_items.append(item)
        else:
            data_items.append(response_json)
        return data_items

class ExploreExtract(Extract):
    def __init__(self, **kwargs):
        if kwargs.get("explore_name", None) is None:
            raise ValueError("explore_name is required")
        endpoint = f"/explores/{kwargs.get('prefix', '')}{kwargs.get('explore_name')}"
        logger.info(f"ExploreExtract endpoint set to: {endpoint}")

        super().__init__(ExtractType.EXPLORE, endpoint)
        self.explore = kwargs.get("explore_name", None)

    def meets_conditions(self, response) -> bool:
        return super().meets_conditions(response) and response.request.method == "GET"

    @staticmethod
    def json_meets_conditions(response_json: dict | list) -> bool:
        return True

    @staticmethod
    def extract_data(response_json: dict | list) -> list[dict]:
        if isinstance(response_json, dict):
            return [response_json]
        elif isinstance(response_json, list):
            return response_json
        return []

class ModelExtract(Extract):
    def __init__(self, **kwargs):
        super().__init__(ExtractType.MODEL, "/models")

    def meets_conditions(self, response) -> bool:
        return super().meets_conditions(response) and response.request.method == "GET"

    @staticmethod
    def json_meets_conditions(response_json: dict | list) -> bool:
        return True

    @staticmethod
    def extract_data(response_json: dict | list) -> list[dict]:
        if isinstance(response_json, dict):
            return [response_json]
        elif isinstance(response_json, list):
            return response_json
        return []
