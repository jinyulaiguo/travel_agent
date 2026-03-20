from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

# 极简节假日 Mock 数据库
HOLIDAYS = {
    "2024-05-01": "劳动节",
    "2024-05-02": "劳动节假期",
    "2024-05-03": "劳动节假期",
    "2024-05-04": "青年节",
    "2024-05-05": "假期补休",
    "2024-10-01": "国庆节",
    "2024-10-02": "国庆节",
    "2024-10-03": "国庆节",
}

async def parse_time_intent(
    query: str, 
    turn_count: int = 0, 
    reference_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    解析模糊时间表达为精确日期区间。
    
    参数:
    - query: 用户的输入 (如 "五一", "下周末", "大概四五天")
    - turn_count: 当前追问轮次 (上限2次)
    - reference_date: 基准日期，默认为今天
    """
    ref_dt = datetime.fromisoformat(reference_date) if reference_date else datetime.now()
    
    # 模拟简单的规则匹配解析
    result = {
        "start_date": None,
        "end_date": None,
        "days": None,
        "requires_clarification": False,
        "message": ""
    }
    
    if "五一" in query:
        result["start_date"] = "2024-05-01"
        result["end_date"] = "2024-05-05"
        result["days"] = 5
        result["holiday_tag"] = "劳动节黄金周"
    elif "周末" in query:
        # 简单计算下一个周六
        days_ahead = 5 - ref_dt.weekday() # Saturday is 5
        if days_ahead <= 0: days_ahead += 7
        start = ref_dt + timedelta(days=days_ahead)
        result["start_date"] = start.strftime("%Y-%m-%d")
        result["end_date"] = (start + timedelta(days=1)).strftime("%Y-%m-%d")
        result["days"] = 2
    elif "天" in query:
        # 提取数字
        import re
        nums = re.findall(r'\d+', query)
        if nums:
            result["days"] = int(nums[0])
            result["start_date"] = ref_dt.strftime("%Y-%m-%d")
            result["end_date"] = (ref_dt + timedelta(days=result["days"]-1)).strftime("%Y-%m-%d")
        else:
            result["requires_clarification"] = True
            result["message"] = "具体是几天呢？"
            
    # 追问轮次处理
    if result["requires_clarification"] and turn_count >= 2:
        result["requires_clarification"] = False
        result["start_date"] = ref_dt.strftime("%Y-%m-%d")
        result["end_date"] = (ref_dt + timedelta(days=4)).strftime("%Y-%m-%d")
        result["days"] = 5
        result["message"] = "由于未能确认具体时间，为您默认安排 5 天行程。"

    # 冲突检测
    if result["start_date"] and result["end_date"]:
        start = datetime.strptime(result["start_date"], "%Y-%m-%d")
        end = datetime.strptime(result["end_date"], "%Y-%m-%d")
        if start > end:
            return {"error": "日期冲突", "message": "返回日期早于出发日期，请重新确认。"}

    return result
