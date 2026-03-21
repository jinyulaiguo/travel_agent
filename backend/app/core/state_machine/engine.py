from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, START, END
from app.schemas.state import PlanningState, NodeStatus, NodeData
from app.core.planner.dining_planner import DiningPlannerModule
from app.services.state_service import StateService
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.runnables import RunnableConfig
# Add other imports as modules are implemented

async def run_planner_node(state: PlanningState, node_key: str, planner_module: Any, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
    """通用节点运行逻辑，包含数据库持久化"""
    node = state.nodes.get(node_key)
    if not node:
        return {}

    # 如果节点已经 CONFIRMED 或 LOCKED，跳过生成
    if node.status in [NodeStatus.CONFIRMED, NodeStatus.LOCKED]:
        return {}

    # 更新状态为生成中
    node.status = NodeStatus.GENERATING
    
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
        # TODO: Log error properly
        node.status = NodeStatus.STALE
        node.compatibility_warning = f"生成失败: {str(e)}"

    # 如果提供了 DB session，持久化状态
    if db:
        await StateService.save_state(db, state)

    return {"nodes": {node_key: node}}

# 各个节点的封装，支持从 graph config 中提取 db
async def l0_intent_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement IntentPlannerModule
    return {"nodes": {"L0_intent": state.nodes.get("L0_intent", NodeData())}}

async def l1_flight_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement FlightPlannerModule
    return {"nodes": {"L1_flight": state.nodes.get("L1_flight", NodeData())}}

async def l2_destination_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement DestinationPlannerModule
    return {"nodes": {"L2_destination": state.nodes.get("L2_destination", NodeData())}}

async def l3_attractions_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement AttractionPlannerModule
    return {"nodes": {"L3_attractions": state.nodes.get("L3_attractions", NodeData())}}

async def l4_hotel_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement HotelPlannerModule
    return {"nodes": {"L4_hotel": state.nodes.get("L4_hotel", NodeData())}}

async def l5_itinerary_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement ItineraryPlannerModule
    return {"nodes": {"L5_itinerary": state.nodes.get("L5_itinerary", NodeData())}}

async def l6_transport_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement TransportPlannerModule
    return {"nodes": {"L6_transport": state.nodes.get("L6_transport", NodeData())}}

async def l7_dining_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    db = None
    if config:
        db = config.get("configurable", {}).get("db")
    module = DiningPlannerModule()
    return await run_planner_node(state, "L7_dining", module, db)

async def l8_cost_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement CostPlannerModule
    return {"nodes": {"L8_cost": state.nodes.get("L8_cost", NodeData())}}

async def l9_export_node(state: PlanningState, config: RunnableConfig = None) -> Dict[str, Any]:
    # TODO: Implement ExportPlannerModule
    return {"nodes": {"L9_export": state.nodes.get("L9_export", NodeData())}}

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
    
    # 分叉到 L3 和 L4
    workflow.add_edge("L2_destination", "L3_attractions")
    workflow.add_edge("L2_destination", "L4_hotel")
    
    # 汇聚到 L5 (L5 等待 L3 和 L4)
    workflow.add_edge("L3_attractions", "L5_itinerary")
    workflow.add_edge("L4_hotel", "L5_itinerary")
    
    # L5 完成后并行执行 L6 和 L7
    workflow.add_edge("L5_itinerary", "L6_transport")
    workflow.add_edge("L5_itinerary", "L7_dining")
    
    # 汇聚到 L8
    workflow.add_edge("L6_transport", "L8_cost")
    workflow.add_edge("L7_dining", "L8_cost")
    
    workflow.add_edge("L8_cost", "L9_export")
    workflow.add_edge("L9_export", END)

    return workflow.compile()
