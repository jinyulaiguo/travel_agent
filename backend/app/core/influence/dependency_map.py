from app.schemas.state import PlanningState, NodeStatus

INFLUENCE_MAP: dict[str, list[str]] = {
    "L0_intent": ["L1_flight", "L2_destination", "L3_attractions",
                  "L4_hotel", "L5_itinerary", "L6_transport", "L7_dining", "L8_cost"],
    "L1_flight": ["L5_itinerary", "L4_hotel", "L8_cost"],
    "L2_destination": ["L3_attractions", "L4_hotel", "L5_itinerary",
                       "L6_transport", "L7_dining", "L8_cost"],
    "L3_attractions": ["L5_itinerary", "L6_transport", "L7_dining", "L8_cost"],
    "L4_hotel": ["L5_itinerary", "L6_transport", "L8_cost"],
    "L5_itinerary": ["L6_transport", "L7_dining", "L8_cost"],
    "L6_transport": ["L8_cost"],
    "L7_dining": ["L8_cost"],
}

def get_affected_nodes(changed_node: str, state: PlanningState) -> list[str]:
    """返回受影响且非 LOCKED 状态的下游节点列表"""
    affected = INFLUENCE_MAP.get(changed_node, [])
    return [
        n for n in affected
        if state.nodes[n].status != NodeStatus.LOCKED
    ]
