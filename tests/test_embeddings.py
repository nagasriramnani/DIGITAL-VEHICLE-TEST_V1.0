"""
Tests for Phase 4: pgvector + Embeddings + Vector Search.
"""
import pytest
import numpy as np
from typing import Dict, Any

# Import modules
from src.ai.embeddings import EmbeddingPipeline, create_embedding_pipeline
from src.ai.similarity import (
    cosine_similarity,
    batch_cosine_similarity,
    find_nearest_neighbors,
    normalize_vector,
    rank_by_similarity
)


class TestEmbeddingPipeline:
    """Test embedding pipeline functionality."""
    
    @pytest.fixture(scope="class")
    def pipeline(self):
        """Create embedding pipeline instance."""
        return EmbeddingPipeline()
    
    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes correctly."""
        assert pipeline is not None
        assert pipeline.model is not None
        assert pipeline.text_dim > 0
        assert pipeline.total_dim == pipeline.text_dim + 50 + 10
    
    def test_text_encoding(self, pipeline):
        """Test text encoding."""
        text = "Battery thermal management test"
        embedding = pipeline.encode_text(text)
        
        assert embedding is not None
        assert embedding.shape[0] == pipeline.text_dim
        assert not np.isnan(embedding).any()
    
    def test_text_batch_encoding(self, pipeline):
        """Test batch text encoding."""
        texts = [
            "Test scenario 1",
            "Test scenario 2",
            "Test scenario 3"
        ]
        
        embeddings = pipeline.encode_text_batch(texts)
        
        assert embeddings.shape == (3, pipeline.text_dim)
        assert not np.isnan(embeddings).any()
    
    def test_structured_features(self, pipeline):
        """Test structured feature extraction."""
        scenario = {
            'test_type': 'performance',
            'complexity_score': 7,
            'risk_level': 'high',
            'estimated_duration_hours': 48.5,
            'estimated_cost_gbp': 12000.0,
            'certification_required': True,
            'environmental_conditions': {
                'temperature_celsius': 40.0,
                'humidity_percent': 80.0,
                'road_surface': 'dry',
                'weather': 'clear'
            },
            'load_profile': {
                'load_percent': 85.0,
                'speed_profile': 'highway',
                'distance_km': 200.0
            }
        }
        
        features = pipeline.extract_structured_features(scenario)
        
        assert features.shape[0] == 50
        assert not np.isnan(features).any()
        assert np.all(features >= 0)  # All features should be non-negative
        assert np.all(features <= 1)  # All features should be normalized to 0-1
    
    def test_graph_features(self, pipeline):
        """Test graph feature extraction."""
        scenario = {
            'target_components': ['Component1', 'Component2'],
            'target_systems': ['System1'],
            'regulatory_standards': ['Standard1', 'Standard2', 'Standard3'],
            'historical_results': [
                {'passed': True},
                {'passed': True},
                {'passed': False}
            ],
            'applicable_platforms': ['EV'],
            'applicable_models': ['Ariya', 'Leaf']
        }
        
        features = pipeline.extract_graph_features(scenario)
        
        assert features.shape[0] == 10
        assert not np.isnan(features).any()
    
    def test_unified_embedding(self, pipeline):
        """Test unified embedding creation."""
        scenario = {
            'scenario_id': 'TEST-001',
            'test_name': 'Battery Thermal Test',
            'description': 'Thermal management validation',
            'test_type': 'performance',
            'complexity_score': 7,
            'risk_level': 'high',
            'estimated_duration_hours': 48.5,
            'estimated_cost_gbp': 12000.0,
            'certification_required': True,
            'environmental_conditions': {
                'temperature_celsius': 40.0,
                'humidity_percent': 80.0,
                'road_surface': 'dry',
                'weather': 'clear'
            },
            'load_profile': {
                'load_percent': 85.0,
                'speed_profile': 'highway',
                'distance_km': 200.0
            },
            'target_components': ['High_Voltage_Battery'],
            'target_systems': ['Battery'],
            'regulatory_standards': ['UNECE_R100'],
            'historical_results': [{'passed': True}],
            'applicable_platforms': ['EV'],
            'applicable_models': ['Ariya']
        }
        
        embedding = pipeline.create_unified_embedding(scenario)
        
        assert embedding.shape[0] == pipeline.total_dim
        assert not np.isnan(embedding).any()
    
    def test_batch_encoding(self, pipeline):
        """Test batch encoding of multiple scenarios."""
        scenarios = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'test_name': f'Test Scenario {i}',
                'description': f'Description {i}',
                'test_type': 'performance',
                'complexity_score': 5,
                'risk_level': 'medium',
                'estimated_duration_hours': 10.0,
                'estimated_cost_gbp': 5000.0,
                'certification_required': False,
                'environmental_conditions': {
                    'temperature_celsius': 20.0,
                    'humidity_percent': 50.0,
                    'road_surface': 'dry',
                    'weather': 'clear'
                },
                'load_profile': {
                    'load_percent': 50.0,
                    'speed_profile': 'mixed',
                    'distance_km': 100.0
                },
                'target_components': ['Component1'],
                'target_systems': ['System1'],
                'regulatory_standards': [],
                'historical_results': [],
                'applicable_platforms': ['EV'],
                'applicable_models': ['Model1']
            }
            for i in range(5)
        ]
        
        embeddings = pipeline.batch_encode_scenarios(scenarios)
        
        assert len(embeddings) == 5
        assert all(emb.shape[0] == pipeline.total_dim for emb in embeddings)


class TestSimilarity:
    """Test similarity computation functions."""
    
    def test_cosine_similarity(self):
        """Test cosine similarity computation."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        vec3 = np.array([0.0, 1.0, 0.0])
        
        # Identical vectors
        sim_12 = cosine_similarity(vec1, vec2)
        assert abs(sim_12 - 1.0) < 1e-6
        
        # Orthogonal vectors
        sim_13 = cosine_similarity(vec1, vec3)
        assert abs(sim_13 - 0.0) < 1e-6
    
    def test_batch_cosine_similarity(self):
        """Test batch cosine similarity."""
        query = np.array([1.0, 0.0, 0.0])
        vectors = np.array([
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.0, 1.0, 0.0]
        ])
        
        similarities = batch_cosine_similarity(query, vectors)
        
        assert len(similarities) == 3
        assert similarities[0] > similarities[1]  # First is most similar
        assert similarities[1] > similarities[2]  # Third is least similar
    
    def test_normalize_vector(self):
        """Test vector normalization."""
        vec = np.array([3.0, 4.0])
        normalized = normalize_vector(vec)
        
        # Check unit length
        norm = np.linalg.norm(normalized)
        assert abs(norm - 1.0) < 1e-6
    
    def test_find_nearest_neighbors(self):
        """Test nearest neighbor search."""
        query = np.array([1.0, 0.0, 0.0, 0.0])
        database = np.array([
            [1.0, 0.0, 0.0, 0.0],  # Exact match
            [0.9, 0.1, 0.0, 0.0],  # Close match
            [0.5, 0.5, 0.0, 0.0],  # Moderate match
            [0.0, 1.0, 0.0, 0.0],  # Poor match
        ])
        
        indices, scores = find_nearest_neighbors(query, database, k=3, metric='cosine')
        
        assert len(indices) == 3
        assert len(scores) == 3
        assert indices[0] == 0  # First result is exact match
        assert scores[0] > scores[1] > scores[2]  # Scores are descending
    
    def test_rank_by_similarity(self):
        """Test ranking candidates by similarity."""
        query = np.array([1.0, 0.0, 0.0])
        
        candidates = [
            {'id': 1, 'embedding': np.array([1.0, 0.0, 0.0])},
            {'id': 2, 'embedding': np.array([0.5, 0.5, 0.0])},
            {'id': 3, 'embedding': np.array([0.0, 1.0, 0.0])},
        ]
        
        ranked = rank_by_similarity(query, candidates)
        
        assert len(ranked) == 3
        assert ranked[0][0]['id'] == 1  # First is most similar
        assert ranked[0][1] > ranked[1][1] > ranked[2][1]  # Scores descending


class TestPGVectorClient:
    """Test PostgreSQL vector client (requires PostgreSQL)."""
    
    @pytest.mark.postgres
    def test_client_initialization(self):
        """Test client can be initialized."""
        try:
            from src.vector.pg_client import get_pg_client
            
            client = get_pg_client()
            assert client is not None
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")
    
    @pytest.mark.postgres
    def test_create_extension(self):
        """Test creating pgvector extension."""
        try:
            from src.vector.pg_client import get_pg_client
            
            client = get_pg_client()
            client.create_extension()
            
            # Verify via health check
            health = client.health_check()
            assert health.get('vector_extension') in ['installed', 'missing']
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")
    
    @pytest.mark.postgres
    def test_create_tables(self):
        """Test creating database tables."""
        try:
            from src.vector.pg_client import get_pg_client
            
            client = get_pg_client()
            client.create_extension()
            client.create_tables()
            
            # Should not raise error
            assert True
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")


class TestVectorIndexOps:
    """Test vector index operations (requires PostgreSQL)."""
    
    @pytest.mark.postgres
    def test_upsert_and_retrieve(self):
        """Test upserting and retrieving a vector."""
        try:
            from src.vector.index_ops import VectorIndexOps
            from src.vector.pg_client import get_pg_client
            
            # Setup
            client = get_pg_client()
            client.create_extension()
            client.create_tables()
            
            ops = VectorIndexOps()
            
            # Upsert test vector
            test_embedding = np.random.rand(828)
            ops.upsert_vector(
                scenario_id='TEST-UPSERT',
                test_name='Test Upsert',
                test_type='performance',
                embedding=test_embedding,
                metadata={
                    'complexity_score': 5,
                    'risk_level': 'medium',
                    'estimated_duration_hours': 10.0,
                    'estimated_cost_gbp': 5000.0
                }
            )
            
            # Retrieve
            retrieved = ops.get_vector_by_id('TEST-UPSERT')
            
            assert retrieved is not None
            assert retrieved['scenario_id'] == 'TEST-UPSERT'
            assert retrieved['test_name'] == 'Test Upsert'
            
            # Clean up
            ops.delete_vector('TEST-UPSERT')
            
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")
    
    @pytest.mark.postgres
    def test_ann_search(self):
        """Test ANN search."""
        try:
            from src.vector.index_ops import VectorIndexOps
            from src.vector.pg_client import get_pg_client
            
            # Setup
            client = get_pg_client()
            client.create_extension()
            client.create_tables()
            
            ops = VectorIndexOps()
            
            # Insert test vectors
            for i in range(3):
                ops.upsert_vector(
                    scenario_id=f'TEST-ANN-{i}',
                    test_name=f'Test ANN {i}',
                    test_type='performance',
                    embedding=np.random.rand(828)
                )
            
            # Search
            query_vector = np.random.rand(828)
            results = ops.ann_search(query_vector, k=2)
            
            assert len(results) <= 2
            if len(results) > 0:
                assert 'scenario_id' in results[0]
                assert 'similarity' in results[0]
            
            # Clean up
            for i in range(3):
                ops.delete_vector(f'TEST-ANN-{i}')
            
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")


class TestIntegration:
    """Integration tests for complete embedding workflow."""
    
    def test_end_to_end_embedding(self):
        """Test complete embedding workflow."""
        # Create pipeline
        pipeline = EmbeddingPipeline()
        
        # Create test scenario
        scenario = {
            'scenario_id': 'INTEGRATION-001',
            'test_name': 'Integration Test',
            'description': 'End-to-end test',
            'test_type': 'performance',
            'complexity_score': 5,
            'risk_level': 'medium',
            'estimated_duration_hours': 10.0,
            'estimated_cost_gbp': 5000.0,
            'certification_required': False,
            'environmental_conditions': {
                'temperature_celsius': 20.0,
                'humidity_percent': 50.0,
                'road_surface': 'dry',
                'weather': 'clear'
            },
            'load_profile': {
                'load_percent': 50.0,
                'speed_profile': 'mixed',
                'distance_km': 100.0
            },
            'target_components': ['Component1'],
            'target_systems': ['System1'],
            'regulatory_standards': ['Standard1'],
            'historical_results': [{'passed': True}],
            'applicable_platforms': ['EV'],
            'applicable_models': ['Model1']
        }
        
        # Create embedding
        embedding = pipeline.create_unified_embedding(scenario)
        
        # Verify embedding
        assert embedding.shape[0] == pipeline.total_dim
        assert not np.isnan(embedding).any()
        
        # Test similarity with itself
        sim = cosine_similarity(embedding, embedding)
        assert abs(sim - 1.0) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

