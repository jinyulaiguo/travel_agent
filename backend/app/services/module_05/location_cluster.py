from typing import List, Dict, Tuple, Any
import math
import random

class LocationClusterService:
    """
    Service for clustering attractions and finding a central location for accommodation.
    """
    
    @staticmethod
    def calculate_centroid(attractions: List[Dict[str, Any]]) -> Tuple[float, float]:
        """
        Calculates the centroid (geometric center) of a list of attractions.
        """
        if not attractions:
            return (0.0, 0.0)
            
        total_lat = 0.0
        total_lng = 0.0
        points = 0
        
        for attraction in attractions:
            coords = attraction.get("coordinates") or {}
            if "lat" in coords and "lng" in coords:
                total_lat += coords["lat"]
                total_lng += coords["lng"]
                points += 1
            
        if points == 0: return (0.0, 0.0)
        return (total_lat / points, total_lng / points)

    @staticmethod
    def kmeans_cluster(attractions: List[Dict[str, Any]], k: int = 2, iterations: int = 5) -> Dict[int, List[Dict[str, Any]]]:
        """
        Simple K-means clustering for attractions (Category III requirement).
        Returns a mapping from cluster_id to list of attractions.
        """
        if not attractions or len(attractions) < k:
            return {0: attractions}
            
        # Initial centroids
        centroids = []
        for i in range(k):
            # Just pick distributed items as initial seeds
            idx = (i * len(attractions)) // k
            c = attractions[idx].get("coordinates")
            centroids.append((c["lat"], c["lng"]))
            
        clusters = {i: [] for i in range(k)}
        
        for _ in range(iterations):
            clusters = {i: [] for i in range(k)}
            # Assignment
            for attraction in attractions:
                c = attraction.get("coordinates")
                dist_sq = [(c["lat"] - x)**2 + (c["lng"] - y)**2 for x, y in centroids]
                best_cluster = dist_sq.index(min(dist_sq))
                clusters[best_cluster].append(attraction)
                attraction["cluster_id"] = best_cluster
            
            # Update centroids
            for i in range(k):
                if clusters[i]:
                    new_lat = sum(a["coordinates"]["lat"] for a in clusters[i]) / len(clusters[i])
                    new_lng = sum(a["coordinates"]["lng"] for a in clusters[i]) / len(clusters[i])
                    centroids[i] = (new_lat, new_lng)
                    
        return clusters

    @staticmethod
    def generate_area_rationale(area_name: str, attractions: List[Dict[str, Any]], avg_time: float) -> str:
        """
        Generates a rationale for the recommended accommodation area.
        """
        top_attractions = [a.get("name", "景点") for a in attractions[:2]]
        attraction_str = "、".join(top_attractions)
        
        return f"推荐入住 {area_name}，前往 {attraction_str} 等主要景点的平均交通时间约 {round(avg_time)} 分钟，地理位置极其便利。"

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points (km).
        """
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a)) 
        return c * 6371
