import logging
from typing import Dict, Any
from app.services.flight import FlightService

logger = logging.getLogger(__name__)

async def flight_search(origin: str, destination: str, date: str, passengers: int = 1) -> Dict[str, Any]:
    """
    搜索候选航班列表的智能体工具接口。
    
    参数:
    - origin (str): 出发地机场/国家代码，如 BJS
    - destination (str): 目的地机场/国家代码，如 TYO
    - date (str): 出发日期，格式 YYYY-MM-DD
    - passengers (int): 乘机总人数，默认 1
    
    返回:
    包含航班候选列表、降级状态、签证提醒标志等综合信息的字典。
    """
    logger.info(f"Agent executing tool `flight_search`: O={origin}, D={destination}, date={date}, P={passengers}")
    service = FlightService()
    
    # 模拟在普通同步或异步agent框架中执行服务
    result = await service.search_flights(
        origin=origin,
        destination=destination,
        date=date,
        passengers=passengers
    )
    
    # 将 Pydantic V2 模型转为字典，作为 Agent 的标准输出
    return result.model_dump()
