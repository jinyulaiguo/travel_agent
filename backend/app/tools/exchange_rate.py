import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 国家代码到币种的映射
COUNTRY_TO_CURRENCY = {
    "TH": "THB",
    "VN": "VND",
    "ID": "IDR",
    "JP": "JPY",
    "US": "USD",
    "MY": "MYR",
    "KR": "KRW",
    "SG": "SGD",
    "HK": "HKD",
    "MO": "MOP",
    "TW": "TWD",
    "EU": "EUR",
    "GB": "GBP",
    "AU": "AUD",
}

# 静态参考汇率（当 API 不可用时降级使用）
# 更新日期：2024-03-20
FALLBACK_RATES = {
    "THB": 0.203,
    "VND": 0.000287,
    "IDR": 0.000458,
    "JPY": 0.0478,
    "USD": 7.21,
    "MYR": 1.52,
    "KRW": 0.0054,
    "SGD": 5.37,
    "HKD": 0.92,
    "EUR": 7.85,
    "GBP": 9.15,
}

FALLBACK_DATE = "2024-03-20"

async def get_exchange_rate(country_code: str) -> Dict[str, Any]:
    """
    根据目的地国家代码获取汇率 (外币 -> CNY)。
    
    Args:
        country_code: 目的地国家代码 (如 'TH')
        
    Returns:
        dict: 包含 currency, rate (汇率), source (来源), date (数据日期)
    """
    currency = COUNTRY_TO_CURRENCY.get(country_code.upper(), "USD")
    if currency == "CNY":
        return {
            "currency": "CNY",
            "rate": 1.0,
            "source": "fixed",
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # 获取该币种相对于 CNY 的汇率
            rate = data.get("rates", {}).get("CNY")
            if rate:
                return {
                    "currency": currency,
                    "rate": float(rate),
                    "source": "ExchangeRate-API",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
    except Exception as e:
        logger.warning(f"Failed to fetch exchange rate for {currency} from API: {e}")
    
    # 降级处理
    rate = FALLBACK_RATES.get(currency, 7.2)  # 默认按 USD 估算
    return {
        "currency": currency,
        "rate": rate,
        "source": "fallback_config",
        "date": FALLBACK_DATE,
        "is_fallback": True
    }
