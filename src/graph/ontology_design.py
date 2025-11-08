"""
Automotive Testing Ontology Design for Neo4j Knowledge Graph.

Defines the schema for nodes (labels) and relationships that represent
the domain of automotive testing, vehicles, components, and test scenarios.
"""
from enum import Enum
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class NodeLabel(str, Enum):
    """Node labels in the knowledge graph."""
    VEHICLE = "Vehicle"
    PLATFORM = "Platform"
    COMPONENT = "Component"
    VEHICLE_SYSTEM = "VehicleSystem"
    TEST_SCENARIO = "TestScenario"
    REGULATORY_STANDARD = "RegulatoryStandard"
    HISTORICAL_TEST = "HistoricalTest"
    TEAM = "Team"
    ODD = "ODD"  # Operational Design Domain
    TEST_TYPE = "TestType"
    FACILITY = "Facility"


class RelationshipType(str, Enum):
    """Relationship types in the knowledge graph."""
    HAS_COMPONENT = "HAS_COMPONENT"
    ON_PLATFORM = "ON_PLATFORM"
    BELONGS_TO_SYSTEM = "BELONGS_TO_SYSTEM"
    REQUIRES_TEST = "REQUIRES_TEST"
    TESTS_COMPONENT = "TESTS_COMPONENT"
    TESTS_SYSTEM = "TESTS_SYSTEM"
    SIMILAR_TO = "SIMILAR_TO"
    HAS_RESULT = "HAS_RESULT"
    FOLLOWS_STANDARD = "FOLLOWS_STANDARD"
    PERFORMED_BY = "PERFORMED_BY"
    IN_ODD = "IN_ODD"
    IS_TYPE = "IS_TYPE"
    REQUIRES_FACILITY = "REQUIRES_FACILITY"
    APPLICABLE_TO = "APPLICABLE_TO"


# Schema definitions for each node type
NODE_SCHEMAS: Dict[str, Dict] = {
    NodeLabel.VEHICLE: {
        "properties": {
            "model_id": "STRING",  # Unique identifier
            "name": "STRING",      # e.g., "Ariya", "Leaf"
            "platform": "STRING",  # "EV", "HEV", "ICE"
            "year": "INTEGER",
            "variant": "STRING",
        },
        "indexes": ["model_id", "name"],
        "constraints": ["model_id"],  # Unique constraint
    },
    
    NodeLabel.PLATFORM: {
        "properties": {
            "platform_id": "STRING",  # "EV", "HEV", "ICE"
            "name": "STRING",
            "description": "STRING",
        },
        "indexes": ["platform_id"],
        "constraints": ["platform_id"],
    },
    
    NodeLabel.COMPONENT: {
        "properties": {
            "component_id": "STRING",
            "name": "STRING",  # e.g., "Electric_Motor", "High_Voltage_Battery"
            "criticality": "STRING",  # "critical", "high", "medium", "low"
            "supplier": "STRING",
            "part_number": "STRING",
        },
        "indexes": ["component_id", "name"],
        "constraints": ["component_id"],
    },
    
    NodeLabel.VEHICLE_SYSTEM: {
        "properties": {
            "system_id": "STRING",
            "name": "STRING",  # e.g., "Powertrain", "ADAS", "Battery"
            "description": "STRING",
        },
        "indexes": ["system_id", "name"],
        "constraints": ["system_id"],
    },
    
    NodeLabel.TEST_SCENARIO: {
        "properties": {
            "scenario_id": "STRING",
            "test_name": "STRING",
            "test_type": "STRING",
            "description": "STRING",
            "complexity_score": "INTEGER",
            "risk_level": "STRING",
            "estimated_duration_hours": "FLOAT",
            "estimated_cost_gbp": "FLOAT",
            "required_personnel": "INTEGER",
            "facility_type": "STRING",
            "certification_required": "BOOLEAN",
            "created_date": "STRING",
            "version": "STRING",
            # Environmental conditions (flattened)
            "env_temperature": "FLOAT",
            "env_humidity": "FLOAT",
            "env_road_surface": "STRING",
            "env_weather": "STRING",
            # Load profile (flattened)
            "load_percent": "FLOAT",
            "speed_profile": "STRING",
            "duration_hours": "FLOAT",
            "distance_km": "FLOAT",
            # Metrics
            "execution_count": "INTEGER",
        },
        "indexes": ["scenario_id", "test_name", "test_type"],
        "constraints": ["scenario_id"],
    },
    
    NodeLabel.REGULATORY_STANDARD: {
        "properties": {
            "standard_id": "STRING",  # e.g., "UNECE_R100", "ISO_26262"
            "name": "STRING",
            "category": "STRING",  # "Safety", "Emissions", "Performance"
            "issuing_body": "STRING",  # "UNECE", "ISO", "SAE"
            "version": "STRING",
            "effective_date": "STRING",
            "description": "STRING",
        },
        "indexes": ["standard_id", "name"],
        "constraints": ["standard_id"],
    },
    
    NodeLabel.HISTORICAL_TEST: {
        "properties": {
            "test_id": "STRING",
            "execution_date": "STRING",
            "passed": "BOOLEAN",
            "failure_mode": "STRING",
            "fix_hours": "FLOAT",
            "engineer_notes": "STRING",
        },
        "indexes": ["test_id", "execution_date"],
        "constraints": ["test_id"],
    },
    
    NodeLabel.TEAM: {
        "properties": {
            "team_id": "STRING",
            "name": "STRING",
            "specialization": "STRING",
            "location": "STRING",
        },
        "indexes": ["team_id"],
        "constraints": ["team_id"],
    },
    
    NodeLabel.ODD: {
        "properties": {
            "odd_id": "STRING",
            "name": "STRING",
            "description": "STRING",
            "speed_range": "STRING",
            "road_types": "STRING",
            "weather_conditions": "STRING",
        },
        "indexes": ["odd_id"],
        "constraints": ["odd_id"],
    },
    
    NodeLabel.TEST_TYPE: {
        "properties": {
            "type_id": "STRING",  # "performance", "durability", etc.
            "name": "STRING",
            "description": "STRING",
        },
        "indexes": ["type_id"],
        "constraints": ["type_id"],
    },
    
    NodeLabel.FACILITY: {
        "properties": {
            "facility_id": "STRING",
            "name": "STRING",
            "type": "STRING",  # "lab", "test_track", "climatic_chamber"
            "location": "STRING",
            "capabilities": "STRING",
        },
        "indexes": ["facility_id"],
        "constraints": ["facility_id"],
    },
}


# Relationship schemas with properties
RELATIONSHIP_SCHEMAS: Dict[str, Dict] = {
    RelationshipType.HAS_COMPONENT: {
        "from": NodeLabel.VEHICLE,
        "to": NodeLabel.COMPONENT,
        "properties": {
            "quantity": "INTEGER",
            "location": "STRING",
        },
    },
    
    RelationshipType.ON_PLATFORM: {
        "from": NodeLabel.VEHICLE,
        "to": NodeLabel.PLATFORM,
        "properties": {},
    },
    
    RelationshipType.BELONGS_TO_SYSTEM: {
        "from": NodeLabel.COMPONENT,
        "to": NodeLabel.VEHICLE_SYSTEM,
        "properties": {},
    },
    
    RelationshipType.REQUIRES_TEST: {
        "from": NodeLabel.VEHICLE,
        "to": NodeLabel.TEST_SCENARIO,
        "properties": {
            "priority": "INTEGER",
            "mandatory": "BOOLEAN",
        },
    },
    
    RelationshipType.TESTS_COMPONENT: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.COMPONENT,
        "properties": {},
    },
    
    RelationshipType.TESTS_SYSTEM: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.VEHICLE_SYSTEM,
        "properties": {},
    },
    
    RelationshipType.SIMILAR_TO: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.TEST_SCENARIO,
        "properties": {
            "similarity_score": "FLOAT",
            "method": "STRING",  # "embedding", "jaccard", "graph"
        },
    },
    
    RelationshipType.HAS_RESULT: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.HISTORICAL_TEST,
        "properties": {},
    },
    
    RelationshipType.FOLLOWS_STANDARD: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.REGULATORY_STANDARD,
        "properties": {
            "compliance_level": "STRING",  # "mandatory", "recommended"
        },
    },
    
    RelationshipType.PERFORMED_BY: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.TEAM,
        "properties": {
            "execution_date": "STRING",
        },
    },
    
    RelationshipType.IN_ODD: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.ODD,
        "properties": {},
    },
    
    RelationshipType.IS_TYPE: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.TEST_TYPE,
        "properties": {},
    },
    
    RelationshipType.REQUIRES_FACILITY: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.FACILITY,
        "properties": {},
    },
    
    RelationshipType.APPLICABLE_TO: {
        "from": NodeLabel.TEST_SCENARIO,
        "to": NodeLabel.PLATFORM,
        "properties": {},
    },
}


def get_create_constraint_queries() -> List[str]:
    """
    Generate Cypher queries to create uniqueness constraints.
    
    Returns:
        List of Cypher CREATE CONSTRAINT queries
    """
    queries = []
    
    for label, schema in NODE_SCHEMAS.items():
        constraints = schema.get("constraints", [])
        for prop in constraints:
            # Neo4j 5.x syntax for unique constraints
            query = f"""
            CREATE CONSTRAINT {label.lower()}_{prop}_unique IF NOT EXISTS
            FOR (n:{label})
            REQUIRE n.{prop} IS UNIQUE
            """
            queries.append(query.strip())
    
    return queries


def get_create_index_queries() -> List[str]:
    """
    Generate Cypher queries to create indexes for faster lookups.
    
    Returns:
        List of Cypher CREATE INDEX queries
    """
    queries = []
    
    for label, schema in NODE_SCHEMAS.items():
        indexes = schema.get("indexes", [])
        for prop in indexes:
            # Neo4j 5.x syntax for indexes
            query = f"""
            CREATE INDEX {label.lower()}_{prop}_idx IF NOT EXISTS
            FOR (n:{label})
            ON (n.{prop})
            """
            queries.append(query.strip())
    
    return queries


def get_schema_summary() -> Dict[str, int]:
    """
    Get a summary of the ontology schema.
    
    Returns:
        Dictionary with counts of node types and relationship types
    """
    return {
        "node_labels": len(NODE_SCHEMAS),
        "relationship_types": len(RELATIONSHIP_SCHEMAS),
        "total_constraints": sum(
            len(schema.get("constraints", []))
            for schema in NODE_SCHEMAS.values()
        ),
        "total_indexes": sum(
            len(schema.get("indexes", []))
            for schema in NODE_SCHEMAS.values()
        ),
    }


def print_schema_documentation():
    """Print human-readable documentation of the ontology."""
    print("\n" + "=" * 70)
    print("AUTOMOTIVE TESTING ONTOLOGY SCHEMA")
    print("=" * 70)
    
    summary = get_schema_summary()
    print(f"\nSummary:")
    print(f"  Node Labels: {summary['node_labels']}")
    print(f"  Relationship Types: {summary['relationship_types']}")
    print(f"  Constraints: {summary['total_constraints']}")
    print(f"  Indexes: {summary['total_indexes']}")
    
    print(f"\n{'NODE LABELS':-^70}")
    for label, schema in NODE_SCHEMAS.items():
        print(f"\n{label}:")
        props = schema.get("properties", {})
        print(f"  Properties: {', '.join(props.keys())}")
        if schema.get("constraints"):
            print(f"  Constraints: {', '.join(schema['constraints'])}")
    
    print(f"\n{'RELATIONSHIP TYPES':-^70}")
    for rel_type, schema in RELATIONSHIP_SCHEMAS.items():
        from_node = schema["from"]
        to_node = schema["to"]
        print(f"\n{rel_type}:")
        print(f"  ({from_node})-[:{rel_type}]->({to_node})")
        if schema.get("properties"):
            print(f"  Properties: {', '.join(schema['properties'].keys())}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Print schema documentation
    print_schema_documentation()
    
    # Show constraint queries
    print("\n" + "=" * 70)
    print("CONSTRAINT QUERIES")
    print("=" * 70)
    for query in get_create_constraint_queries()[:3]:
        print(f"\n{query}")
    print("\n... (and more)")
    
    # Show index queries
    print("\n" + "=" * 70)
    print("INDEX QUERIES")
    print("=" * 70)
    for query in get_create_index_queries()[:3]:
        print(f"\n{query}")
    print("\n... (and more)")
    
    print("\n[OK] Ontology design complete")

