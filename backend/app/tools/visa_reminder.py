from typing import Optional, Dict

async def visa_reminder(origin_country_code: str, target_country_code: str) -> Optional[Dict[str, str]]:
    """
    检测是否跨国并触发签证提示。
    
    参数:
    - origin_country_code (str): 出发国代码 (如 'CN')
    - target_country_code (str): 目标国代码 (如 'TH')
    
    返回:
    - Dict: 包含官方查询链接，或 None (如果不跨境)
    """
    if origin_country_code.upper() == target_country_code.upper():
        return None
        
    # 定义一些常用国家的官方查询链接
    VISA_RESOURCES = {
        "TH": "https://www.thaievisa.go.th/",
        "JP": "https://www.mofa.go.jp/j_info/visit/visa/index.html",
        "KR": "https://www.visa.go.kr/",
        "VN": "https://evisa.xuatnhapcanh.gov.vn/",
        "SG": "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements",
    }
    
    link = VISA_RESOURCES.get(target_country_code.upper(), "https://www.iatatravelcentre.com/")
    
    return {
        "type": "visa_reminder",
        "message": "检测到跨境旅行，请务必核实目的地签证政策。",
        "official_link": link,
        "note": "以上建议仅供参考，请以官方最新公告为准。"
    }
