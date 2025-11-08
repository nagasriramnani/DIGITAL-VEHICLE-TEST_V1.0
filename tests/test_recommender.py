"""
Tests for Phase 5: Recommender + Deduplication + Explainability.
"""
import pytest
import numpy as np
from typing import Dict, Any, List

from src.ai.recommender import TestRecommender, create_recommender
from src.ai.duplicate_detector import (
    DuplicateDetector,
    jaccard_similarity,
    text_jaccard_similarity,
    HDBSCAN_AVAILABLE
)


class TestRecommender:
    """Test recommendation engine."""
    
    @pytest.fixture
    def recommender(self):
        """Create recommender instance."""
        return create_recommender()
    
    @pytest.fixture
    def sample_candidates(self):
        """Create sample test scenarios."""
        return [
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
            },
            {
                'scenario_id': 'TEST-003',
                'test_name': 'Brake System Test',
                'test_type': 'safety',
                'applicable_platforms': ['ICE'],
                'target_systems': ['Chassis'],
                'target_components': ['Brake_System_Hydraulic'],
                'regulatory_standards': ['UNECE_R13H'],
                'complexity_score': 6,
                'risk_level': 'critical',
                'estimated_duration_hours': 36.0,
                'estimated_cost_gbp': 8000.0,
                'historical_results': [{'passed': True}]
            }
        ]
    
    def test_recommender_initialization(self, recommender):
        """Test recommender initializes correctly."""
        assert recommender is not None
        assert recommender.weights['semantic'] == 0.4
        assert recommender.weights['graph'] == 0.3
        assert recommender.weights['rules'] == 0.2
        assert recommender.weights['historical'] == 0.1
    
    def test_semantic_score(self, recommender):
        """Test semantic similarity scoring."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        vec3 = np.array([0.0, 1.0, 0.0])
        
        score_identical = recommender.compute_semantic_score(vec1, vec2)
        score_different = recommender.compute_semantic_score(vec1, vec3)
        
        assert score_identical > 0.99
        assert score_different < 0.1
    
    def test_graph_proximity(self, recommender):
        """Test graph proximity scoring."""
        query_components = ['Component_A', 'Component_B']
        candidate_components = ['Component_A', 'Component_B', 'Component_C']
        query_systems = ['System_1']
        candidate_systems = ['System_1']
        
        score = recommender.compute_graph_proximity(
            query_components,
            candidate_components,
            query_systems,
            candidate_systems
        )
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should have good overlap
    
    def test_rules_score(self, recommender):
        """Test rules-based scoring."""
        query_spec = {
            'platform': 'EV',
            'systems': ['Battery'],
            'components': ['High_Voltage_Battery']
        }
        
        candidate = {
            'applicable_platforms': ['EV'],
            'target_systems': ['Battery', 'Thermal'],
            'target_components': ['High_Voltage_Battery', 'Battery_Management_System'],
            'regulatory_standards': ['UNECE_R100', 'ISO_6469']
        }
        
        score, rules_fired = recommender.compute_rules_score(query_spec, candidate)
        
        assert 0 <= score <= 1
        assert len(rules_fired) > 0
        assert any('Platform match' in rule for rule in rules_fired)
    
    def test_historical_score(self, recommender):
        """Test historical success scoring."""
        # High pass rate
        candidate1 = {
            'historical_results': [{'passed': True}, {'passed': True}, {'passed': True}]
        }
        score1 = recommender.compute_historical_score(candidate1)
        
        # Low pass rate
        candidate2 = {
            'historical_results': [{'passed': False}, {'passed': False}, {'passed': True}]
        }
        score2 = recommender.compute_historical_score(candidate2)
        
        # No history
        candidate3 = {
            'historical_results': []
        }
        score3 = recommender.compute_historical_score(candidate3)
        
        assert score1 > score2
        assert score3 == 0.5  # Neutral
    
    def test_recommend(self, recommender, sample_candidates):
        """Test complete recommendation workflow."""
        query_spec = {
            'platform': 'EV',
            'systems': ['Battery', 'Powertrain'],
            'components': ['High_Voltage_Battery', 'Electric_Motor'],
            'description': 'Testing for EV battery and motor'
        }
        
        recommendations = recommender.recommend(query_spec, sample_candidates, top_k=2)
        
        assert len(recommendations) <= 2
        assert len(recommendations) > 0
        
        # Check structure
        first_rec = recommendations[0]
        assert 'scenario_id' in first_rec
        assert 'score' in first_rec
        assert 'explain' in first_rec
        assert 'metadata' in first_rec
        
        # Check explain structure
        explain = first_rec['explain']
        assert 'scores' in explain
        assert 'rules_fired' in explain
        assert 'notes' in explain
        
        # Scores should be sorted descending
        if len(recommendations) > 1:
            assert recommendations[0]['score'] >= recommendations[1]['score']
    
    def test_recommend_for_vehicle(self, recommender, sample_candidates):
        """Test vehicle-based recommendation convenience method."""
        recommendations = recommender.recommend_for_vehicle(
            vehicle_model='Ariya',
            platform='EV',
            systems=['Battery'],
            components=['High_Voltage_Battery'],
            candidates=sample_candidates,
            top_k=3
        )
        
        assert len(recommendations) > 0
        assert recommendations[0]['score'] > 0
    
    def test_explain_recommendation(self, recommender, sample_candidates):
        """Test explanation generation."""
        query_spec = {
            'platform': 'EV',
            'systems': ['Battery'],
            'components': []
        }
        
        recommendations = recommender.recommend(query_spec, sample_candidates, top_k=1)
        
        if recommendations:
            explanation = recommender.explain_recommendation(recommendations[0], verbose=True)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 0
            assert 'Score' in explanation or 'score' in explanation


class TestJaccardSimilarity:
    """Test Jaccard similarity functions."""
    
    def test_set_jaccard(self):
        """Test set-based Jaccard similarity."""
        set1 = {1, 2, 3}
        set2 = {2, 3, 4}
        set3 = {1, 2, 3}
        
        sim_overlap = jaccard_similarity(set1, set2)
        sim_identical = jaccard_similarity(set1, set3)
        sim_disjoint = jaccard_similarity({1, 2}, {3, 4})
        
        assert 0 < sim_overlap < 1
        assert sim_identical == 1.0
        assert sim_disjoint == 0.0
    
    def test_text_jaccard(self):
        """Test text-based Jaccard similarity."""
        text1 = "Battery thermal test for EV"
        text2 = "Battery thermal validation for EV"
        text3 = "Motor performance test"
        
        sim_similar = text_jaccard_similarity(text1, text2)
        sim_different = text_jaccard_similarity(text1, text3)
        
        assert sim_similar > sim_different
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1


@pytest.mark.skipif(not HDBSCAN_AVAILABLE, reason="HDBSCAN not installed")
class TestDuplicateDetector:
    """Test duplicate detection (requires HDBSCAN)."""
    
    @pytest.fixture
    def detector(self):
        """Create duplicate detector instance."""
        return DuplicateDetector(min_cluster_size=2, similarity_threshold=0.85)
    
    @pytest.fixture
    def sample_scenarios_with_duplicates(self):
        """Create sample scenarios with some duplicates."""
        return [
            {
                'scenario_id': 'TEST-001',
                'test_name': 'Battery Thermal Test',
                'test_type': 'performance',
                'target_components': ['High_Voltage_Battery', 'BMS'],
                'target_systems': ['Battery', 'Thermal'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['UNECE_R100'],
                'embedding': np.random.rand(100),
                'historical_results': [{'passed': True}]
            },
            {
                'scenario_id': 'TEST-002',
                'test_name': 'Battery Thermal Validation',  # Similar to TEST-001
                'test_type': 'performance',
                'target_components': ['High_Voltage_Battery', 'BMS'],
                'target_systems': ['Battery', 'Thermal'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['UNECE_R100'],
                'embedding': np.random.rand(100) * 0.1 + np.random.rand(100),  # Similar embedding
                'historical_results': []
            },
            {
                'scenario_id': 'TEST-003',
                'test_name': 'Motor Performance Test',  # Different
                'test_type': 'performance',
                'target_components': ['Electric_Motor'],
                'target_systems': ['Powertrain'],
                'applicable_platforms': ['EV', 'HEV'],
                'regulatory_standards': ['ISO_8854'],
                'embedding': np.random.rand(100) + 10,  # Very different embedding
                'historical_results': []
            }
        ]
    
    def test_detector_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert detector.min_cluster_size == 2
        assert detector.similarity_threshold == 0.85
    
    def test_detailed_similarity(self, detector):
        """Test detailed similarity computation."""
        scenario1 = {
            'scenario_id': 'TEST-001',
            'test_name': 'Battery Thermal Test',
            'test_type': 'performance',
            'target_components': ['Battery', 'BMS'],
            'target_systems': ['Battery'],
            'applicable_platforms': ['EV'],
            'regulatory_standards': ['UNECE_R100']
        }
        
        scenario2 = {
            'scenario_id': 'TEST-002',
            'test_name': 'Battery Thermal Validation',
            'test_type': 'performance',
            'target_components': ['Battery', 'BMS', 'Thermal'],
            'target_systems': ['Battery', 'Thermal'],
            'applicable_platforms': ['EV'],
            'regulatory_standards': ['UNECE_R100', 'ISO_6469']
        }
        
        similarity = detector._compute_detailed_similarity(scenario1, scenario2)
        
        assert 'overall' in similarity
        assert 'name' in similarity
        assert 'components' in similarity
        assert 'systems' in similarity
        assert 0 <= similarity['overall'] <= 1
    
    def test_select_canonical(self, detector):
        """Test canonical scenario selection."""
        scenarios = [
            {
                'scenario_id': 'TEST-001',
                'historical_results': [{'passed': True}],
                'target_components': ['A', 'B']
            },
            {
                'scenario_id': 'TEST-002',
                'historical_results': [{'passed': True}, {'passed': True}],
                'target_components': ['A', 'B', 'C']
            }
        ]
        
        canonical = detector._select_canonical(scenarios)
        
        assert canonical['scenario_id'] == 'TEST-002'  # More executions and components
    
    def test_find_similar_pairs(self, detector):
        """Test finding similar pairs."""
        scenarios = [
            {
                'scenario_id': 'TEST-001',
                'test_name': 'Test A',
                'test_type': 'performance',
                'target_components': ['A', 'B'],
                'target_systems': ['S1'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['R1']
            },
            {
                'scenario_id': 'TEST-002',
                'test_name': 'Test B',
                'test_type': 'performance',
                'target_components': ['A', 'B'],
                'target_systems': ['S1'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['R1']
            }
        ]
        
        pairs = detector.find_similar_pairs(scenarios, threshold=0.5)
        
        assert isinstance(pairs, list)
        # Should find at least one similar pair with high similarity
        if pairs:
            assert 'similarity' in pairs[0]
            assert pairs[0]['similarity'] >= 0.5


class TestIntegration:
    """Integration tests for recommendation workflow."""
    
    def test_end_to_end_recommendation(self):
        """Test complete recommendation workflow."""
        recommender = create_recommender()
        
        query = {
            'platform': 'EV',
            'systems': ['Battery'],
            'components': ['High_Voltage_Battery']
        }
        
        candidates = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'test_name': f'Test Scenario {i}',
                'test_type': 'performance',
                'applicable_platforms': ['EV'],
                'target_systems': ['Battery'],
                'target_components': ['High_Voltage_Battery'],
                'regulatory_standards': ['UNECE_R100'],
                'complexity_score': 5,
                'risk_level': 'medium',
                'estimated_duration_hours': 10.0,
                'estimated_cost_gbp': 5000.0,
                'historical_results': []
            }
            for i in range(5)
        ]
        
        recommendations = recommender.recommend(query, candidates, top_k=3)
        
        assert len(recommendations) > 0
        assert len(recommendations) <= 3
        
        # All recommendations should have complete structure
        for rec in recommendations:
            assert rec['score'] >= 0
            assert rec['score'] <= 1
            assert 'explain' in rec
            assert 'metadata' in rec


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

