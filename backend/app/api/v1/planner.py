from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/api/v1/planner", tags=["planner"])

@router.post("/session/{session_id}/run")
async def run_planning(session_id: str):
    async def event_generator():
        # Placeholder for real planning service
        events = [
            {"type": "node_status_change", "node": "L0_intent", "old_status": "pending", "new_status": "generating"},
            {"type": "node_data_ready", "node": "L0_intent", "data": {"intent": "travel to Tokyo"}, "confidence_map": {}},
            {"type": "node_status_change", "node": "L0_intent", "old_status": "generating", "new_status": "generated"}
        ]
        for event in events:
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
