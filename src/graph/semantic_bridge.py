"""
Semantic Web bridge for exporting Neo4j graph to RDF/OWL and enabling SPARQL queries.
Provides interoperability with semantic web standards.
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
from rdflib.namespace import XSD, DCTERMS, SKOS
from pyshacl import validate

from src.graph.neo4j_connector import get_connector

logger = logging.getLogger(__name__)


# Define custom namespaces for VTA ontology
VTA = Namespace("http://nissan-ntce.cranfield.ac.uk/vta/ontology#")
VTAD = Namespace("http://nissan-ntce.cranfield.ac.uk/vta/data#")


class SemanticBridge:
    """
    Bridge between Neo4j property graph and RDF semantic web.
    Enables RDF export, SPARQL queries, and SHACL validation.
    """
    
    def __init__(self):
        """Initialize semantic bridge."""
        self.connector = get_connector()
        self.rdf_graph = None
    
    def build_rdf_graph_from_kg(
        self,
        include_vehicles: bool = True,
        include_components: bool = True,
        include_scenarios: bool = True,
        limit: Optional[int] = None
    ) -> Graph:
        """
        Build RDF graph from Neo4j knowledge graph.
        
        Args:
            include_vehicles: Include vehicle nodes
            include_components: Include component nodes
            include_scenarios: Include test scenario nodes
            limit: Limit number of scenarios to export (for testing)
            
        Returns:
            RDFLib Graph with triples from knowledge graph
        """
        logger.info("Building RDF graph from Neo4j knowledge graph...")
        
        g = Graph()
        
        # Bind namespaces
        g.bind("vta", VTA)
        g.bind("vtad", VTAD)
        g.bind("owl", OWL)
        g.bind("dcterms", DCTERMS)
        g.bind("skos", SKOS)
        
        # Export Vehicles
        if include_vehicles:
            self._export_vehicles_to_rdf(g)
        
        # Export Platforms
        self._export_platforms_to_rdf(g)
        
        # Export Components
        if include_components:
            self._export_components_to_rdf(g)
        
        # Export Systems
        self._export_systems_to_rdf(g)
        
        # Export Test Scenarios
        if include_scenarios:
            self._export_scenarios_to_rdf(g, limit=limit)
        
        # Export Regulatory Standards
        self._export_standards_to_rdf(g)
        
        logger.info(f"RDF graph built: {len(g)} triples")
        self.rdf_graph = g
        return g
    
    def _export_vehicles_to_rdf(self, g: Graph) -> None:
        """Export vehicles to RDF."""
        query = """
        MATCH (v:Vehicle)-[:ON_PLATFORM]->(p:Platform)
        RETURN v.model_id as id, v.name as name, v.platform as platform
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            vehicle_uri = VTAD[f"vehicle/{row['id']}"]
            
            # Type assertion
            g.add((vehicle_uri, RDF.type, VTA.Vehicle))
            
            # Properties
            g.add((vehicle_uri, RDFS.label, Literal(row['name'])))
            g.add((vehicle_uri, VTA.modelId, Literal(row['id'])))
            
            # Platform relationship
            platform_uri = VTAD[f"platform/{row['platform']}"]
            g.add((vehicle_uri, VTA.onPlatform, platform_uri))
    
    def _export_platforms_to_rdf(self, g: Graph) -> None:
        """Export platforms to RDF."""
        query = """
        MATCH (p:Platform)
        RETURN p.platform_id as id, p.name as name, p.description as description
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            platform_uri = VTAD[f"platform/{row['id']}"]
            
            g.add((platform_uri, RDF.type, VTA.Platform))
            g.add((platform_uri, RDFS.label, Literal(row['name'])))
            if row.get('description'):
                g.add((platform_uri, DCTERMS.description, Literal(row['description'])))
    
    def _export_components_to_rdf(self, g: Graph) -> None:
        """Export components to RDF."""
        query = """
        MATCH (c:Component)-[:BELONGS_TO_SYSTEM]->(s:VehicleSystem)
        RETURN c.component_id as id, c.name as name, 
               c.criticality as criticality, s.system_id as system
        LIMIT 100
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            component_uri = VTAD[f"component/{row['id']}"]
            
            g.add((component_uri, RDF.type, VTA.Component))
            g.add((component_uri, RDFS.label, Literal(row['name'])))
            g.add((component_uri, VTA.criticality, Literal(row['criticality'])))
            
            # System relationship
            system_uri = VTAD[f"system/{row['system']}"]
            g.add((component_uri, VTA.belongsToSystem, system_uri))
    
    def _export_systems_to_rdf(self, g: Graph) -> None:
        """Export vehicle systems to RDF."""
        query = """
        MATCH (s:VehicleSystem)
        RETURN s.system_id as id, s.name as name, s.description as description
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            system_uri = VTAD[f"system/{row['id']}"]
            
            g.add((system_uri, RDF.type, VTA.VehicleSystem))
            g.add((system_uri, RDFS.label, Literal(row['name'])))
            if row.get('description'):
                g.add((system_uri, DCTERMS.description, Literal(row['description'])))
    
    def _export_scenarios_to_rdf(self, g: Graph, limit: Optional[int] = None) -> None:
        """Export test scenarios to RDF."""
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        MATCH (t:TestScenario)-[:IS_TYPE]->(tt:TestType)
        RETURN t.scenario_id as id, t.test_name as name, t.test_type as type,
               t.description as description, t.complexity_score as complexity,
               t.risk_level as risk, t.estimated_duration_hours as duration,
               t.estimated_cost_gbp as cost, t.certification_required as certification
        {limit_clause}
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            scenario_uri = VTAD[f"scenario/{row['id']}"]
            
            g.add((scenario_uri, RDF.type, VTA.TestScenario))
            g.add((scenario_uri, RDFS.label, Literal(row['name'])))
            g.add((scenario_uri, VTA.testType, Literal(row['type'])))
            
            if row.get('description'):
                g.add((scenario_uri, DCTERMS.description, Literal(row['description'])))
            
            g.add((scenario_uri, VTA.complexityScore, Literal(row['complexity'], datatype=XSD.integer)))
            g.add((scenario_uri, VTA.riskLevel, Literal(row['risk'])))
            g.add((scenario_uri, VTA.estimatedDuration, Literal(row['duration'], datatype=XSD.float)))
            g.add((scenario_uri, VTA.estimatedCost, Literal(row['cost'], datatype=XSD.float)))
            g.add((scenario_uri, VTA.certificationRequired, Literal(row['certification'], datatype=XSD.boolean)))
            
            # Link to test type
            test_type_uri = VTAD[f"testtype/{row['type']}"]
            g.add((scenario_uri, VTA.isType, test_type_uri))
    
    def _export_standards_to_rdf(self, g: Graph) -> None:
        """Export regulatory standards to RDF."""
        query = """
        MATCH (r:RegulatoryStandard)
        RETURN r.standard_id as id, r.name as name, r.category as category
        LIMIT 50
        """
        results = self.connector.execute_query(query)
        
        for row in results:
            standard_uri = VTAD[f"standard/{row['id']}"]
            
            g.add((standard_uri, RDF.type, VTA.RegulatoryStandard))
            g.add((standard_uri, RDFS.label, Literal(row['name'])))
            if row.get('category'):
                g.add((standard_uri, VTA.category, Literal(row['category'])))
    
    def export_owl_ttl(self, output_path: str = "semantic/ontology.ttl") -> None:
        """
        Export OWL ontology to Turtle format.
        
        Args:
            output_path: Path to output OWL file
        """
        logger.info(f"Exporting OWL ontology to {output_path}...")
        
        g = Graph()
        g.bind("vta", VTA)
        g.bind("owl", OWL)
        g.bind("rdfs", RDFS)
        
        # Ontology header
        ontology_uri = VTA[""]
        g.add((ontology_uri, RDF.type, OWL.Ontology))
        g.add((ontology_uri, RDFS.label, Literal("Virtual Testing Assistant Ontology")))
        g.add((ontology_uri, DCTERMS.description, Literal(
            "Ontology for automotive testing scenarios, vehicles, and components"
        )))
        
        # Classes
        classes = [
            ("Vehicle", "A vehicle model"),
            ("Platform", "A vehicle platform (EV, HEV, ICE)"),
            ("Component", "A vehicle component"),
            ("VehicleSystem", "A vehicle system (Powertrain, ADAS, etc.)"),
            ("TestScenario", "A test scenario"),
            ("RegulatoryStandard", "A regulatory standard"),
            ("TestType", "A type of test (performance, safety, etc.)"),
            ("Facility", "A testing facility"),
        ]
        
        for class_name, description in classes:
            class_uri = VTA[class_name]
            g.add((class_uri, RDF.type, OWL.Class))
            g.add((class_uri, RDFS.label, Literal(class_name)))
            g.add((class_uri, RDFS.comment, Literal(description)))
        
        # Object Properties
        object_properties = [
            ("onPlatform", "Vehicle", "Platform", "Links vehicle to its platform"),
            ("hasComponent", "Vehicle", "Component", "Vehicle has a component"),
            ("belongsToSystem", "Component", "VehicleSystem", "Component belongs to a system"),
            ("requiresTest", "Vehicle", "TestScenario", "Vehicle requires this test"),
            ("testsComponent", "TestScenario", "Component", "Test scenario tests this component"),
            ("followsStandard", "TestScenario", "RegulatoryStandard", "Test follows regulatory standard"),
            ("isType", "TestScenario", "TestType", "Test scenario has this type"),
        ]
        
        for prop_name, domain, range_class, description in object_properties:
            prop_uri = VTA[prop_name]
            g.add((prop_uri, RDF.type, OWL.ObjectProperty))
            g.add((prop_uri, RDFS.label, Literal(prop_name)))
            g.add((prop_uri, RDFS.comment, Literal(description)))
            g.add((prop_uri, RDFS.domain, VTA[domain]))
            g.add((prop_uri, RDFS.range, VTA[range_class]))
        
        # Data Properties
        data_properties = [
            ("modelId", "Vehicle", XSD.string, "Model identifier"),
            ("testType", "TestScenario", XSD.string, "Type of test"),
            ("complexityScore", "TestScenario", XSD.integer, "Complexity score (1-10)"),
            ("riskLevel", "TestScenario", XSD.string, "Risk level"),
            ("estimatedDuration", "TestScenario", XSD.float, "Estimated duration in hours"),
            ("estimatedCost", "TestScenario", XSD.float, "Estimated cost in GBP"),
            ("certificationRequired", "TestScenario", XSD.boolean, "Certification required flag"),
            ("criticality", "Component", XSD.string, "Component criticality level"),
            ("category", "RegulatoryStandard", XSD.string, "Standard category"),
        ]
        
        for prop_name, domain, range_type, description in data_properties:
            prop_uri = VTA[prop_name]
            g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            g.add((prop_uri, RDFS.label, Literal(prop_name)))
            g.add((prop_uri, RDFS.comment, Literal(description)))
            g.add((prop_uri, RDFS.domain, VTA[domain]))
            g.add((prop_uri, RDFS.range, range_type))
        
        # Serialize to file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        g.serialize(destination=output_path, format="turtle")
        logger.info(f"OWL ontology exported: {len(g)} triples")
    
    def run_sparql(self, query: str) -> List[Dict[str, Any]]:
        """
        Run SPARQL query on the RDF graph.
        
        Args:
            query: SPARQL query string
            
        Returns:
            List of query results as dictionaries
        """
        if self.rdf_graph is None:
            logger.warning("RDF graph not built. Building now...")
            self.build_rdf_graph_from_kg(limit=100)
        
        results = []
        qres = self.rdf_graph.query(query)
        
        for row in qres:
            result = {}
            for var in qres.vars:
                value = row[var]
                if isinstance(value, Literal):
                    result[str(var)] = value.toPython()
                elif isinstance(value, URIRef):
                    result[str(var)] = str(value)
                else:
                    result[str(var)] = str(value) if value else None
            results.append(result)
        
        return results
    
    def validate_shacl(
        self,
        shapes_path: str = "semantic/shapes.ttl",
        data_graph: Optional[Graph] = None
    ) -> Dict[str, Any]:
        """
        Validate RDF graph against SHACL shapes.
        
        Args:
            shapes_path: Path to SHACL shapes file
            data_graph: Data graph to validate (uses self.rdf_graph if None)
            
        Returns:
            Dictionary with validation results
        """
        if data_graph is None:
            if self.rdf_graph is None:
                logger.warning("RDF graph not built. Building now...")
                self.build_rdf_graph_from_kg(limit=50)
            data_graph = self.rdf_graph
        
        logger.info(f"Validating RDF graph against SHACL shapes: {shapes_path}")
        
        # Load shapes
        shapes_graph = Graph()
        shapes_graph.parse(shapes_path, format="turtle")
        
        # Validate
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False,
        )
        
        return {
            "conforms": conforms,
            "violations_count": len(list(results_graph.subjects())) if not conforms else 0,
            "violations_text": results_text if not conforms else "No violations",
            "results_graph": results_graph
        }
    
    def export_jsonld(self, output_path: str = "semantic/data.jsonld") -> None:
        """
        Export RDF graph to JSON-LD format.
        
        Args:
            output_path: Path to output JSON-LD file
        """
        if self.rdf_graph is None:
            logger.warning("RDF graph not built. Building now...")
            self.build_rdf_graph_from_kg(limit=100)
        
        logger.info(f"Exporting JSON-LD to {output_path}...")
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.rdf_graph.serialize(destination=output_path, format="json-ld", indent=2)
        logger.info("JSON-LD exported")


def build_rdf_from_neo4j(limit: Optional[int] = None) -> Graph:
    """
    Convenience function to build RDF graph from Neo4j.
    
    Args:
        limit: Limit number of scenarios
        
    Returns:
        RDFLib Graph
    """
    bridge = SemanticBridge()
    return bridge.build_rdf_graph_from_kg(limit=limit)


def export_owl_ontology(output_path: str = "semantic/ontology.ttl") -> None:
    """
    Convenience function to export OWL ontology (doesn't require Neo4j).
    
    Args:
        output_path: Path to output file
    """
    # Create the ontology directly without needing Neo4j connection
    logger.info(f"Exporting OWL ontology to {output_path}...")
    
    g = Graph()
    g.bind("vta", VTA)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    
    # Ontology header
    ontology_uri = VTA[""]
    g.add((ontology_uri, RDF.type, OWL.Ontology))
    g.add((ontology_uri, RDFS.label, Literal("Virtual Testing Assistant Ontology")))
    g.add((ontology_uri, DCTERMS.description, Literal(
        "Ontology for automotive testing scenarios, vehicles, and components"
    )))
    
    # Classes
    classes = [
        ("Vehicle", "A vehicle model"),
        ("Platform", "A vehicle platform (EV, HEV, ICE)"),
        ("Component", "A vehicle component"),
        ("VehicleSystem", "A vehicle system (Powertrain, ADAS, etc.)"),
        ("TestScenario", "A test scenario"),
        ("RegulatoryStandard", "A regulatory standard"),
        ("TestType", "A type of test (performance, safety, etc.)"),
        ("Facility", "A testing facility"),
    ]
    
    for class_name, description in classes:
        class_uri = VTA[class_name]
        g.add((class_uri, RDF.type, OWL.Class))
        g.add((class_uri, RDFS.label, Literal(class_name)))
        g.add((class_uri, RDFS.comment, Literal(description)))
    
    # Object Properties
    object_properties = [
        ("onPlatform", "Vehicle", "Platform", "Links vehicle to its platform"),
        ("hasComponent", "Vehicle", "Component", "Vehicle has a component"),
        ("belongsToSystem", "Component", "VehicleSystem", "Component belongs to a system"),
        ("requiresTest", "Vehicle", "TestScenario", "Vehicle requires this test"),
        ("testsComponent", "TestScenario", "Component", "Test scenario tests this component"),
        ("followsStandard", "TestScenario", "RegulatoryStandard", "Test follows regulatory standard"),
        ("isType", "TestScenario", "TestType", "Test scenario has this type"),
    ]
    
    for prop_name, domain, range_class, description in object_properties:
        prop_uri = VTA[prop_name]
        g.add((prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((prop_uri, RDFS.label, Literal(prop_name)))
        g.add((prop_uri, RDFS.comment, Literal(description)))
        g.add((prop_uri, RDFS.domain, VTA[domain]))
        g.add((prop_uri, RDFS.range, VTA[range_class]))
    
    # Data Properties
    data_properties = [
        ("modelId", "Vehicle", XSD.string, "Model identifier"),
        ("testType", "TestScenario", XSD.string, "Type of test"),
        ("complexityScore", "TestScenario", XSD.integer, "Complexity score (1-10)"),
        ("riskLevel", "TestScenario", XSD.string, "Risk level"),
        ("estimatedDuration", "TestScenario", XSD.float, "Estimated duration in hours"),
        ("estimatedCost", "TestScenario", XSD.float, "Estimated cost in GBP"),
        ("certificationRequired", "TestScenario", XSD.boolean, "Certification required flag"),
        ("criticality", "Component", XSD.string, "Component criticality level"),
        ("category", "RegulatoryStandard", XSD.string, "Standard category"),
    ]
    
    for prop_name, domain, range_type, description in data_properties:
        prop_uri = VTA[prop_name]
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.label, Literal(prop_name)))
        g.add((prop_uri, RDFS.comment, Literal(description)))
        g.add((prop_uri, RDFS.domain, VTA[domain]))
        g.add((prop_uri, RDFS.range, range_type))
    
    # Serialize to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=output_path, format="turtle")
    logger.info(f"OWL ontology exported: {len(g)} triples")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SEMANTIC BRIDGE TEST")
    print("=" * 70)
    
    bridge = SemanticBridge()
    
    # Export OWL ontology
    print("\n[1/3] Exporting OWL ontology...")
    bridge.export_owl_ttl()
    print("[OK] OWL ontology exported to semantic/ontology.ttl")
    
    # Build RDF graph (sample)
    print("\n[2/3] Building sample RDF graph...")
    try:
        rdf_graph = bridge.build_rdf_graph_from_kg(
            include_vehicles=True,
            include_components=True,
            include_scenarios=True,
            limit=10
        )
        print(f"[OK] RDF graph built: {len(rdf_graph)} triples")
        
        # Run sample SPARQL query
        print("\n[3/3] Running sample SPARQL query...")
        query = """
        PREFIX vta: <http://nissan-ntce.cranfield.ac.uk/vta/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?vehicle ?label
        WHERE {
            ?vehicle a vta:Vehicle .
            ?vehicle rdfs:label ?label .
        }
        LIMIT 5
        """
        results = bridge.run_sparql(query)
        print(f"[OK] Found {len(results)} vehicles:")
        for r in results:
            print(f"  - {r.get('label')}")
    except Exception as e:
        print(f"[SKIP] Neo4j not available: {e}")
        print("       OWL ontology still exported successfully")
    
    print("\n[OK] Semantic bridge test complete")

