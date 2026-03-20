from typing import List, Dict, Any
from app.services.module_05.location_cluster import LocationClusterService

async def cluster_attractions(
    attractions: List[Dict[str, Any]], 
    k: int = 2
) -> Dict[str, Any]:
    """
    对景点坐标集合做地理聚类 (K-means)。
    
    参数:
    - attractions: 景点列表，每个景点需含 coordinates {lat, lng}
    - k: 聚类数量
    
    返回:
    - Dict: { cluster_id: [attractions], centroids: { cluster_id: {lat, lng} } }
    """
    service = LocationClusterService()
    clusters = service.kmeans_cluster(attractions, k=k)
    
    centroids = {}
    for cid, items in clusters.items():
        centroids[cid] = service.calculate_centroid(items)
        
    return {
        "clusters": clusters,
        "centroids": {cid: {"lat": c[0], "lng": c[1]} for cid, c in centroids.items()},
        "k": k,
        "total_attractions": len(attractions)
    }
