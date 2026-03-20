import asyncio
import logging
from typing import List

from app.schemas.flight import FlightCandidate, FlightList
from app.adapters.flight import AmadeusFlightAdapter

logger = logging.getLogger(__name__)

class FlightService:
    def __init__(self):
        self.adapter = AmadeusFlightAdapter()
        # 接口优先级：Amadeus API（主） -> 携程开放平台（备） -> Skyscanner API（备）
    
    async def search_flights(self, origin: str, destination: str, date: str, passengers: int) -> FlightList:
        logger.info(f"[FlightService] Initiating search_flights for {origin} -> {destination}")
        
        # 实现重试与 5秒 超时控制
        max_retries = 1
        timeout = 5.0
        
        adapter_response = None
        for attempt in range(max_retries + 1):
            try:
                # 假设传递给适配器的参数
                fetch_task = self.adapter.fetch(
                    origin=origin, 
                    destination=destination, 
                    date=date, 
                    passengers=passengers
                )
                adapter_response = await asyncio.wait_for(fetch_task, timeout=timeout)
                if adapter_response and not adapter_response.is_fallback:
                    break
            except asyncio.TimeoutError:
                logger.warning(f"[FlightService] Attempt {attempt+1} timed out after {timeout} seconds.")
                if attempt == max_retries:
                    # 超过最大重试，触发降级保护
                    logger.error("[FlightService] Max retries reached. Triggering API Fallback.")
                    adapter_response = await self.adapter.fallback(Exception("Timeout 5s reached"))
            except Exception as e:
                logger.error(f"[FlightService] Attempt {attempt+1} failed with error: {str(e)}")
                if attempt == max_retries:
                    adapter_response = await self.adapter.fallback(e)
                    
        # 处理结果并评分
        candidates = adapter_response.data.get("candidates", []) if adapter_response else []
        if candidates:
            candidates = self._calculate_scores(candidates)
            
        # Visa Reminder 判断 (根据国家代码/简单模拟)
        visa_reminder_shown = self._check_visa_requirements(origin, destination)
        
        return FlightList(
            candidates=candidates,
            visa_reminder_shown=visa_reminder_shown,
            is_fallback=adapter_response.is_fallback if adapter_response else True,
            fallback_message=adapter_response.fallback_reason if adapter_response else "Service Unavailable"
        )
        
    def _calculate_scores(self, candidates: List[FlightCandidate]) -> List[FlightCandidate]:
        if not candidates:
            return []
            
        min_price = min(c.price for c in candidates)
        min_duration = min(c.duration_minutes for c in candidates)
        
        for c in candidates:
            # 价格得分 (40%): 最低价=100分，每高出10%扣10分
            price_ratio = (c.price - min_price) / min_price if min_price > 0 else 0
            price_score = max(0, 100 - (price_ratio / 0.1) * 10)
            
            # 飞行时长得分 (25%): 最短时长=100分，按比例递减
            duration_score = (min_duration / c.duration_minutes * 100) if c.duration_minutes > 0 else 0
            
            # 转机次数得分 (20%): 直飞=100，一次中转=70，两次及以上=40
            if c.stops == 0:
                stop_score = 100
            elif c.stops == 1:
                stop_score = 70
            else:
                stop_score = 40
                
            # 历史准点率得分 (15%)
            otp_score = (c.on_time_rate_30d * 100) if c.on_time_rate_30d else 0
            
            # 综合相加
            total = (price_score * 0.40) + (duration_score * 0.25) + (stop_score * 0.20) + (otp_score * 0.15)
            c.total_score = round(total, 2)
            
        # 排序并标记主推理由
        candidates.sort(key=lambda x: x.total_score, reverse=True)
        if candidates:
            candidates[0].recommend_reason = "综合评分最高"
            
        return candidates
        
    def _check_visa_requirements(self, origin: str, destination: str) -> bool:
        """
        Task 2-4: 跨境检测逻辑
        这里使用简化的逻辑，如果前两个字符不同(比如 CN !== TH)，判定为跨境
        """
        if len(origin) >= 2 and len(destination) >= 2:
            return origin[:2].upper() != destination[:2].upper()
        return origin != destination
