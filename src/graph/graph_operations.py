"""
Knowledge Graph operations for ingesting synthetic data and querying.
Handles schema creation, data ingestion, and baseline queries.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from src.graph.neo4j_connector import get_connector
from src.graph.ontology_design import (
    get_create_constraint_queries,
    get_create_index_queries,
    NodeLabel,
    RelationshipType,
)
from src.data.nissan_vehicle_models import NISSAN_MODELS, COMPONENTS

logger = logging.getLogger(__name__)


class GraphOperations:
    """Operations for managing the knowledge graph."""
    
    def __init__(self):
        """Initialize graph operations with connector."""
        self.connector = get_connector()
    
    def create_schema(self) -> None:
        """
        Create the knowledge graph schema (constraints and indexes).
        This should be called before ingesting data.
        """
        logger.info("Creating knowledge graph schema...")
        
        # Create constraints
        constraint_queries = get_create_constraint_queries()
        for query in constraint_queries:
            try:
                self.connector.execute_write(query)
                logger.debug(f"Created constraint: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Constraint creation warning: {e}")
        
        # Create indexes
        index_queries = get_create_index_queries()
        for query in index_queries:
            try:
                self.connector.execute_write(query)
                logger.debug(f"Created index: {query[:50]}...")
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        logger.info(f"Schema created: {len(constraint_queries)} constraints, {len(index_queries)} indexes")
    
    def ingest_synthetic_data(self, json_path: str = "src/data/test_scenarios.json") -> Dict[str, int]:
        """
        Ingest synthetic test scenarios from JSON into the knowledge graph.
        
        Args:
            json_path: Path to the synthetic data JSON file
            
        Returns:
            Dictionary with counts of created nodes and relationships
        """
        logger.info(f"Loading synthetic data from {json_path}...")
        
        # Load JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        scenarios = data["scenarios"]
        logger.info(f"Loaded {len(scenarios)} test scenarios")
        
        # Track what we create
        stats = {
            "vehicles": 0,
            "platforms": 0,
            "components": 0,
            "systems": 0,
            "test_scenarios": 0,
            "test_types": 0,
            "regulatory_standards": 0,
            "historical_tests": 0,
            "facilities": 0,
            "relationships": 0,
        }
        
        # Step 1: Create Platforms
        logger.info("Creating platforms...")
        platforms = set()
        for model, platform in NISSAN_MODELS.items():
            platforms.add(platform.value)
        
        for platform in platforms:
            query = """
            MERGE (p:Platform {platform_id: $platform_id})
            SET p.name = $name,
                p.description = $description
            """
            self.connector.execute_write(query, {
                "platform_id": platform,
                "name": platform,
                "description": f"{platform} vehicle platform"
            })
            stats["platforms"] += 1
        
        # Step 2: Create Vehicle Systems
        logger.info("Creating vehicle systems...")
        systems = set()
        for comp in COMPONENTS:
            systems.add(comp.system.value)
        
        for system in systems:
            query = """
            MERGE (s:VehicleSystem {system_id: $system_id})
            SET s.name = $name,
                s.description = $description
            """
            self.connector.execute_write(query, {
                "system_id": system,
                "name": system,
                "description": f"{system} vehicle system"
            })
            stats["systems"] += 1
        
        # Step 3: Create Components
        logger.info("Creating components...")
        for comp in COMPONENTS:
            query = """
            MERGE (c:Component {component_id: $component_id})
            SET c.name = $name,
                c.criticality = $criticality
            """
            self.connector.execute_write(query, {
                "component_id": comp.name,
                "name": comp.name,
                "criticality": comp.criticality
            })
            stats["components"] += 1
            
            # Create BELONGS_TO_SYSTEM relationship
            query = """
            MATCH (c:Component {component_id: $component_id})
            MATCH (s:VehicleSystem {system_id: $system_id})
            MERGE (c)-[r:BELONGS_TO_SYSTEM]->(s)
            """
            self.connector.execute_write(query, {
                "component_id": comp.name,
                "system_id": comp.system.value
            })
            stats["relationships"] += 1
        
        # Step 4: Create Vehicles
        logger.info("Creating vehicles...")
        for model, platform in NISSAN_MODELS.items():
            query = """
            MERGE (v:Vehicle {model_id: $model_id})
            SET v.name = $name,
                v.platform = $platform
            """
            self.connector.execute_write(query, {
                "model_id": model,
                "name": model,
                "platform": platform.value
            })
            stats["vehicles"] += 1
            
            # Create ON_PLATFORM relationship
            query = """
            MATCH (v:Vehicle {model_id: $model_id})
            MATCH (p:Platform {platform_id: $platform_id})
            MERGE (v)-[r:ON_PLATFORM]->(p)
            """
            self.connector.execute_write(query, {
                "model_id": model,
                "platform_id": platform.value
            })
            stats["relationships"] += 1
            
            # Create HAS_COMPONENT relationships for applicable components
            for comp in COMPONENTS:
                if platform in comp.applicable_platforms:
                    query = """
                    MATCH (v:Vehicle {model_id: $model_id})
                    MATCH (c:Component {component_id: $component_id})
                    MERGE (v)-[r:HAS_COMPONENT]->(c)
                    SET r.quantity = 1
                    """
                    self.connector.execute_write(query, {
                        "model_id": model,
                        "component_id": comp.name
                    })
                    stats["relationships"] += 1
        
        # Step 5: Create Test Types
        logger.info("Creating test types...")
        test_types = set(s["test_type"] for s in scenarios)
        for test_type in test_types:
            query = """
            MERGE (t:TestType {type_id: $type_id})
            SET t.name = $name,
                t.description = $description
            """
            self.connector.execute_write(query, {
                "type_id": test_type,
                "name": test_type.title(),
                "description": f"{test_type.title()} testing"
            })
            stats["test_types"] += 1
        
        # Step 6: Create Facilities
        logger.info("Creating facilities...")
        facility_types = set(s["facility_type"] for s in scenarios)
        for facility_type in facility_types:
            query = """
            MERGE (f:Facility {facility_id: $facility_id})
            SET f.name = $name,
                f.type = $type
            """
            self.connector.execute_write(query, {
                "facility_id": facility_type,
                "name": facility_type.replace("_", " ").title(),
                "type": facility_type
            })
            stats["facilities"] += 1
        
        # Step 7: Create Regulatory Standards
        logger.info("Creating regulatory standards...")
        all_standards = set()
        for scenario in scenarios:
            all_standards.update(scenario["regulatory_standards"])
        
        for standard in all_standards:
            query = """
            MERGE (r:RegulatoryStandard {standard_id: $standard_id})
            SET r.name = $name,
                r.category = $category
            """
            # Infer category from standard name
            category = "General"
            if "UNECE" in standard or "NCAP" in standard or "ISO_26262" in standard:
                category = "Safety"
            elif "WLTP" in standard or "EPA" in standard or "EURO" in standard:
                category = "Emissions"
            elif "ISO" in standard or "SAE" in standard:
                category = "Technical"
            
            self.connector.execute_write(query, {
                "standard_id": standard,
                "name": standard.replace("_", " "),
                "category": category
            })
            stats["regulatory_standards"] += 1
        
        # Step 8: Create Test Scenarios (in batches)
        logger.info(f"Creating {len(scenarios)} test scenarios...")
        batch_size = 50
        
        for i in range(0, len(scenarios), batch_size):
            batch = scenarios[i:i + batch_size]
            
            for scenario in batch:
                # Create test scenario node
                query = """
                MERGE (t:TestScenario {scenario_id: $scenario_id})
                SET t.test_name = $test_name,
                    t.test_type = $test_type,
                    t.description = $description,
                    t.complexity_score = $complexity_score,
                    t.risk_level = $risk_level,
                    t.estimated_duration_hours = $estimated_duration_hours,
                    t.estimated_cost_gbp = $estimated_cost_gbp,
                    t.required_personnel = $required_personnel,
                    t.facility_type = $facility_type,
                    t.certification_required = $certification_required,
                    t.created_date = $created_date,
                    t.version = $version,
                    t.execution_count = $execution_count,
                    t.env_temperature = $env_temperature,
                    t.env_humidity = $env_humidity,
                    t.env_road_surface = $env_road_surface,
                    t.env_weather = $env_weather,
                    t.load_percent = $load_percent,
                    t.speed_profile = $speed_profile,
                    t.duration_hours = $duration_hours,
                    t.distance_km = $distance_km
                """
                env = scenario["environmental_conditions"]
                load = scenario["load_profile"]
                
                self.connector.execute_write(query, {
                    "scenario_id": scenario["scenario_id"],
                    "test_name": scenario["test_name"],
                    "test_type": scenario["test_type"],
                    "description": scenario["description"],
                    "complexity_score": scenario["complexity_score"],
                    "risk_level": scenario["risk_level"],
                    "estimated_duration_hours": scenario["estimated_duration_hours"],
                    "estimated_cost_gbp": scenario["estimated_cost_gbp"],
                    "required_personnel": scenario["required_personnel"],
                    "facility_type": scenario["facility_type"],
                    "certification_required": scenario["certification_required"],
                    "created_date": scenario["created_date"],
                    "version": scenario["version"],
                    "execution_count": scenario["execution_count"],
                    "env_temperature": env["temperature_celsius"],
                    "env_humidity": env["humidity_percent"],
                    "env_road_surface": env["road_surface"],
                    "env_weather": env["weather"],
                    "load_percent": load["load_percent"],
                    "speed_profile": load["speed_profile"],
                    "duration_hours": load["duration_hours"],
                    "distance_km": load["distance_km"],
                })
                stats["test_scenarios"] += 1
                
                # Connect to test type
                query = """
                MATCH (t:TestScenario {scenario_id: $scenario_id})
                MATCH (tt:TestType {type_id: $type_id})
                MERGE (t)-[r:IS_TYPE]->(tt)
                """
                self.connector.execute_write(query, {
                    "scenario_id": scenario["scenario_id"],
                    "type_id": scenario["test_type"]
                })
                stats["relationships"] += 1
                
                # Connect to facility
                query = """
                MATCH (t:TestScenario {scenario_id: $scenario_id})
                MATCH (f:Facility {facility_id: $facility_id})
                MERGE (t)-[r:REQUIRES_FACILITY]->(f)
                """
                self.connector.execute_write(query, {
                    "scenario_id": scenario["scenario_id"],
                    "facility_id": scenario["facility_type"]
                })
                stats["relationships"] += 1
                
                # Connect to applicable vehicles
                for model in scenario["applicable_models"]:
                    query = """
                    MATCH (v:Vehicle {model_id: $model_id})
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (v)-[r:REQUIRES_TEST]->(t)
                    SET r.priority = $priority
                    """
                    self.connector.execute_write(query, {
                        "model_id": model,
                        "scenario_id": scenario["scenario_id"],
                        "priority": 1 if scenario["certification_required"] else 2
                    })
                    stats["relationships"] += 1
                
                # Connect to applicable platforms
                for platform in scenario["applicable_platforms"]:
                    query = """
                    MATCH (p:Platform {platform_id: $platform_id})
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (t)-[r:APPLICABLE_TO]->(p)
                    """
                    self.connector.execute_write(query, {
                        "platform_id": platform,
                        "scenario_id": scenario["scenario_id"]
                    })
                    stats["relationships"] += 1
                
                # Connect to target components
                for component in scenario["target_components"]:
                    query = """
                    MATCH (c:Component {component_id: $component_id})
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (t)-[r:TESTS_COMPONENT]->(c)
                    """
                    self.connector.execute_write(query, {
                        "component_id": component,
                        "scenario_id": scenario["scenario_id"]
                    })
                    stats["relationships"] += 1
                
                # Connect to target systems
                for system in scenario["target_systems"]:
                    query = """
                    MATCH (s:VehicleSystem {system_id: $system_id})
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (t)-[r:TESTS_SYSTEM]->(s)
                    """
                    self.connector.execute_write(query, {
                        "system_id": system,
                        "scenario_id": scenario["scenario_id"]
                    })
                    stats["relationships"] += 1
                
                # Connect to regulatory standards
                for standard in scenario["regulatory_standards"]:
                    query = """
                    MATCH (r:RegulatoryStandard {standard_id: $standard_id})
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (t)-[rel:FOLLOWS_STANDARD]->(r)
                    SET rel.compliance_level = $compliance_level
                    """
                    self.connector.execute_write(query, {
                        "standard_id": standard,
                        "scenario_id": scenario["scenario_id"],
                        "compliance_level": "mandatory" if scenario["certification_required"] else "recommended"
                    })
                    stats["relationships"] += 1
                
                # Create historical test results
                for hist_result in scenario["historical_results"]:
                    query = """
                    CREATE (h:HistoricalTest {
                        test_id: $test_id,
                        execution_date: $execution_date,
                        passed: $passed,
                        failure_mode: $failure_mode,
                        fix_hours: $fix_hours,
                        engineer_notes: $engineer_notes
                    })
                    WITH h
                    MATCH (t:TestScenario {scenario_id: $scenario_id})
                    MERGE (t)-[r:HAS_RESULT]->(h)
                    """
                    self.connector.execute_write(query, {
                        "test_id": hist_result["test_id"],
                        "execution_date": hist_result["execution_date"],
                        "passed": hist_result["passed"],
                        "failure_mode": hist_result.get("failure_mode"),
                        "fix_hours": hist_result["fix_hours"],
                        "engineer_notes": hist_result["engineer_notes"],
                        "scenario_id": scenario["scenario_id"]
                    })
                    stats["historical_tests"] += 1
                    stats["relationships"] += 1
            
            if (i + batch_size) % 100 == 0:
                logger.info(f"  Processed {min(i + batch_size, len(scenarios))}/{len(scenarios)} scenarios...")
        
        logger.info("Synthetic data ingestion complete!")
        return stats
    
    def get_required_tests(self, vehicle_id: str) -> List[Dict[str, Any]]:
        """
        Get all required tests for a specific vehicle.
        
        Args:
            vehicle_id: Vehicle model ID
            
        Returns:
            List of test scenarios with details
        """
        query = """
        MATCH (v:Vehicle {model_id: $vehicle_id})-[r:REQUIRES_TEST]->(t:TestScenario)
        RETURN t.scenario_id as scenario_id,
               t.test_name as test_name,
               t.test_type as test_type,
               t.risk_level as risk_level,
               t.estimated_duration_hours as duration,
               t.estimated_cost_gbp as cost,
               r.priority as priority
        ORDER BY r.priority, t.risk_level DESC
        """
        return self.connector.execute_query(query, {"vehicle_id": vehicle_id})
    
    def get_odd_coverage(self, vehicle_id: str) -> Dict[str, Any]:
        """
        Get ODD (Operational Design Domain) coverage for a vehicle.
        
        Args:
            vehicle_id: Vehicle model ID
            
        Returns:
            Dictionary with ODD coverage statistics
        """
        query = """
        MATCH (v:Vehicle {model_id: $vehicle_id})-[:REQUIRES_TEST]->(t:TestScenario)
        WITH v, count(DISTINCT t) as total_tests,
             collect(DISTINCT t.env_weather) as weathers,
             collect(DISTINCT t.env_road_surface) as road_surfaces,
             collect(DISTINCT t.speed_profile) as speed_profiles
        RETURN v.model_id as vehicle,
               total_tests,
               weathers,
               road_surfaces,
               speed_profiles
        """
        results = self.connector.execute_query(query, {"vehicle_id": vehicle_id})
        return results[0] if results else {}
    
    def get_scenario_similarity_edges(self, seed_ids: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get scenarios similar to the seed scenarios based on graph structure.
        This is a baseline; will be enhanced with vector similarity in Phase 4.
        
        Args:
            seed_ids: List of scenario IDs
            limit: Maximum number of similar scenarios to return
            
        Returns:
            List of similar scenarios with similarity scores
        """
        query = """
        MATCH (seed:TestScenario)
        WHERE seed.scenario_id IN $seed_ids
        MATCH (seed)-[:TESTS_COMPONENT]->(c:Component)<-[:TESTS_COMPONENT]-(similar:TestScenario)
        WHERE NOT similar.scenario_id IN $seed_ids
        WITH similar, count(DISTINCT c) as shared_components
        RETURN similar.scenario_id as scenario_id,
               similar.test_name as test_name,
               similar.test_type as test_type,
               shared_components as similarity_score
        ORDER BY shared_components DESC
        LIMIT $limit
        """
        return self.connector.execute_query(query, {"seed_ids": seed_ids, "limit": limit})
    
    def get_tests_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """
        Get all tests applicable to a specific platform.
        
        Args:
            platform: Platform ID (EV, HEV, ICE)
            
        Returns:
            List of test scenarios
        """
        query = """
        MATCH (t:TestScenario)-[:APPLICABLE_TO]->(p:Platform {platform_id: $platform})
        RETURN t.scenario_id as scenario_id,
               t.test_name as test_name,
               t.test_type as test_type,
               t.complexity_score as complexity,
               t.estimated_duration_hours as duration,
               t.estimated_cost_gbp as cost
        ORDER BY t.complexity_score DESC
        """
        return self.connector.execute_query(query, {"platform": platform})
    
    def get_component_test_coverage(self, component_id: str) -> Dict[str, Any]:
        """
        Get test coverage statistics for a specific component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Dictionary with coverage statistics
        """
        query = """
        MATCH (c:Component {component_id: $component_id})<-[:TESTS_COMPONENT]-(t:TestScenario)
        WITH c, count(t) as test_count,
             collect(DISTINCT t.test_type) as test_types,
             sum(t.estimated_duration_hours) as total_hours,
             sum(t.estimated_cost_gbp) as total_cost
        RETURN c.name as component,
               c.criticality as criticality,
               test_count,
               test_types,
               total_hours,
               total_cost
        """
        results = self.connector.execute_query(query, {"component_id": component_id})
        return results[0] if results else {}


# Convenience functions
def create_schema():
    """Create the knowledge graph schema."""
    ops = GraphOperations()
    ops.create_schema()


def ingest_synthetic():
    """Ingest synthetic test scenarios."""
    ops = GraphOperations()
    return ops.ingest_synthetic_data()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("KNOWLEDGE GRAPH OPERATIONS TEST")
    print("=" * 70)
    
    ops = GraphOperations()
    
    # Create schema
    print("\n[1/2] Creating schema...")
    ops.create_schema()
    print("[OK] Schema created")
    
    # Ingest data
    print("\n[2/2] Ingesting synthetic data...")
    stats = ops.ingest_synthetic_data()
    
    print("\n" + "=" * 70)
    print("INGESTION STATISTICS")
    print("=" * 70)
    for key, value in stats.items():
        print(f"  {key:25s}: {value:6,d}")
    
    print("\n[OK] Knowledge graph operations complete")

