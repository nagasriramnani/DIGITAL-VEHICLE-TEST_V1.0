"""
Duplicate and redundant test detection using HDBSCAN clustering and similarity metrics.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from collections import defaultdict

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("HDBSCAN not available. Install with: pip install hdbscan")

from src.ai.similarity import cosine_similarity, compute_similarity_matrix

logger = logging.getLogger(__name__)


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Compute Jaccard similarity between two sets.
    
    Args:
        set1: First set
        set2: Second set
        
    Returns:
        Jaccard similarity (0-1)
    """
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def text_jaccard_similarity(text1: str, text2: str) -> float:
    """
    Compute Jaccard similarity between two texts (tokenized).
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Jaccard similarity (0-1)
    """
    # Simple tokenization (split on whitespace and lowercase)
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    
    return jaccard_similarity(tokens1, tokens2)


class DuplicateDetector:
    """
    Detects duplicate and redundant test scenarios using clustering and similarity metrics.
    """
    
    def __init__(
        self,
        min_cluster_size: int = 2,
        min_samples: int = 1,
        similarity_threshold: float = 0.85
    ):
        """
        Initialize duplicate detector.
        
        Args:
            min_cluster_size: Minimum cluster size for HDBSCAN
            min_samples: Minimum samples for HDBSCAN
            similarity_threshold: Threshold for considering tests as duplicates
        """
        if not HDBSCAN_AVAILABLE:
            raise ImportError("HDBSCAN is required for duplicate detection. Install with: pip install hdbscan")
        
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.similarity_threshold = similarity_threshold
    
    def detect_duplicates_by_embedding(
        self,
        scenarios: List[Dict[str, Any]],
        embedding_key: str = 'embedding'
    ) -> Dict[str, Any]:
        """
        Detect duplicates using HDBSCAN clustering on embeddings.
        
        Args:
            scenarios: List of test scenarios with embeddings
            embedding_key: Key for embedding in scenario dict
            
        Returns:
            Dictionary with clusters and duplicate information
        """
        if not scenarios:
            return {'clusters': [], 'duplicates': []}
        
        logger.info(f"Detecting duplicates in {len(scenarios)} scenarios using HDBSCAN...")
        
        # Extract embeddings
        embeddings = []
        valid_scenarios = []
        
        for scenario in scenarios:
            if embedding_key in scenario:
                emb = scenario[embedding_key]
                if isinstance(emb, list):
                    emb = np.array(emb)
                embeddings.append(emb)
                valid_scenarios.append(scenario)
        
        if len(embeddings) < self.min_cluster_size:
            logger.warning(f"Not enough scenarios ({len(embeddings)}) for clustering (min: {self.min_cluster_size})")
            return {'clusters': [], 'duplicates': []}
        
        embeddings = np.array(embeddings)
        
        # Perform HDBSCAN clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        cluster_labels = clusterer.fit_predict(embeddings)
        
        # Organize clusters
        clusters_dict = defaultdict(list)
        noise_points = []
        
        for idx, label in enumerate(cluster_labels):
            if label == -1:
                noise_points.append(valid_scenarios[idx])
            else:
                clusters_dict[label].append(valid_scenarios[idx])
        
        # Convert to list of clusters
        clusters = [
            {
                'cluster_id': cluster_id,
                'size': len(members),
                'scenarios': members,
                'canonical': self._select_canonical(members)
            }
            for cluster_id, members in clusters_dict.items()
        ]
        
        # Sort clusters by size (descending)
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        logger.info(f"Found {len(clusters)} clusters, {len(noise_points)} noise points")
        
        # Identify potential duplicates within clusters
        duplicates = self._identify_duplicates_in_clusters(clusters)
        
        return {
            'clusters': clusters,
            'duplicates': duplicates,
            'noise_points': noise_points,
            'n_clusters': len(clusters),
            'n_noise': len(noise_points)
        }
    
    def _select_canonical(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select canonical (representative) scenario from a cluster.
        
        Criteria:
        - Most historical executions
        - Highest pass rate
        - Most comprehensive (most components tested)
        
        Args:
            scenarios: List of scenarios in cluster
            
        Returns:
            Canonical scenario
        """
        if not scenarios:
            return {}
        
        best_scenario = scenarios[0]
        best_score = -1
        
        for scenario in scenarios:
            # Score based on execution count, pass rate, and component coverage
            historical = scenario.get('historical_results', [])
            execution_count = len(historical)
            
            pass_rate = 0.5
            if historical:
                passed = sum(1 for h in historical if h.get('passed', False))
                pass_rate = passed / len(historical)
            
            component_count = len(scenario.get('target_components', []))
            
            # Combined score
            score = execution_count * 0.4 + pass_rate * 0.3 + component_count * 0.3
            
            if score > best_score:
                best_score = score
                best_scenario = scenario
        
        return best_scenario
    
    def _identify_duplicates_in_clusters(
        self,
        clusters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify high-confidence duplicates within clusters.
        
        Args:
            clusters: List of clusters with scenarios
            
        Returns:
            List of duplicate groups
        """
        duplicates = []
        
        for cluster in clusters:
            scenarios = cluster['scenarios']
            canonical = cluster['canonical']
            
            if len(scenarios) < 2:
                continue
            
            # For each non-canonical scenario, check similarity
            cluster_duplicates = []
            
            for scenario in scenarios:
                if scenario['scenario_id'] == canonical['scenario_id']:
                    continue
                
                # Compute detailed similarity
                similarity = self._compute_detailed_similarity(canonical, scenario)
                
                if similarity['overall'] >= self.similarity_threshold:
                    cluster_duplicates.append({
                        'scenario_id': scenario['scenario_id'],
                        'test_name': scenario['test_name'],
                        'similarity_to_canonical': similarity['overall'],
                        'similarity_breakdown': similarity,
                        'recommendation': 'consolidate' if similarity['overall'] > 0.95 else 'review'
                    })
            
            if cluster_duplicates:
                duplicates.append({
                    'cluster_id': cluster['cluster_id'],
                    'canonical_id': canonical['scenario_id'],
                    'canonical_name': canonical['test_name'],
                    'duplicates': cluster_duplicates,
                    'potential_savings': self._estimate_savings(canonical, cluster_duplicates)
                })
        
        return duplicates
    
    def _compute_detailed_similarity(
        self,
        scenario1: Dict[str, Any],
        scenario2: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Compute detailed similarity breakdown between two scenarios.
        
        Args:
            scenario1: First scenario
            scenario2: Second scenario
            
        Returns:
            Dictionary with similarity scores
        """
        similarities = {}
        
        # Text similarity (name and description)
        name1 = scenario1.get('test_name', '')
        name2 = scenario2.get('test_name', '')
        similarities['name'] = text_jaccard_similarity(name1, name2)
        
        # Component similarity (Jaccard)
        comp1 = set(scenario1.get('target_components', []))
        comp2 = set(scenario2.get('target_components', []))
        similarities['components'] = jaccard_similarity(comp1, comp2)
        
        # System similarity (Jaccard)
        sys1 = set(scenario1.get('target_systems', []))
        sys2 = set(scenario2.get('target_systems', []))
        similarities['systems'] = jaccard_similarity(sys1, sys2)
        
        # Test type match
        similarities['test_type'] = 1.0 if scenario1.get('test_type') == scenario2.get('test_type') else 0.0
        
        # Platform overlap
        plat1 = set(scenario1.get('applicable_platforms', []))
        plat2 = set(scenario2.get('applicable_platforms', []))
        similarities['platforms'] = jaccard_similarity(plat1, plat2)
        
        # Regulatory standards overlap
        reg1 = set(scenario1.get('regulatory_standards', []))
        reg2 = set(scenario2.get('regulatory_standards', []))
        similarities['standards'] = jaccard_similarity(reg1, reg2)
        
        # Overall similarity (weighted average)
        similarities['overall'] = (
            similarities['name'] * 0.15 +
            similarities['components'] * 0.25 +
            similarities['systems'] * 0.20 +
            similarities['test_type'] * 0.15 +
            similarities['platforms'] * 0.10 +
            similarities['standards'] * 0.15
        )
        
        return similarities
    
    def _estimate_savings(
        self,
        canonical: Dict[str, Any],
        duplicates: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Estimate time and cost savings from removing duplicates.
        
        Args:
            canonical: Canonical scenario
            duplicates: List of duplicate scenarios
            
        Returns:
            Dictionary with savings estimates
        """
        # Assume we keep canonical and remove duplicates
        # But we may need to extend canonical to cover all unique aspects
        
        # Conservative estimate: save 80% of duplicate test time/cost
        reduction_factor = 0.8
        
        total_duration = canonical.get('estimated_duration_hours', 0)
        total_cost = canonical.get('estimated_cost_gbp', 0)
        
        duplicate_duration = 0
        duplicate_cost = 0
        
        # Look up full scenarios (we only have IDs in duplicates list)
        # For now, estimate average
        avg_duration = 10.0  # hours
        avg_cost = 5000.0  # GBP
        
        duplicate_duration = len(duplicates) * avg_duration
        duplicate_cost = len(duplicates) * avg_cost
        
        return {
            'time_saved_hours': duplicate_duration * reduction_factor,
            'cost_saved_gbp': duplicate_cost * reduction_factor,
            'tests_eliminated': len(duplicates),
            'reduction_percent': (len(duplicates) / (len(duplicates) + 1)) * 100
        }
    
    def find_similar_pairs(
        self,
        scenarios: List[Dict[str, Any]],
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Find all pairs of scenarios above similarity threshold.
        
        Args:
            scenarios: List of test scenarios
            threshold: Similarity threshold
            
        Returns:
            List of similar pairs with similarity scores
        """
        similar_pairs = []
        
        for i, scenario1 in enumerate(scenarios):
            for j, scenario2 in enumerate(scenarios[i+1:], i+1):
                similarity = self._compute_detailed_similarity(scenario1, scenario2)
                
                if similarity['overall'] >= threshold:
                    similar_pairs.append({
                        'scenario1_id': scenario1['scenario_id'],
                        'scenario1_name': scenario1['test_name'],
                        'scenario2_id': scenario2['scenario_id'],
                        'scenario2_name': scenario2['test_name'],
                        'similarity': similarity['overall'],
                        'similarity_breakdown': similarity
                    })
        
        # Sort by similarity (descending)
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_pairs


def create_duplicate_detector(
    min_cluster_size: int = 2,
    similarity_threshold: float = 0.85
) -> DuplicateDetector:
    """
    Create a duplicate detector instance.
    
    Args:
        min_cluster_size: Minimum cluster size for HDBSCAN
        similarity_threshold: Threshold for duplicates
        
    Returns:
        DuplicateDetector instance
    """
    return DuplicateDetector(
        min_cluster_size=min_cluster_size,
        similarity_threshold=similarity_threshold
    )


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DUPLICATE DETECTOR TEST")
    print("=" * 70)
    
    if not HDBSCAN_AVAILABLE:
        print("\n[ERROR] HDBSCAN not available. Install with: pip install hdbscan")
    else:
        print("\n[1/2] Creating duplicate detector...")
        detector = DuplicateDetector(min_cluster_size=2, similarity_threshold=0.85)
        print("[OK] Detector created")
        
        print("\n[2/2] Testing similarity computation...")
        
        # Mock scenarios
        scenario1 = {
            'scenario_id': 'TEST-001',
            'test_name': 'Battery Thermal Test',
            'test_type': 'performance',
            'target_components': ['High_Voltage_Battery', 'Battery_Management_System'],
            'target_systems': ['Battery', 'Thermal'],
            'applicable_platforms': ['EV'],
            'regulatory_standards': ['UNECE_R100', 'ISO_6469']
        }
        
        scenario2 = {
            'scenario_id': 'TEST-002',
            'test_name': 'Battery Thermal Validation',
            'test_type': 'performance',
            'target_components': ['High_Voltage_Battery', 'Battery_Management_System', 'Coolant_System'],
            'target_systems': ['Battery', 'Thermal'],
            'applicable_platforms': ['EV'],
            'regulatory_standards': ['UNECE_R100']
        }
        
        similarity = detector._compute_detailed_similarity(scenario1, scenario2)
        
        print(f"[OK] Similarity between scenarios: {similarity['overall']:.3f}")
        print(f"     Breakdown:")
        print(f"       Name:       {similarity['name']:.3f}")
        print(f"       Components: {similarity['components']:.3f}")
        print(f"       Systems:    {similarity['systems']:.3f}")
        print(f"       Test Type:  {similarity['test_type']:.3f}")
        
        print("\n[OK] Duplicate detector test complete")

