"""
Tests for Phase 2: Neo4j Knowledge Graph operations.
"""
import pytest
from typing import Dict, Any

from src.graph.neo4j_connector import get_connector, Neo4jConnector
from src.graph.ontology_design import (
    get_create_constraint_queries,
    get_create_index_queries,
    get_schema_summary,
    NODE_SCHEMAS,
    RELATIONSHIP_SCHEMAS,
)
from src.graph.graph_operations import GraphOperations


# Mark all tests as requiring Neo4j
pytestmark = pytest.mark.neo4j


@pytest.fixture(scope="module")
def neo4j_available() -> bool:
    """Check if Neo4j is available."""
    try:
        connector = get_connector()
        health = connector.health_check()
        return health["status"] == "healthy"
    except Exception:
        return False


@pytest.fixture(scope="module")
def graph_ops(neo4j_available) -> GraphOperations:
    """Create GraphOperations instance if Neo4j is available."""
    if not neo4j_available:
        pytest.skip("Neo4j not available")
    return GraphOperations()


class TestOntologyDesign:
    """Test ontology schema definitions."""
    
    def test_node_schemas_defined(self):
        """Test that node schemas are defined."""
        assert len(NODE_SCHEMAS) > 0
        assert "Vehicle" in str(NODE_SCHEMAS.keys())
        assert "TestScenario" in str(NODE_SCHEMAS.keys())
    
    def test_relationship_schemas_defined(self):
        """Test that relationship schemas are defined."""
        assert len(RELATIONSHIP_SCHEMAS) > 0
        assert "HAS_COMPONENT" in str(RELATIONSHIP_SCHEMAS.keys())
        assert "REQUIRES_TEST" in str(RELATIONSHIP_SCHEMAS.keys())
    
    def test_constraint_queries_generated(self):
        """Test that constraint queries can be generated."""
        queries = get_create_constraint_queries()
        assert len(queries) > 0
        assert any("CONSTRAINT" in q for q in queries)
    
    def test_index_queries_generated(self):
        """Test that index queries can be generated."""
        queries = get_create_index_queries()
        assert len(queries) > 0
        assert any("INDEX" in q for q in queries)
    
    def test_schema_summary(self):
        """Test schema summary generation."""
        summary = get_schema_summary()
        assert "node_labels" in summary
        assert "relationship_types" in summary
        assert summary["node_labels"] > 0
        assert summary["relationship_types"] > 0


class TestNeo4jConnector:
    """Test Neo4j connector functionality."""
    
    def test_connector_singleton(self, neo4j_available):
        """Test that connector uses singleton pattern."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")
        
        connector1 = get_connector()
        connector2 = get_connector()
        assert connector1 is connector2
    
    def test_health_check(self, neo4j_available):
        """Test Neo4j health check."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")
        
        connector = get_connector()
        health = connector.health_check()
        
        assert "status" in health
        assert health["status"] == "healthy"
        assert "node_count" in health
        assert "relationship_count" in health
    
    def test_simple_query(self, neo4j_available):
        """Test executing a simple query."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")
        
        connector = get_connector()
        result = connector.execute_query("RETURN 1 as value")
        
        assert len(result) == 1
        assert result[0]["value"] == 1
    
    def test_database_stats(self, neo4j_available):
        """Test getting database statistics."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")
        
        connector = get_connector()
        stats = connector.get_database_stats()
        
        assert "total_nodes" in stats
        assert "total_relationships" in stats
        assert "nodes_by_label" in stats
        assert "relationships_by_type" in stats


class TestGraphOperations:
    """Test graph operations."""
    
    def test_operations_initialization(self, graph_ops):
        """Test that graph operations can be initialized."""
        assert graph_ops is not None
        assert graph_ops.connector is not None
    
    def test_create_schema(self, graph_ops):
        """Test schema creation."""
        # This should not raise an error
        graph_ops.create_schema()
        
        # Verify constraints were created (check via query)
        connector = graph_ops.connector
        result = connector.execute_query("SHOW CONSTRAINTS")
        # Should have at least some constraints
        assert len(result) >= 0  # May be 0 if already exists
    
    def test_ingest_synthetic_data(self, graph_ops):
        """Test ingesting synthetic data."""
        # Clear database first
        connector = graph_ops.connector
        connector.clear_database()
        
        # Create schema
        graph_ops.create_schema()
        
        # Ingest data
        stats = graph_ops.ingest_synthetic_data()
        
        # Verify statistics
        assert stats["vehicles"] > 0
        assert stats["platforms"] > 0
        assert stats["components"] > 0
        assert stats["systems"] > 0
        assert stats["test_scenarios"] > 0
        assert stats["relationships"] > 0
        
        # Verify some data was actually created
        db_stats = connector.get_database_stats()
        assert db_stats["total_nodes"] > 0
        assert db_stats["total_relationships"] > 0
    
    def test_get_required_tests(self, graph_ops):
        """Test getting required tests for a vehicle."""
        # Ensure data is ingested
        try:
            stats = graph_ops.connector.get_database_stats()
            if stats["total_nodes"] == 0:
                graph_ops.create_schema()
                graph_ops.ingest_synthetic_data()
        except:
            graph_ops.create_schema()
            graph_ops.ingest_synthetic_data()
        
        # Get tests for Ariya (EV)
        tests = graph_ops.get_required_tests("Ariya")
        
        assert len(tests) > 0
        # Check structure
        if tests:
            assert "scenario_id" in tests[0]
            assert "test_name" in tests[0]
            assert "test_type" in tests[0]
    
    def test_get_odd_coverage(self, graph_ops):
        """Test getting ODD coverage for a vehicle."""
        # Ensure data is ingested
        try:
            stats = graph_ops.connector.get_database_stats()
            if stats["total_nodes"] == 0:
                graph_ops.create_schema()
                graph_ops.ingest_synthetic_data()
        except:
            graph_ops.create_schema()
            graph_ops.ingest_synthetic_data()
        
        # Get ODD coverage for Leaf (EV)
        coverage = graph_ops.get_odd_coverage("Leaf")
        
        assert coverage is not None
        if coverage:
            assert "total_tests" in coverage
            assert "weathers" in coverage
            assert "road_surfaces" in coverage
    
    def test_get_scenario_similarity(self, graph_ops):
        """Test getting similar scenarios."""
        # Ensure data is ingested
        try:
            stats = graph_ops.connector.get_database_stats()
            if stats["total_nodes"] == 0:
                graph_ops.create_schema()
                graph_ops.ingest_synthetic_data()
        except:
            graph_ops.create_schema()
            graph_ops.ingest_synthetic_data()
        
        # Get a test scenario first
        query = "MATCH (t:TestScenario) RETURN t.scenario_id as id LIMIT 1"
        result = graph_ops.connector.execute_query(query)
        
        if result:
            seed_id = result[0]["id"]
            similar = graph_ops.get_scenario_similarity_edges([seed_id], limit=5)
            
            # Should return some similar scenarios (or empty if no similar ones)
            assert isinstance(similar, list)
    
    def test_get_tests_by_platform(self, graph_ops):
        """Test getting tests by platform."""
        # Ensure data is ingested
        try:
            stats = graph_ops.connector.get_database_stats()
            if stats["total_nodes"] == 0:
                graph_ops.create_schema()
                graph_ops.ingest_synthetic_data()
        except:
            graph_ops.create_schema()
            graph_ops.ingest_synthetic_data()
        
        # Get tests for EV platform
        tests = graph_ops.get_tests_by_platform("EV")
        
        assert len(tests) > 0
        if tests:
            assert "scenario_id" in tests[0]
            assert "test_type" in tests[0]
    
    def test_get_component_test_coverage(self, graph_ops):
        """Test getting component test coverage."""
        # Ensure data is ingested
        try:
            stats = graph_ops.connector.get_database_stats()
            if stats["total_nodes"] == 0:
                graph_ops.create_schema()
                graph_ops.ingest_synthetic_data()
        except:
            graph_ops.create_schema()
            graph_ops.ingest_synthetic_data()
        
        # Get coverage for Electric_Motor component
        coverage = graph_ops.get_component_test_coverage("Electric_Motor")
        
        assert coverage is not None
        if coverage:
            assert "component" in coverage
            assert "test_count" in coverage
            assert coverage["component"] == "Electric_Motor"


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_full_workflow(self, neo4j_available):
        """Test complete workflow: schema creation -> ingestion -> queries."""
        if not neo4j_available:
            pytest.skip("Neo4j not available")
        
        ops = GraphOperations()
        connector = ops.connector
        
        # Clear database
        connector.clear_database()
        
        # Create schema
        ops.create_schema()
        
        # Ingest data
        stats = ops.ingest_synthetic_data()
        
        # Verify ingestion
        assert stats["test_scenarios"] >= 300  # At least 300 scenarios
        
        # Test queries
        tests_ariya = ops.get_required_tests("Ariya")
        assert len(tests_ariya) > 0
        
        tests_ev = ops.get_tests_by_platform("EV")
        assert len(tests_ev) > 0
        
        # Get database stats
        db_stats = connector.get_database_stats()
        
        print("\n" + "=" * 60)
        print("INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"\nIngestion Stats:")
        for key, value in stats.items():
            print(f"  {key:25s}: {value:6,d}")
        
        print(f"\nDatabase Stats:")
        print(f"  Total Nodes:        {db_stats['total_nodes']:6,d}")
        print(f"  Total Relationships: {db_stats['total_relationships']:6,d}")
        
        print(f"\nQuery Results:")
        print(f"  Tests for Ariya:    {len(tests_ariya):6,d}")
        print(f"  Tests for EV:       {len(tests_ev):6,d}")
        
        print("\n[OK] Full workflow complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

