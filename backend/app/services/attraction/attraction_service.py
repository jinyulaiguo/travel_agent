import random
import math
from typing import List, Dict, Optional, Tuple
from app.schemas.attraction import (
    AttractionRecord, AttractionRecommendationRequest, 
    ConfirmedAttraction, AttractionList, Coordinates
)
from app.services.attraction.knowledge_base_service import KnowledgeBaseService

class AttractionService:
    def __init__(self, kb_service: KnowledgeBaseService):
        self.kb_service = kb_service

    def recommend_attractions(self, request: AttractionRecommendationRequest) -> AttractionList:
        """
        Generate recommended attractions based on cities, available days, and travel style.
        """
        all_candidates: List[AttractionRecord] = []
        for city in request.cities:
            all_candidates.extend(self.kb_service.get_attractions_by_city(city))

        # 1. Implementation of matching logic: filter by tags
        # matched = candidates that have any of the travel_style tags
        preferred_tags = set(request.travel_style)
        
        # Calculate matching score
        scored_candidates = []
        for a in all_candidates:
            matching_tags = set(a.attraction_tags).intersection(preferred_tags)
            score = len(matching_tags)
            scored_candidates.append((a, score))
            
        # Filter: if results < minimum, include all and sort by score
        min_recommendations = max(3, request.available_days * 2)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Take up to max_limit
        max_limit = min(15, math.ceil(request.available_days * 2.5))
        final_records = [x[0] for x in scored_candidates[:max_limit]]
        
        # 2. Geographical Clustering (Simple K-Means simulation)
        num_clusters = max(1, request.available_days)
        clusters = self._cluster_attractions(final_records, num_clusters)
        
        # 3. Build Result
        confirmed: List[ConfirmedAttraction] = []
        total_hours = 0
        for i, cluster in enumerate(clusters):
            for a in cluster:
                confirmed.append(ConfirmedAttraction(
                    attraction_id=a.id,
                    name=a.name["zh"],
                    cluster_id=i + 1,
                    suggested_duration_hours=a.suggested_duration_hours,
                    coordinates=a.coordinates,
                    attraction_tags=a.attraction_tags,
                    opening_hours=a.opening_hours,
                    confidence_level=a.confidence_level,
                    last_updated=a.last_updated,
                    is_custom=False
                ))
                total_hours += a.suggested_duration_hours
                
        return AttractionList(
            confirmed_attractions=confirmed,
            total_estimated_hours=round(total_hours, 1)
        )

    def _cluster_attractions(self, attractions: List[AttractionRecord], k: int) -> List[List[AttractionRecord]]:
        """
        Simple K-Means clustering based on coordinates.
        """
        if not attractions:
            return []
        if len(attractions) <= k:
            return [[a] for a in attractions]

        # Initialize centroids randomly
        centroids: List[Coordinates] = [random.choice(attractions).coordinates for _ in range(k)]
        
        # Max 10 iterations for simplicity
        assignments = [0] * len(attractions)
        for _ in range(10):
            # Assignment step
            for i, a in enumerate(attractions):
                distances = []
                for c in centroids:
                    d = math.sqrt((a.coordinates.lat - c.lat)**2 + (a.coordinates.lng - c.lng)**2)
                    distances.append(d)
                assignments[i] = distances.index(min(distances))
            
            # Update step
            new_centroids = []
            for j in range(k):
                cluster_points = [attractions[m].coordinates for m, assign in enumerate(assignments) if assign == j]
                if not cluster_points:
                    new_centroids.append(centroids[j])
                    continue
                mean_lat = sum(p.lat for p in cluster_points) / len(cluster_points)
                mean_lng = sum(p.lng for p in cluster_points) / len(cluster_points)
                new_centroids.append(Coordinates(lat=mean_lat, lng=mean_lng))
            
            if new_centroids == centroids:
                break
            centroids = new_centroids
            
        # Group by assignments
        result = [[] for _ in range(k)]
        for i, assign in enumerate(assignments):
            result[assign].append(attractions[i])
        return [r for r in result if r]  # Filter empty clusters

    def generate_reason(self, attraction: AttractionRecord, user_styles: List[str]) -> str:
        """
        Generate a short reason (<= 15 chars).
        """
        matched = set(attraction.attraction_tags).intersection(set(user_styles))
        if matched:
            tag = list(matched)[0]
            return f"符合您的{tag}偏好"
        return "必游地标景点推荐"
