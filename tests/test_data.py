"""
Tests for Phase 1: Data generation and configuration.
"""
import json
import pytest
from pathlib import Path

from src.config.settings import Settings
from src.data.nissan_vehicle_models import (
    NISSAN_MODELS, COMPONENTS, Platform, VehicleSystem,
    get_components_for_platform, get_platform_for_model
)
from src.data.synthetic_data_generator import SyntheticDataGenerator


class TestSettings:
    """Test configuration management."""
    
    def test_settings_loads(self):
        """Test that settings can be loaded."""
        settings = Settings()
        assert settings is not None
        assert settings.app_name == "Virtual Testing Assistant"
    
    def test_neo4j_config(self):
        """Test Neo4j configuration."""
        settings = Settings()
        assert settings.neo4j_uri.startswith("bolt://")
        assert settings.neo4j_user is not None
        assert settings.neo4j_password is not None
    
    def test_pg_config(self):
        """Test PostgreSQL configuration."""
        settings = Settings()
        assert "postgresql" in settings.pg_conn
        assert settings.get_pg_database() == "vta"
    
    def test_business_config(self):
        """Test business configuration."""
        settings = Settings()
        assert settings.engineering_hourly_rate > 0
        assert settings.campaigns_per_year > 0
    
    def test_hf_config(self):
        """Test HuggingFace LLM configuration."""
        settings = Settings()
        assert settings.hf_llm_model_id is not None
        assert settings.hf_device in ["auto", "cpu", "cuda"]
        assert 0 <= settings.hf_temperature <= 2.0
        assert settings.hf_max_new_tokens > 0


class TestVehicleModels:
    """Test vehicle model definitions."""
    
    def test_models_defined(self):
        """Test that vehicle models are defined."""
        assert len(NISSAN_MODELS) >= 6
        assert "Ariya" in NISSAN_MODELS
        assert "Leaf" in NISSAN_MODELS
    
    def test_platforms_assigned(self):
        """Test that each model has a platform."""
        for model, platform in NISSAN_MODELS.items():
            assert platform in [Platform.EV, Platform.HEV, Platform.ICE]
    
    def test_ev_models(self):
        """Test EV models are correctly classified."""
        assert NISSAN_MODELS["Ariya"] == Platform.EV
        assert NISSAN_MODELS["Leaf"] == Platform.EV
    
    def test_components_defined(self):
        """Test that components are defined."""
        assert len(COMPONENTS) >= 50
    
    def test_components_have_systems(self):
        """Test that all components have valid systems."""
        for component in COMPONENTS:
            assert component.system in VehicleSystem
            assert len(component.applicable_platforms) > 0
            assert component.criticality in ["critical", "high", "medium", "low"]
    
    def test_get_components_for_platform(self):
        """Test getting components for a platform."""
        ev_components = get_components_for_platform(Platform.EV)
        assert len(ev_components) > 0
        
        ice_components = get_components_for_platform(Platform.ICE)
        assert len(ice_components) > 0
        
        # EV should have battery components
        ev_component_names = [c.name for c in ev_components]
        assert "High_Voltage_Battery" in ev_component_names
    
    def test_platform_lookup(self):
        """Test platform lookup by model."""
        assert get_platform_for_model("Ariya") == Platform.EV
        assert get_platform_for_model("Qashqai") == Platform.ICE


class TestSyntheticDataGenerator:
    """Test synthetic data generation."""
    
    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return SyntheticDataGenerator(seed=42)
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly."""
        assert generator.seed == 42
        assert len(generator.test_templates) == 6
    
    def test_generate_small_set(self, generator):
        """Test generating a small set of scenarios."""
        scenarios = generator.generate_scenarios(target_count=50)
        assert len(scenarios) >= 45  # Allow some variance
        assert len(scenarios) <= 55
    
    def test_scenario_structure(self, generator):
        """Test that generated scenarios have required fields."""
        scenarios = generator.generate_scenarios(target_count=10)
        
        for scenario in scenarios:
            # Core fields
            assert scenario.scenario_id is not None
            assert scenario.test_name is not None
            assert scenario.test_type in ["performance", "durability", "safety", "regulatory", "adas", "emissions"]
            
            # Vehicle context
            assert len(scenario.applicable_models) > 0
            assert len(scenario.applicable_platforms) > 0
            assert len(scenario.target_components) > 0
            assert len(scenario.target_systems) > 0
            
            # Resource estimates
            assert scenario.estimated_duration_hours > 0
            assert scenario.estimated_cost_gbp > 0
            assert scenario.required_personnel > 0
            
            # Risk & complexity
            assert 1 <= scenario.complexity_score <= 10
            assert scenario.risk_level in ["low", "medium", "high", "critical"]
    
    def test_environmental_conditions(self, generator):
        """Test environmental conditions are realistic."""
        scenarios = generator.generate_scenarios(target_count=20)
        
        for scenario in scenarios:
            env = scenario.environmental_conditions
            assert -50 <= env.temperature_celsius <= 60
            assert 0 <= env.humidity_percent <= 100
            assert env.altitude_meters >= 0
            assert env.road_surface in ["dry", "wet", "snow", "ice", "gravel"]
            assert env.weather in ["clear", "rain", "snow", "fog"]
    
    def test_load_profile(self, generator):
        """Test load profiles are realistic."""
        scenarios = generator.generate_scenarios(target_count=20)
        
        for scenario in scenarios:
            load = scenario.load_profile
            assert 0 <= load.load_percent <= 100
            assert load.speed_profile in ["urban", "highway", "mixed", "sport", "eco", "regulatory"]
            assert load.duration_hours > 0
            assert load.distance_km > 0
    
    def test_test_type_distribution(self, generator):
        """Test that all test types are represented."""
        scenarios = generator.generate_scenarios(target_count=100)
        
        test_types = set(s.test_type for s in scenarios)
        assert "performance" in test_types
        assert "durability" in test_types
        assert "safety" in test_types
        assert "regulatory" in test_types
        assert "adas" in test_types
    
    def test_platform_coverage(self, generator):
        """Test that all platforms are covered."""
        scenarios = generator.generate_scenarios(target_count=100)
        
        all_platforms = set()
        for scenario in scenarios:
            all_platforms.update(scenario.applicable_platforms)
        
        assert "EV" in all_platforms
        assert "HEV" in all_platforms or "ICE" in all_platforms


class TestGeneratedJSON:
    """Test the generated JSON file."""
    
    @pytest.fixture(scope="class")
    def json_data(self):
        """Load the generated JSON file."""
        json_path = Path("src/data/test_scenarios.json")
        
        # Generate if doesn't exist
        if not json_path.exists():
            generator = SyntheticDataGenerator(seed=42)
            scenarios = generator.generate_scenarios(target_count=500)
            generator.save_to_json(scenarios, str(json_path))
        
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def test_json_exists(self):
        """Test that JSON file exists or can be created."""
        json_path = Path("src/data/test_scenarios.json")
        
        if not json_path.exists():
            generator = SyntheticDataGenerator(seed=42)
            scenarios = generator.generate_scenarios(target_count=500)
            generator.save_to_json(scenarios, str(json_path))
        
        assert json_path.exists()
    
    def test_json_structure(self, json_data):
        """Test JSON has correct structure."""
        assert "metadata" in json_data
        assert "scenarios" in json_data
        assert "scenario_count" in json_data["metadata"]
    
    def test_scenario_count(self, json_data):
        """Test that sufficient scenarios are generated."""
        count = len(json_data["scenarios"])
        assert count >= 300, f"Expected at least 300 scenarios, got {count}"
        assert count <= 600, f"Expected at most 600 scenarios, got {count}"
    
    def test_all_scenarios_have_required_fields(self, json_data):
        """Test that all scenarios have required fields."""
        required_fields = [
            "scenario_id", "test_name", "test_type", "description",
            "applicable_models", "applicable_platforms", "target_components",
            "estimated_duration_hours", "estimated_cost_gbp"
        ]
        
        for i, scenario in enumerate(json_data["scenarios"][:10]):  # Check first 10
            for field in required_fields:
                assert field in scenario, f"Scenario {i} missing field: {field}"
    
    def test_numeric_ranges(self, json_data):
        """Test that numeric values are in valid ranges."""
        for scenario in json_data["scenarios"]:
            assert scenario["estimated_duration_hours"] > 0
            assert scenario["estimated_cost_gbp"] > 0
            assert scenario["required_personnel"] > 0
            assert 1 <= scenario["complexity_score"] <= 10
            
            env = scenario["environmental_conditions"]
            assert -50 <= env["temperature_celsius"] <= 60
            assert 0 <= env["humidity_percent"] <= 100
    
    def test_platform_representation(self, json_data):
        """Test that multiple platforms are represented."""
        platforms = set()
        for scenario in json_data["scenarios"]:
            platforms.update(scenario["applicable_platforms"])
        
        assert len(platforms) >= 2, f"Expected multiple platforms, got {platforms}"
    
    def test_system_representation(self, json_data):
        """Test that multiple systems are represented."""
        systems = set()
        for scenario in json_data["scenarios"]:
            systems.update(scenario["target_systems"])
        
        assert len(systems) >= 5, f"Expected multiple systems, got {systems}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

