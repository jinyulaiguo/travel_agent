from typing import Dict, Any, Union, List

def annotate_confidence(
    data: Union[Dict[str, Any], List[Dict[str, Any]]], 
    level: str = "L1", 
    description: str = ""
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    横向支撑工具，为数据字段附加置信度标签 (L1~L5)。
    
    层级说明:
    - L1: 实时确切数据 (Real-time)
    - L2: 官方快照数据 (Snapshot)
    - L3: 统计/外部数据 (Statistical)
    - L4: 知识库数据 (Knowledge Base)
    - L5: 经验估算数据 (Estimate)
    """
    valid_levels = {"L1", "L2", "L3", "L4", "L5"}
    target_level = level.upper() if level.upper() in valid_levels else "L5"
    
    annotation = {
        "confidence_level": target_level,
        "confidence_description": description or f"Data sourced with confidence level {target_level}"
    }
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item.update(annotation)
        return data
    elif isinstance(data, dict):
        data.update(annotation)
        return data
        
    return data
