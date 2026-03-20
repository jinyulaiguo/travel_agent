import asyncio
import logging
from typing import Any
from datetime import datetime, timedelta

from app.adapters.base import BaseAdapter, AdapterResponse, ConfidenceLevel
from app.schemas.flight import FlightCandidate

logger = logging.getLogger(__name__)

class AmadeusFlightAdapter(BaseAdapter):
    """
    Amadeus 航班数据真实适配器接口 (当前使用 Mock 实现对接架构)
    提供 5 秒内的响应，并在调用前后打印完整日志
    """
    async def fetch(self, **kwargs) -> AdapterResponse:
        origin = kwargs.get("origin")
        destination = kwargs.get("destination")
        date = kwargs.get("date")
        passengers = kwargs.get("passengers", 1)

        # 1. 记录 API Request 日志
        logger.info(f"[AmadeusAdapter] API Request: origin={origin}, destination={destination}, "
                    f"date={date}, passengers={passengers}")

        # ======= 真实 API Request 占位 =======
        # 在此处发真实的 HTTP 请求 (httpx.AsyncClient) 给 Amadeus API
        # 这里模拟 1-2 秒的网络延迟
        await asyncio.sleep(1.0)
        
        # 为了测试超时机制，如果在 kwargs 传入 timeout 标示，则故意沉睡超过5秒
        if kwargs.get("_test_timeout"):
            await asyncio.sleep(6.0)

        # 模拟响应数据
        now = datetime.now()
        candidates = [
            FlightCandidate(
                flight_id=f"MU{origin}{destination}1",
                flight_no="MU1234",
                departure_time=now + timedelta(days=1, hours=10),
                arrival_time=now + timedelta(days=1, hours=14),
                duration_minutes=240,
                stops=0,
                price=1200.0,
                price_snapshot_time=now,
                on_time_rate_30d=0.95,
                airline="China Eastern"
            ),
            FlightCandidate(
                flight_id=f"CA{origin}{destination}1",
                flight_no="CA5678",
                departure_time=now + timedelta(days=1, hours=8),
                arrival_time=now + timedelta(days=1, hours=16),
                duration_minutes=480,
                stops=1,
                transfer_cities=["SHA"],
                price=800.0,
                price_snapshot_time=now,
                on_time_rate_30d=0.88,
                airline="Air China"
            ),
            FlightCandidate(
                flight_id=f"CZ{origin}{destination}1",
                flight_no="CZ9012",
                departure_time=now + timedelta(days=1, hours=12),
                arrival_time=now + timedelta(days=1, hours=20),
                duration_minutes=480,
                stops=2,
                transfer_cities=["SHA", "HKG"],
                price=600.0,
                price_snapshot_time=now,
                on_time_rate_30d=0.75,
                airline="China Southern"
            )
        ]

        # 2. 记录 API Response & Latency 日志
        logger.info(f"[AmadeusAdapter] API Response: fetched {len(candidates)} candidates. Latency: 1005ms")

        # ======= 组装 AdapterResponse =======
        return AdapterResponse(
            data={"candidates": candidates},
            confidence=ConfidenceLevel.L1_REALTIME,
            fetched_at=now,
            source="Amadeus"
        )

    async def fallback(self, error: Exception, **kwargs) -> AdapterResponse:
        logger.warning(f"[AmadeusAdapter] Fallback triggered! Error: {str(error)}")
        return AdapterResponse(
            data={"candidates": []},
            confidence=ConfidenceLevel.L1_REALTIME,
            fetched_at=datetime.now(),
            source="Amadeus",
            is_fallback=True,
            fallback_reason=str(error)
        )
