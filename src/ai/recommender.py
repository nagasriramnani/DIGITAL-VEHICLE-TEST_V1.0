"""
Test scenario recommendation engine with ensemble scoring and explainability.
Combines semantic similarity, graph proximity, rules, and historical success.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
import numpy as np
from collections import defaultdict

if TYPE_CHECKING:
    from src.ai.embeddings import EmbeddingPipeline

try:
    from src.ai.similarity import cosine_similarity
except ImportError:
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Fallback cosine similarity if similarity module unavailable."""
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

logger = logging.getLogger(__name__)


class TestRecommender:
    """
    Ensemble test recommendation system.
    
    Scoring Formula:
        final_score = 0.4 * semantic_similarity
                    + 0.3 * graph_proximity
                    + 0.2 * rules_score
                    + 0.1 * historical_success
    """
    
    def __init__(self, embedding_pipeline: Optional[Any] = None):
        """
        Initialize test recommender.
        
        Args:
            embedding_pipeline: Optional pre-initialized embedding pipeline
        """
        self.embedding_pipeline = embedding_pipeline
        
        # Scoring weights
        self.weights = {
            'semantic': 0.4,
            'graph': 0.3,
            'rules': 0.2,
            'historical': 0.1
        }
        
        # Platform-specific rules
        self.platform_rules = {
            'EV': {
                'Battery': ['UNECE_R100', 'ISO_6469', 'SAE_J2929'],
                'Powertrain': ['ISO_8854', 'SAE_J1772'],
                'ADAS': ['UNECE_R157', 'ISO_26262'],
            },
            'HEV': {
                'Battery': ['UNECE_R100', 'ISO_6469'],
                'Powertrain': ['WLTP_Class3b', 'EPA_FTP75', 'EURO_6E'],
            },
            'ICE': {
                'Powertrain': ['WLTP_Class3b', 'EPA_FTP75', 'EURO_6E'],
                'Chassis': ['UNECE_R13H', 'FMVSS_135'],
            }
        }
    
    def compute_semantic_score(
        self,
        query_embedding: np.ndarray,
        candidate_embedding: np.ndarray
    ) -> float:
        """
        Compute semantic similarity score.
        
        Args:
            query_embedding: Query scenario embedding
            candidate_embedding: Candidate scenario embedding
            
        Returns:
            Similarity score (0-1)
        """
        return cosine_similarity(query_embedding, candidate_embedding)
    
    def compute_graph_proximity(
        self,
        query_components: List[str],
        candidate_components: List[str],
        query_systems: List[str],
        candidate_systems: List[str],
        graph_data: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Compute graph-based proximity score.
        
        Uses:
        - Shared components (Jaccard similarity)
        - Shared systems (Jaccard similarity)
        - Graph shortest path distance (if available)
        
        Args:
            query_components: Query scenario components
            candidate_components: Candidate scenario components
            query_systems: Query scenario systems
            candidate_systems: Candidate scenario systems
            graph_data: Optional pre-computed graph metrics
            
        Returns:
            Proximity score (0-1)
        """
        scores = []
        
        # Component overlap (Jaccard)
        if query_components and candidate_components:
            query_set = set(query_components)
            candidate_set = set(candidate_components)
            intersection = len(query_set & candidate_set)
            union = len(query_set | candidate_set)
            component_jaccard = intersection / union if union > 0 else 0
            scores.append(component_jaccard)
        
        # System overlap (Jaccard)
        if query_systems and candidate_systems:
            query_set = set(query_systems)
            candidate_set = set(candidate_systems)
            intersection = len(query_set & candidate_set)
            union = len(query_set | candidate_set)
            system_jaccard = intersection / union if union > 0 else 0
            scores.append(system_jaccard)
        
        # Graph distance (if available)
        if graph_data and 'shortest_path_length' in graph_data:
            # Normalize by max expected path length (e.g., 5)
            path_score = 1.0 - min(graph_data['shortest_path_length'] / 5.0, 1.0)
            scores.append(path_score)
        
        return np.mean(scores) if scores else 0.5
    
    def compute_rules_score(
        self,
        query_spec: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """
        Compute rules-based score with explanations.
        
        Rules:
        - Platform matching (EV/HEV/ICE)
        - System-specific regulatory requirements
        - Criticality matching
        - Test type appropriateness
        
        Args:
            query_spec: Query specification with platform, systems, etc.
            candidate: Candidate test scenario
            
        Returns:
            Tuple of (score, rules_fired)
        """
        score = 0.0
        rules_fired = []
        
        query_platform = query_spec.get('platform', '')
        query_systems = query_spec.get('systems', [])
        query_components = query_spec.get('components', [])
        
        candidate_platforms = candidate.get('applicable_platforms', [])
        candidate_systems = candidate.get('target_systems', [])
        candidate_standards = candidate.get('regulatory_standards', [])
        
        # Rule 1: Platform matching (0.3 weight)
        if query_platform in candidate_platforms:
            score += 0.3
            rules_fired.append(f"Platform match: {query_platform}")
        
        # Rule 2: Regulatory standards for platform+system (0.4 weight)
        if query_platform in self.platform_rules:
            for system in query_systems:
                if system in self.platform_rules[query_platform]:
                    expected_standards = self.platform_rules[query_platform][system]
                    matched = [s for s in expected_standards if s in candidate_standards]
                    if matched:
                        score += 0.4 * (len(matched) / len(expected_standards))
                        rules_fired.append(f"Regulatory match for {system}: {', '.join(matched)}")
        
        # Rule 3: System overlap (0.2 weight)
        if query_systems and candidate_systems:
            overlap = len(set(query_systems) & set(candidate_systems))
            if overlap > 0:
                score += 0.2 * (overlap / len(query_systems))
                rules_fired.append(f"System overlap: {overlap}/{len(query_systems)} systems")
        
        # Rule 4: Critical component testing (0.1 weight)
        # If query has critical components, prefer tests that cover them
        if query_components:
            candidate_components = candidate.get('target_components', [])
            overlap = len(set(query_components) & set(candidate_components))
            if overlap > 0:
                score += 0.1
                rules_fired.append(f"Component coverage: {overlap} components")
        
        # Normalize to 0-1
        score = min(score, 1.0)
        
        return score, rules_fired
    
    def compute_historical_score(
        self,
        candidate: Dict[str, Any]
    ) -> float:
        """
        Compute score based on historical test success.
        
        Factors:
        - Pass rate of historical executions
        - Number of executions (confidence)
        - Recency (more recent = better)
        
        Args:
            candidate: Candidate test scenario with historical results
            
        Returns:
            Historical success score (0-1)
        """
        historical = candidate.get('historical_results', [])
        
        if not historical:
            return 0.5  # Neutral score for untested scenarios
        
        # Pass rate
        passed = sum(1 for h in historical if h.get('passed', False))
        pass_rate = passed / len(historical)
        
        # Execution count confidence (cap at 10 executions)
        confidence = min(len(historical) / 10.0, 1.0)
        
        # Combine: weighted by confidence
        score = pass_rate * confidence + 0.5 * (1 - confidence)
        
        return score
    
    def recommend(
        self,
        query_spec: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
        graph_data: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend tests based on query specification.
        
        Args:
            query_spec: Query with vehicle_id/platform/systems/components/description
            candidates: List of candidate test scenarios
            top_k: Number of recommendations to return
            graph_data: Optional dict mapping scenario_id to graph metrics
            
        Returns:
            List of recommended tests with scores and explanations
        """
        logger.info(f"Generating recommendations for query with {len(candidates)} candidates...")
        
        # Create query embedding if embedding pipeline available
        query_embedding = None
        if self.embedding_pipeline and 'description' in query_spec:
            query_text = query_spec.get('description', '')
            if 'name' in query_spec:
                query_text = f"{query_spec['name']} {query_text}"
            query_embedding = self.embedding_pipeline.encode_text(query_text)
        
        # Score all candidates
        recommendations = []
        
        for candidate in candidates:
            explain = {
                'neighbors': [],
                'kg_paths': [],
                'rules_fired': [],
                'scores': {},
                'notes': []
            }
            
            # Semantic score
            semantic_score = 0.0
            if query_embedding is not None and 'embedding' in candidate:
                candidate_emb = candidate['embedding']
                if isinstance(candidate_emb, list):
                    candidate_emb = np.array(candidate_emb)
                semantic_score = self.compute_semantic_score(query_embedding, candidate_emb)
                explain['scores']['semantic'] = semantic_score
            
            # Graph proximity score
            graph_score = self.compute_graph_proximity(
                query_spec.get('components', []),
                candidate.get('target_components', []),
                query_spec.get('systems', []),
                candidate.get('target_systems', []),
                graph_data.get(candidate.get('scenario_id')) if graph_data else None
            )
            explain['scores']['graph'] = graph_score
            
            # Rules score
            rules_score, rules_fired = self.compute_rules_score(query_spec, candidate)
            explain['scores']['rules'] = rules_score
            explain['rules_fired'] = rules_fired
            
            # Historical score
            historical_score = self.compute_historical_score(candidate)
            explain['scores']['historical'] = historical_score
            
            # Final weighted score
            final_score = (
                self.weights['semantic'] * semantic_score +
                self.weights['graph'] * graph_score +
                self.weights['rules'] * rules_score +
                self.weights['historical'] * historical_score
            )
            
            # Add explanation notes
            if semantic_score > 0.8:
                explain['notes'].append("High semantic similarity")
            if graph_score > 0.7:
                explain['notes'].append("Strong graph connectivity")
            if rules_score > 0.7:
                explain['notes'].append("Matches multiple rules")
            if historical_score > 0.8:
                explain['notes'].append("High historical success rate")
            
            recommendations.append({
                'scenario_id': candidate.get('scenario_id'),
                'test_name': candidate.get('test_name'),
                'test_type': candidate.get('test_type'),
                'score': final_score,
                'explain': explain,
                'metadata': {
                    'complexity_score': candidate.get('complexity_score'),
                    'risk_level': candidate.get('risk_level'),
                    'estimated_duration_hours': candidate.get('estimated_duration_hours'),
                    'estimated_cost_gbp': candidate.get('estimated_cost_gbp'),
                }
            })
        
        # Sort by score (descending)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Generated {len(recommendations)} recommendations, returning top {top_k}")
        
        return recommendations[:top_k]
    
    def recommend_for_vehicle(
        self,
        vehicle_model: str,
        platform: str,
        systems: List[str],
        components: List[str],
        candidates: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Convenience method for vehicle-based recommendations.
        
        Args:
            vehicle_model: Vehicle model name (e.g., "Ariya")
            platform: Platform type (EV/HEV/ICE)
            systems: Target vehicle systems
            components: Target components
            candidates: List of candidate test scenarios
            top_k: Number of recommendations
            
        Returns:
            List of recommended tests
        """
        query_spec = {
            'vehicle_model': vehicle_model,
            'platform': platform,
            'systems': systems,
            'components': components,
            'name': f"{vehicle_model} Testing",
            'description': f"Test scenarios for {vehicle_model} {platform} covering {', '.join(systems)}"
        }
        
        return self.recommend(query_spec, candidates, top_k=top_k)
    
    def explain_recommendation(
        self,
        recommendation: Dict[str, Any],
        verbose: bool = True
    ) -> str:
        """
        Generate human-readable explanation for a recommendation.
        
        Args:
            recommendation: Recommendation dictionary with explain field
            verbose: Include detailed score breakdown
            
        Returns:
            Explanation string
        """
        lines = []
        
        lines.append(f"Test: {recommendation['test_name']}")
        lines.append(f"Overall Score: {recommendation['score']:.3f}")
        
        if verbose:
            explain = recommendation.get('explain', {})
            scores = explain.get('scores', {})
            
            lines.append("\nScore Breakdown:")
            lines.append(f"  Semantic Similarity: {scores.get('semantic', 0):.3f} (weight: {self.weights['semantic']})")
            lines.append(f"  Graph Proximity:     {scores.get('graph', 0):.3f} (weight: {self.weights['graph']})")
            lines.append(f"  Rules Matching:      {scores.get('rules', 0):.3f} (weight: {self.weights['rules']})")
            lines.append(f"  Historical Success:  {scores.get('historical', 0):.3f} (weight: {self.weights['historical']})")
            
            rules_fired = explain.get('rules_fired', [])
            if rules_fired:
                lines.append("\nRules Fired:")
                for rule in rules_fired:
                    lines.append(f"  • {rule}")
            
            notes = explain.get('notes', [])
            if notes:
                lines.append("\nNotes:")
                for note in notes:
                    lines.append(f"  • {note}")
        
        return '\n'.join(lines)


def create_recommender(embedding_pipeline: Optional[Any] = None) -> TestRecommender:
    """
    Create a test recommender instance.
    
    Args:
        embedding_pipeline: Optional pre-initialized embedding pipeline
        
    Returns:
        TestRecommender instance
    """
    return TestRecommender(embedding_pipeline=embedding_pipeline)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST RECOMMENDER TEST")
    print("=" * 70)
    
    # Create recommender
    print("\n[1/2] Creating recommender...")
    recommender = TestRecommender()
    print("[OK] Recommender created")
    
    # Test recommendation
    print("\n[2/2] Testing recommendation...")
    
    # Mock query spec
    query = {
        'vehicle_model': 'Ariya',
        'platform': 'EV',
        'systems': ['Battery', 'Powertrain'],
        'components': ['High_Voltage_Battery', 'Electric_Motor'],
        'description': 'Battery and powertrain testing for Ariya EV'
    }
    
    # Mock candidates
    candidates = [
        {
            'scenario_id': 'TEST-001',
            'test_name': 'Battery Thermal Test',
            'test_type': 'performance',
            'applicable_platforms': ['EV'],
            'target_systems': ['Battery', 'Thermal'],
            'target_components': ['High_Voltage_Battery', 'Battery_Management_System'],
            'regulatory_standards': ['UNECE_R100', 'ISO_6469'],
            'complexity_score': 7,
            'risk_level': 'high',
            'estimated_duration_hours': 48.0,
            'estimated_cost_gbp': 12000.0,
            'historical_results': [{'passed': True}, {'passed': True}]
        },
        {
            'scenario_id': 'TEST-002',
            'test_name': 'Motor Performance Test',
            'test_type': 'performance',
            'applicable_platforms': ['EV', 'HEV'],
            'target_systems': ['Powertrain'],
            'target_components': ['Electric_Motor', 'Inverter'],
            'regulatory_standards': ['ISO_8854'],
            'complexity_score': 5,
            'risk_level': 'medium',
            'estimated_duration_hours': 24.0,
            'estimated_cost_gbp': 6000.0,
            'historical_results': [{'passed': True}, {'passed': False}, {'passed': True}]
        }
    ]
    
    recommendations = recommender.recommend(query, candidates, top_k=2)
    
    print(f"[OK] Generated {len(recommendations)} recommendations\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"Recommendation #{i}:")
        print(recommender.explain_recommendation(rec, verbose=True))
        print()
    
    print("[OK] Test recommender test complete")

