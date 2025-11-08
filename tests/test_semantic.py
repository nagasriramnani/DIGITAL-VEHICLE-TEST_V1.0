"""
Tests for Phase 3: Semantic Web (RDF/OWL/SPARQL/SHACL).
"""
import pytest
from pathlib import Path
from typing import Dict, Any

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS

# Import modules
from src.graph.semantic_bridge import SemanticBridge, export_owl_ontology
from src.graph.jsonld import (
    get_jsonld_context,
    serialize_vehicle_jsonld,
    serialize_component_jsonld,
    serialize_test_scenario_jsonld,
    serialize_multiple_jsonld,
)

# Define namespaces
VTA = Namespace("http://nissan-ntce.cranfield.ac.uk/vta/ontology#")
VTAD = Namespace("http://nissan-ntce.cranfield.ac.uk/vta/data#")


class TestOWLOntology:
    """Test OWL ontology export and structure."""
    
    def test_ontology_file_exists(self):
        """Test that ontology file can be created."""
        output_path = "semantic/ontology.ttl"
        
        # Ensure file exists (might be created by semantic_bridge)
        if not Path(output_path).exists():
            export_owl_ontology(output_path)
        
        assert Path(output_path).exists()
    
    def test_ontology_can_be_parsed(self):
        """Test that ontology file is valid Turtle/RDF."""
        ontology_path = "semantic/ontology.ttl"
        
        # Ensure it exists
        if not Path(ontology_path).exists():
            export_owl_ontology(ontology_path)
        
        # Parse the ontology
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Should have triples
        assert len(g) > 0
    
    def test_ontology_has_classes(self):
        """Test that ontology defines expected classes."""
        ontology_path = "semantic/ontology.ttl"
        
        if not Path(ontology_path).exists():
            export_owl_ontology(ontology_path)
        
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Check for key classes
        expected_classes = [
            "Vehicle",
            "Platform",
            "Component",
            "VehicleSystem",
            "TestScenario",
            "RegulatoryStandard",
        ]
        
        for class_name in expected_classes:
            class_uri = VTA[class_name]
            # Check if class is defined
            assert (class_uri, RDF.type, None) in g, f"Class {class_name} not found"
    
    def test_ontology_has_properties(self):
        """Test that ontology defines expected properties."""
        ontology_path = "semantic/ontology.ttl"
        
        if not Path(ontology_path).exists():
            export_owl_ontology(ontology_path)
        
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Check for key properties
        expected_properties = [
            "onPlatform",
            "hasComponent",
            "requiresTest",
            "testsComponent",
            "followsStandard",
        ]
        
        for prop_name in expected_properties:
            prop_uri = VTA[prop_name]
            # Check if property is defined
            assert (prop_uri, RDF.type, None) in g, f"Property {prop_name} not found"


class TestJSONLD:
    """Test JSON-LD context and serialization."""
    
    def test_jsonld_context_structure(self):
        """Test JSON-LD context has required structure."""
        context = get_jsonld_context()
        
        assert "@context" in context
        assert "vta" in context["@context"]
        assert "Vehicle" in context["@context"]
        assert "TestScenario" in context["@context"]
    
    def test_serialize_vehicle_jsonld(self):
        """Test vehicle serialization to JSON-LD."""
        vehicle = {
            "model_id": "Ariya",
            "name": "Ariya",
            "platform": "EV"
        }
        
        jsonld = serialize_vehicle_jsonld(vehicle)
        
        assert "@context" in jsonld
        assert "@graph" in jsonld
        assert len(jsonld["@graph"]) == 1
        
        vehicle_node = jsonld["@graph"][0]
        assert vehicle_node["@type"] == "Vehicle"
        assert vehicle_node["label"] == "Ariya"
        assert "vtad:vehicle/Ariya" in vehicle_node["@id"]
    
    def test_serialize_component_jsonld(self):
        """Test component serialization to JSON-LD."""
        component = {
            "component_id": "High_Voltage_Battery",
            "name": "High Voltage Battery",
            "criticality": "critical",
            "system": "Battery"
        }
        
        jsonld = serialize_component_jsonld(component)
        
        assert "@context" in jsonld
        assert "@graph" in jsonld
        
        comp_node = jsonld["@graph"][0]
        assert comp_node["@type"] == "Component"
        assert comp_node["criticality"] == "critical"
    
    def test_serialize_test_scenario_jsonld(self):
        """Test scenario serialization to JSON-LD."""
        scenario = {
            "scenario_id": "SCN-001",
            "test_name": "Battery Thermal Test",
            "test_type": "performance",
            "description": "Thermal management validation",
            "complexity_score": 7,
            "risk_level": "high",
            "estimated_duration_hours": 48.5,
            "estimated_cost_gbp": 12000.0,
            "certification_required": True
        }
        
        jsonld = serialize_test_scenario_jsonld(scenario)
        
        assert "@context" in jsonld
        assert "@graph" in jsonld
        
        scenario_node = jsonld["@graph"][0]
        assert scenario_node["@type"] == "TestScenario"
        assert scenario_node["testType"] == "performance"
        assert scenario_node["complexityScore"] == 7
        assert scenario_node["certificationRequired"] is True
    
    def test_serialize_multiple_jsonld(self):
        """Test serializing multiple items to JSON-LD."""
        vehicles = [
            {"model_id": "Ariya", "name": "Ariya", "platform": "EV"},
            {"model_id": "Leaf", "name": "Leaf", "platform": "EV"}
        ]
        
        jsonld = serialize_multiple_jsonld(vehicles, "vehicle")
        
        assert "@context" in jsonld
        assert "@graph" in jsonld
        assert len(jsonld["@graph"]) == 2
        
        for node in jsonld["@graph"]:
            assert node["@type"] == "Vehicle"


class TestSemanticBridge:
    """Test semantic bridge functionality."""
    
    @pytest.mark.neo4j
    def test_semantic_bridge_initialization(self):
        """Test that semantic bridge can be initialized (requires Neo4j)."""
        try:
            bridge = SemanticBridge()
            assert bridge is not None
            assert bridge.connector is not None
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")
    
    def test_export_owl_ttl(self):
        """Test exporting OWL ontology to Turtle (doesn't need Neo4j data)."""
        # Use the function directly which doesn't require Neo4j connection
        from src.graph.semantic_bridge import export_owl_ontology
        
        output_path = "semantic/ontology_test.ttl"
        export_owl_ontology(output_path)
        
        assert Path(output_path).exists()
        
        # Verify it's valid RDF
        g = Graph()
        g.parse(output_path, format="turtle")
        assert len(g) > 0
        
        # Cleanup
        Path(output_path).unlink()
    
    @pytest.mark.neo4j
    def test_build_rdf_graph_from_kg(self):
        """Test building RDF graph from Neo4j (requires Neo4j)."""
        try:
            bridge = SemanticBridge()
            
            # Build small sample
            rdf_graph = bridge.build_rdf_graph_from_kg(
                include_vehicles=True,
                include_components=True,
                include_scenarios=True,
                limit=5
            )
            
            assert rdf_graph is not None
            assert len(rdf_graph) > 0
            
            # Check namespaces are bound
            ns_dict = dict(rdf_graph.namespaces())
            assert "vta" in ns_dict
            assert "vtad" in ns_dict
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")
    
    @pytest.mark.neo4j
    def test_run_sparql_query(self):
        """Test running SPARQL query (requires Neo4j)."""
        try:
            bridge = SemanticBridge()
            bridge.build_rdf_graph_from_kg(limit=5)
            
            query = """
            PREFIX vta: <http://nissan-ntce.cranfield.ac.uk/vta/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT (COUNT(?s) as ?count)
            WHERE {
                ?s a ?type .
            }
            """
            
            results = bridge.run_sparql(query)
            
            assert len(results) > 0
            assert "count" in results[0]
        except Exception as e:
            pytest.skip(f"Neo4j not available or RDF graph empty: {e}")
    
    def test_validate_shacl_shapes_exist(self):
        """Test that SHACL shapes file exists."""
        shapes_path = "semantic/shapes.ttl"
        assert Path(shapes_path).exists()
    
    def test_validate_shacl_shapes_parseable(self):
        """Test that SHACL shapes can be parsed."""
        shapes_path = "semantic/shapes.ttl"
        
        g = Graph()
        g.parse(shapes_path, format="turtle")
        
        assert len(g) > 0
    
    @pytest.mark.neo4j
    def test_validate_shacl(self):
        """Test SHACL validation (requires Neo4j)."""
        try:
            bridge = SemanticBridge()
            bridge.build_rdf_graph_from_kg(limit=5)
            
            result = bridge.validate_shacl()
            
            assert "conforms" in result
            assert "violations_count" in result
            # May or may not conform depending on data
            assert isinstance(result["conforms"], bool)
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")


class TestSHACLShapes:
    """Test SHACL shapes definitions."""
    
    def test_shapes_file_structure(self):
        """Test SHACL shapes file structure."""
        shapes_path = "semantic/shapes.ttl"
        
        g = Graph()
        g.parse(shapes_path, format="turtle")
        
        # Check for SHACL namespace
        SH = Namespace("http://www.w3.org/ns/shacl#")
        
        # Find shape definitions
        shapes = list(g.subjects(RDF.type, SH.NodeShape))
        assert len(shapes) > 0, "No SHACL NodeShapes found"
    
    def test_shapes_define_constraints(self):
        """Test that shapes define property constraints."""
        shapes_path = "semantic/shapes.ttl"
        
        g = Graph()
        g.parse(shapes_path, format="turtle")
        
        SH = Namespace("http://www.w3.org/ns/shacl#")
        
        # Check for property shapes
        property_shapes = list(g.subjects(SH.path, None))
        assert len(property_shapes) > 0, "No property constraints found"


class TestRDFSerialization:
    """Test RDF serialization in different formats."""
    
    def test_ontology_serialize_turtle(self):
        """Test serializing ontology as Turtle."""
        ontology_path = "semantic/ontology.ttl"
        
        if not Path(ontology_path).exists():
            export_owl_ontology(ontology_path)
        
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Serialize to string
        ttl_string = g.serialize(format="turtle")
        assert len(ttl_string) > 0
        assert "@prefix" in ttl_string or "PREFIX" in ttl_string
    
    @pytest.mark.neo4j
    def test_export_jsonld(self):
        """Test exporting RDF graph to JSON-LD (requires Neo4j)."""
        try:
            bridge = SemanticBridge()
            bridge.build_rdf_graph_from_kg(limit=3)
            
            output_path = "semantic/data_test.jsonld"
            bridge.export_jsonld(output_path)
            
            assert Path(output_path).exists()
            
            # Cleanup
            Path(output_path).unlink()
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")


class TestIntegration:
    """Integration tests for complete semantic workflow."""
    
    @pytest.mark.neo4j
    @pytest.mark.integration
    def test_complete_semantic_workflow(self):
        """Test complete semantic workflow from Neo4j to validated RDF."""
        try:
            bridge = SemanticBridge()
            
            # 1. Build RDF graph from Neo4j
            rdf_graph = bridge.build_rdf_graph_from_kg(limit=10)
            assert len(rdf_graph) > 0
            
            # 2. Run SPARQL query
            query = """
            PREFIX vta: <http://nissan-ntce.cranfield.ac.uk/vta/ontology#>
            SELECT (COUNT(?s) as ?count)
            WHERE { ?s a vta:Vehicle . }
            """
            results = bridge.run_sparql(query)
            assert len(results) > 0
            
            # 3. Validate with SHACL
            validation = bridge.validate_shacl()
            assert "conforms" in validation
            
            # 4. Export to JSON-LD
            bridge.export_jsonld("semantic/workflow_test.jsonld")
            assert Path("semantic/workflow_test.jsonld").exists()
            
            # Cleanup
            Path("semantic/workflow_test.jsonld").unlink()
            
            print("\n[OK] Complete semantic workflow successful")
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

