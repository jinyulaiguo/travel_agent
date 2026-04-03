from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, START, END
from app.schemas.state import PlanningState, NodeStatus, NodeData
from app.core.planner.intent_planner import IntentPlannerModule
from app.core.planner.flight_planner import FlightPlannerModule
from app.core.planner.destination_planner import DestinationPlannerModule
from app.core.planner.attraction_planner import AttractionPlannerModule
from app.core.planner.hotel_planner import HotelPlannerModule
from app.core.planner.itinerary_planner import ItineraryPlannerModule
from app.core.planner.transport_planner import TransportPlannerModule
from app.core.planner.dining_planner import DiningPlannerModule
from app.core.planner.cost_planner import CostPlannerModule
from app.core.planner.export_planner import ExportPlannerModule
from app.services.state_service import StateService
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.runnables import RunnableConfig
# Add other imports as modules are implemented

async def run_planner_node(state: PlanningState, node_key: str, planner_module: Any, db_factory: Optional[Any] = None) -> Dict[str, Any]:
    """通用节点运行逻辑，包含数据库持久化 (使用 db_factory 以支持并发)"""
    node = state.nodes.get(node_key)
    if not node:
        return {}

    # 如果节点已经 CONFIRMED 或 LOCKED，跳过生成
    if node.status in [NodeStatus.CONFIRMED, NodeStatus.LOCKED]:
        return {}

    # 更新状态为生成中
    node.status = NodeStatus.GENERATING
    if db_factory:
        async with db_factory() as db:
            await StateService.save_state(db, state)

    try:
        # 校验输入依赖
        if await planner_module.validate_input(state):
            data = await planner_module.generate(state)
            node.data = data
            node.status = NodeStatus.GENERATED
        else:
            # 依赖未就绪，或者上游数据不足
            node.status = NodeStatus.PENDING
    except Exception as e:
        import traceback
        node.status = NodeStatus.STALE
        node.compatibility_warning = f"生成失败: {str(e)}"
        print(f"Error in node {node_key}: {traceback.format_exc()}")

    # 如果提供了 DB factory，打开独立 session 持久化状态
    if db_factory:
        async with db_factory() as db:
            await StateService.save_state(db, state)

    return {"nodes": {node_key: node}}

# 各个节点的封装，支持从 graph config 中提取 db_factory
async def l0_intent_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = IntentPlannerModule()
    return await run_planner_node(state, "L0_intent", module, db_factory)

async def l1_flight_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = FlightPlannerModule()
    return await run_planner_node(state, "L1_flight", module, db_factory)

async def l2_destination_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = DestinationPlannerModule()
    return await run_planner_node(state, "L2_destination", module, db_factory)

async def l3_attractions_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = AttractionPlannerModule()
    return await run_planner_node(state, "L3_attractions", module, db_factory)

async def l4_hotel_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = HotelPlannerModule()
    return await run_planner_node(state, "L4_hotel", module, db_factory)

async def l5_itinerary_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = ItineraryPlannerModule()
    return await run_planner_node(state, "L5_itinerary", module, db_factory)

async def l6_transport_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = TransportPlannerModule()
    return await run_planner_node(state, "L6_transport", module, db_factory)

async def l7_dining_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = DiningPlannerModule()
    return await run_planner_node(state, "L7_dining", module, db_factory)

async def l8_cost_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = CostPlannerModule()
    return await run_planner_node(state, "L8_cost", module, db_factory)

async def l9_export_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db_factory = config.get("configurable", {}).get("db_factory") if config else None
    module = ExportPlannerModule()
    return await run_planner_node(state, "L9_export", module, db_factory)

def create_planning_graph():
    """创建规划工作流图"""
    workflow = StateGraph(PlanningState)

    # 添加节点
    workflow.add_node("L0_intent", l0_intent_node)
    workflow.add_node("L1_flight", l1_flight_node)
    workflow.add_node("L2_destination", l2_destination_node)
    workflow.add_node("L3_attractions", l3_attractions_node)
    workflow.add_node("L4_hotel", l4_hotel_node)
    workflow.add_node("L5_itinerary", l5_itinerary_node)
    workflow.add_node("L6_transport", l6_transport_node)
    workflow.add_node("L7_dining", l7_dining_node)
    workflow.add_node("L8_cost", l8_cost_node)
    workflow.add_node("L9_export", l9_export_node)

    # 构建边 (根据流程图拓扑结构)
    workflow.add_edge(START, "L0_intent")
    workflow.add_edge("L0_intent", "L1_flight")
    workflow.add_edge("L1_flight", "L2_destination")
    
    # 串行执行 L3 -> L4 -> L5
    workflow.add_edge("L2_destination", "L3_attractions")
    workflow.add_edge("L3_attractions", "L4_hotel")
    workflow.add_edge("L4_hotel", "L5_itinerary")
    
    # 串行执行 L6 -> L7 防止并发数据库脏写
    workflow.add_edge("L5_itinerary", "L6_transport")
    workflow.add_edge("L6_transport", "L7_dining")
    
    # 汇聚到 L8
    workflow.add_edge("L7_dining", "L8_cost")
    
    workflow.add_edge("L8_cost", "L9_export")
    workflow.add_edge("L9_export", END)

    return workflow.compile()
