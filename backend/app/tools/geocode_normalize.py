from typing import Dict, Any, Optional
import random

async def geocode_normalize(query: str) -> Dict[str, Any]:
    """
    将用户输入的模糊地名标准化为结构化对象。
    
    参数:
    - query (str): 模糊地名，如 "清迈", "Chiang Mai", "曼谷考山路"
    
    返回:
    - Dict: { city, country, country_code, lat, lng }
    """
    # Mock 数据字典
    MOCK_DATABASE = {
        "清迈": {"city": "Chiang Mai", "country": "Thailand", "country_code": "TH", "lat": 18.7883, "lng": 98.9853},
        "曼谷": {"city": "Bangkok", "country": "Thailand", "country_code": "TH", "lat": 13.7563, "lng": 100.5018},
        "普吉岛": {"city": "Phuket", "country": "Thailand", "country_code": "TH", "lat": 7.8804, "lng": 98.3922},
        "东京": {"city": "Tokyo", "country": "Japan", "country_code": "JP", "lat": 35.6762, "lng": 139.6503},
        "大阪": {"city": "Osaka", "country": "Japan", "country_code": "JP", "lat": 34.6937, "lng": 135.5023},
        "京都": {"city": "Kyoto", "country": "Japan", "country_code": "JP", "lat": 35.0116, "lng": 135.7681},
    }
    
    # 模糊匹配逻辑 (简单 Mock)
    for key, data in MOCK_DATABASE.items():
        if key in query or query.lower() in key.lower() or query.lower() in data["city"].lower():
            return {**data, "status": "verified", "confidence": "L4_KNOWLEDGE"}
    
    # 兜底返回 (模拟 API 没找到精确匹配但给出一个最可能的)
    return {
        "city": query,
        "country": "Unknown",
        "country_code": "XX",
        "lat": 0.0,
        "lng": 0.0,
        "status": "unverified",
        "confidence": "L5_ESTIMATE",
        "message": "未能精确匹配地名，请手动核对坐标。"
    }
