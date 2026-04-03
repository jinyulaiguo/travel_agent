import json
from pathlib import Path
from typing import List, Optional
from app.schemas.attraction import AttractionRecord

class KnowledgeBaseService:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            # Default path relative to the project root
            data_path = str(Path(__file__).parent.parent.parent / "data" / "mock_attractions.json")
        self.data_path = data_path
        self._data: List[AttractionRecord] = self._load_data()

    def _load_data(self) -> List[AttractionRecord]:
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return [AttractionRecord(**item) for item in raw_data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_attractions_by_city(self, city: str) -> List[AttractionRecord]:
        if not city:
            return []
        
        # Normalize: '北京市' -> '北京', '清迈' -> '清迈'
        normalized_city = city.replace("市", "").replace("县", "").strip()
        
        return [a for a in self._data if a.city.replace("市", "").replace("县", "").strip() == normalized_city]

    def search_attractions(self, query: str, city: Optional[str] = None) -> List[AttractionRecord]:
        results = []
        q = query.lower()
        for a in self._data:
            if city and a.city != city:
                continue
            if q in a.name["zh"].lower() or q in a.name["en"].lower():
                results.append(a)
        return results

    def get_all_attractions(self) -> List[AttractionRecord]:
        return self._data
