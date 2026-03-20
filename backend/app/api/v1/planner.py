from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
from sqlalchemy.orm import Session
from app.api import deps
from app.services.state_service import StateService
from app.core.state_machine.engine import create_planning_graph
from app.db.session import SessionLocal

router = APIRouter(prefix="/api/v1/planner", tags=["planner"])

@router.post("/session/{session_id}/run")
async def run_planning(
    session_id: str, 
    user_id: str = "default_user",
    db: Session = Depends(deps.get_db)
):
    async def event_generator():
        # 获取当前状态
        state = StateService.get_state(db, session_id, user_id)
        graph = create_planning_graph()
        
        # 配置 Graph 运行指令，传入 db session
        config = {"configurable": {"session_id": session_id, "db": db}}
        
        # 使用 astream_events 监听节点执行情况
        async for event in graph.astream_events(state, config, version="v2"):
            kind = event["event"]
            if kind == "on_chain_start":
                # 图开始运行
                pass
            elif kind == "on_node_start":
                node_name = event["name"]
                yield f"data: {json.dumps({'type': 'node_status_change', 'node': node_name, 'status': 'generating'}, ensure_ascii=False)}\n\n"
            elif kind == "on_node_end":
                node_name = event["name"]
                # 节点完成
                yield f"data: {json.dumps({'type': 'node_status_change', 'node': node_name, 'status': 'generated'}, ensure_ascii=False)}\n\n"
                
                # 如果有数据更新，也可以在这里推送 node_data_ready
                # 某些场景下 node 输出在 event['data']['output']
                output = event.get("data", {}).get("output")
                if output and hasattr(output, "nodes") and node_name in output.nodes:
                    node_data = output.nodes[node_name]
                    if node_data.data:
                        yield f"data: {json.dumps({'type': 'node_data_ready', 'node': node_name, 'data': node_data.data}, ensure_ascii=False)}\n\n"

        # 最终状态已在 run_planner_node 中通过 StateService.save_state 持久化
        yield "data: {\"type\": \"planning_complete\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
