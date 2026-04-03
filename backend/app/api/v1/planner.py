from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.api import deps
from app.services.state_service import StateService
from app.core.state_machine.engine import create_planning_graph
from app.db.session import SessionLocal

router = APIRouter(tags=["planner"])

@router.get("/session/{session_id}/run")
async def run_planning(
    session_id: str, 
    user_id: str = "default_user"
):
    async def event_generator():
        async with SessionLocal() as db:
            # 获取当前状态
            state = await StateService.get_state(db, session_id, user_id)
            graph = create_planning_graph()
            
            # 配置 Graph 运行指令，传入 db factory 而非单一 session
            config = {"configurable": {"session_id": session_id, "db_factory": SessionLocal}}
            
            # 使用 astream_events 监听节点执行情况, 传入 state.model_dump() 以兼容内部合并逻辑
            async for event in graph.astream_events(state.model_dump(), config, version="v2"):
                kind = event["event"]
                if kind == "on_chain_start":
                    # 图开始运行
                    pass
                elif kind == "on_node_start":
                    node_name = event["name"]
                    yield f"data: {json.dumps({'type': 'node_status_change', 'node': node_name, 'status': 'generating'}, ensure_ascii=False)}\n\n"
                elif kind == "on_node_end":
                    node_name = event["name"]
                    # 节点完成，尝试提取实际输出状态
                    output = event.get("data", {}).get("output", {})
                    # LangGraph 节点返回格式为 {"nodes": {node_name: node_data}}
                    node_data_obj = None
                    if isinstance(output, dict) and "nodes" in output and node_name in output["nodes"]:
                        node_data_obj = output["nodes"][node_name]
                        final_status = node_data_obj.status if hasattr(node_data_obj, "status") else "generated"
                        yield f"data: {json.dumps({'type': 'node_status_change', 'node': node_name, 'status': final_status}, ensure_ascii=False)}\n\n"
                        
                        # 同步推送节点数据
                        if hasattr(node_data_obj, "data") and node_data_obj.data:
                            yield f"data: {json.dumps({'type': 'node_data_ready', 'node': node_name, 'data': node_data_obj.data}, ensure_ascii=False)}\n\n"
                    else:
                        # 降级处理
                        yield f"data: {json.dumps({'type': 'node_status_change', 'node': node_name, 'status': 'generated'}, ensure_ascii=False)}\n\n"

            # 最终状态已在 run_planner_node 中通过 StateService.save_state 持久化
            yield "data: {\"type\": \"planning_complete\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
