"""
Tests for Phase 6: Simulation Export (CARLA/SUMO).
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any

from src.sim.base import (
    SimulationScenario,
    SimulationPlatform,
    VehicleConfiguration,
    EnvironmentalConditions,
    TrafficScenario,
    Route,
    TestManeuver,
    WeatherCondition,
    RoadType,
    TrafficDensity
)
from src.sim.scenario_converter import ScenarioConverter, create_scenario_converter
from src.sim.carla_exporter import CARLAExporter, create_carla_exporter
from src.sim.sumo_exporter import SUMOExporter, create_sumo_exporter


class TestSimulationBase:
    """Test base simulation data structures."""
    
    def test_vehicle_configuration(self):
        """Test vehicle configuration creation."""
        vehicle = VehicleConfiguration(
            model="Ariya",
            platform="EV",
            mass_kg=1800.0,
            max_speed_kmh=180.0,
            battery_capacity_kwh=87.0
        )
        
        assert vehicle.model == "Ariya"
        assert vehicle.platform == "EV"
        assert vehicle.mass_kg == 1800.0
        assert vehicle.battery_capacity_kwh == 87.0
    
    def test_environmental_conditions(self):
        """Test environmental conditions creation."""
        env = EnvironmentalConditions(
            weather=WeatherCondition.RAIN,
            road_surface=RoadType.WET_ASPHALT,
            temperature_celsius=15.0
        )
        
        assert env.weather == WeatherCondition.RAIN
        assert env.road_surface == RoadType.WET_ASPHALT
        assert env.temperature_celsius == 15.0
    
    def test_traffic_scenario(self):
        """Test traffic scenario creation."""
        traffic = TrafficScenario(
            density=TrafficDensity.HIGH,
            num_vehicles=30,
            num_pedestrians=10
        )
        
        assert traffic.density == TrafficDensity.HIGH
        assert traffic.num_vehicles == 30
        assert traffic.num_pedestrians == 10
    
    def test_route_creation(self):
        """Test route creation."""
        route = Route(
            waypoints=[(0, 0, 0.5), (100, 0, 0.5), (200, 50, 0.5)],
            speed_limits_kmh=[50.0, 80.0, 50.0],
            total_distance_m=250.0,
            route_type="urban"
        )
        
        assert len(route.waypoints) == 3
        assert len(route.speed_limits_kmh) == 3
        assert route.total_distance_m == 250.0
        assert route.route_type == "urban"
    
    def test_test_maneuver(self):
        """Test maneuver creation."""
        maneuver = TestManeuver(
            maneuver_type="lane_change",
            trigger_time_s=10.0,
            duration_s=5.0,
            parameters={'direction': 'left'}
        )
        
        assert maneuver.maneuver_type == "lane_change"
        assert maneuver.trigger_time_s == 10.0
        assert maneuver.duration_s == 5.0
        assert maneuver.parameters['direction'] == 'left'
    
    def test_simulation_scenario(self):
        """Test complete simulation scenario creation."""
        vehicle = VehicleConfiguration(model="Ariya", platform="EV")
        env = EnvironmentalConditions()
        traffic = TrafficScenario()
        route = Route()
        
        scenario = SimulationScenario(
            scenario_id="TEST-001",
            name="Test Scenario",
            description="Test description",
            platform=SimulationPlatform.CARLA,
            ego_vehicle=vehicle,
            environment=env,
            traffic=traffic,
            route=route,
            duration_seconds=300.0
        )
        
        assert scenario.scenario_id == "TEST-001"
        assert scenario.name == "Test Scenario"
        assert scenario.platform == SimulationPlatform.CARLA
        assert scenario.duration_seconds == 300.0
    
    def test_scenario_to_dict(self):
        """Test scenario serialization to dictionary."""
        vehicle = VehicleConfiguration(model="Ariya", platform="EV")
        env = EnvironmentalConditions()
        traffic = TrafficScenario()
        route = Route()
        
        scenario = SimulationScenario(
            scenario_id="TEST-001",
            name="Test",
            description="Desc",
            platform=SimulationPlatform.CARLA,
            ego_vehicle=vehicle,
            environment=env,
            traffic=traffic,
            route=route
        )
        
        scenario_dict = scenario.to_dict()
        
        assert isinstance(scenario_dict, dict)
        assert scenario_dict['scenario_id'] == "TEST-001"
        assert scenario_dict['platform'] == "CARLA"
        assert 'ego_vehicle' in scenario_dict
        assert 'environment' in scenario_dict


class TestScenarioConverter:
    """Test scenario converter."""
    
    @pytest.fixture
    def converter(self):
        """Create converter instance."""
        return create_scenario_converter()
    
    @pytest.fixture
    def sample_vta_scenario(self):
        """Create sample VTA scenario."""
        return {
            'scenario_id': 'VTA-TEST-001',
            'test_name': 'Battery Thermal Test',
            'description': 'EV battery thermal performance',
            'test_type': 'performance',
            'applicable_platforms': ['EV'],
            'target_components': ['High_Voltage_Battery', 'Battery_Management_System'],
            'target_systems': ['Battery', 'Thermal'],
            'environmental_conditions': {
                'ambient_temperature_celsius': 35.0,
                'humidity_percent': 60.0,
                'road_surface_condition': 'dry'
            },
            'complexity_score': 7,
            'risk_level': 'high',
            'estimated_duration_hours': 2.0,
            'estimated_cost_gbp': 8000.0,
            'regulatory_standards': ['UNECE_R100', 'ISO_6469'],
            'certification_required': True
        }
    
    def test_converter_initialization(self, converter):
        """Test converter initializes correctly."""
        assert converter is not None
    
    def test_convert_from_vta(self, converter, sample_vta_scenario):
        """Test converting VTA scenario to simulation scenario."""
        sim_scenario = converter.convert_from_vta(
            sample_vta_scenario,
            platform=SimulationPlatform.CARLA
        )
        
        assert sim_scenario.scenario_id == 'VTA-TEST-001'
        assert sim_scenario.name == 'Battery Thermal Test'
        assert sim_scenario.platform == SimulationPlatform.CARLA
        assert sim_scenario.ego_vehicle.platform == 'EV'
        assert sim_scenario.duration_seconds == 7200.0  # 2 hours
    
    def test_extract_vehicle_config(self, converter, sample_vta_scenario):
        """Test vehicle configuration extraction."""
        sim_scenario = converter.convert_from_vta(sample_vta_scenario)
        
        vehicle = sim_scenario.ego_vehicle
        assert vehicle.platform == 'EV'
        assert vehicle.battery_capacity_kwh is not None
        assert vehicle.battery_capacity_kwh > 0
    
    def test_extract_environment(self, converter, sample_vta_scenario):
        """Test environment extraction."""
        sim_scenario = converter.convert_from_vta(sample_vta_scenario)
        
        env = sim_scenario.environment
        assert env.temperature_celsius == 35.0
        assert env.humidity_percent == 60.0
        assert env.road_surface == RoadType.DRY_ASPHALT
    
    def test_extract_traffic(self, converter, sample_vta_scenario):
        """Test traffic extraction."""
        sim_scenario = converter.convert_from_vta(sample_vta_scenario)
        
        traffic = sim_scenario.traffic
        assert isinstance(traffic.density, TrafficDensity)
        assert traffic.num_vehicles >= 0
    
    def test_generate_route(self, converter, sample_vta_scenario):
        """Test route generation."""
        sim_scenario = converter.convert_from_vta(sample_vta_scenario)
        
        route = sim_scenario.route
        assert len(route.waypoints) > 0
        assert route.total_distance_m > 0
        assert route.route_type in ['urban', 'highway', 'rural', 'mixed']
    
    def test_extract_maneuvers(self, converter):
        """Test maneuver extraction."""
        vta_scenario = {
            'scenario_id': 'TEST-002',
            'test_name': 'Lane Change Test',
            'test_type': 'adas',
            'applicable_platforms': ['EV'],
            'environmental_conditions': {},
            'estimated_duration_hours': 1.0
        }
        
        sim_scenario = converter.convert_from_vta(vta_scenario)
        
        # ADAS test should include lane change maneuver
        assert len(sim_scenario.maneuvers) > 0
        assert any(m.maneuver_type == 'lane_change' for m in sim_scenario.maneuvers)
    
    def test_convert_batch(self, converter):
        """Test batch conversion."""
        vta_scenarios = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'test_name': f'Test {i}',
                'test_type': 'performance',
                'applicable_platforms': ['EV'],
                'environmental_conditions': {},
                'estimated_duration_hours': 1.0
            }
            for i in range(3)
        ]
        
        sim_scenarios = converter.convert_batch(vta_scenarios, SimulationPlatform.CARLA)
        
        assert len(sim_scenarios) == 3
        assert all(isinstance(s, SimulationScenario) for s in sim_scenarios)


class TestCARLAExporter:
    """Test CARLA exporter."""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        """Create CARLA exporter with temp directory."""
        return create_carla_exporter(output_dir=str(tmp_path / "carla"))
    
    @pytest.fixture
    def sample_sim_scenario(self):
        """Create sample simulation scenario."""
        vehicle = VehicleConfiguration(model="Ariya", platform="EV")
        env = EnvironmentalConditions(weather=WeatherCondition.CLEAR)
        traffic = TrafficScenario(density=TrafficDensity.MEDIUM, num_vehicles=10)
        route = Route()
        
        return SimulationScenario(
            scenario_id="SIM-001",
            name="CARLA Test",
            description="Test scenario for CARLA",
            platform=SimulationPlatform.CARLA,
            ego_vehicle=vehicle,
            environment=env,
            traffic=traffic,
            route=route,
            duration_seconds=300.0
        )
    
    def test_exporter_initialization(self, exporter):
        """Test exporter initializes correctly."""
        assert exporter is not None
        assert exporter.output_dir.exists()
    
    def test_export_python_script(self, exporter, sample_sim_scenario):
        """Test Python script generation."""
        output_path = exporter.export_python_script(sample_sim_scenario)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.py'
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'import carla' in content
        assert 'def main()' in content
        assert sample_sim_scenario.name in content
    
    def test_export_openscenario(self, exporter, sample_sim_scenario):
        """Test OpenScenario XML generation."""
        output_path = exporter.export_openscenario(sample_sim_scenario)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.xosc'
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '<?xml version="1.0"' in content
        assert '<OpenSCENARIO>' in content
        assert sample_sim_scenario.ego_vehicle.model in content
    
    def test_weather_mapping(self, exporter, sample_sim_scenario):
        """Test weather condition mapping."""
        weather_config = exporter._get_weather_config(WeatherCondition.RAIN)
        
        assert 'cloudiness' in weather_config
        assert 'precipitation' in weather_config
        assert weather_config['precipitation'] > 0


class TestSUMOExporter:
    """Test SUMO exporter."""
    
    @pytest.fixture
    def exporter(self, tmp_path):
        """Create SUMO exporter with temp directory."""
        return create_sumo_exporter(output_dir=str(tmp_path / "sumo"))
    
    @pytest.fixture
    def sample_sim_scenario(self):
        """Create sample simulation scenario."""
        vehicle = VehicleConfiguration(model="Ariya", platform="EV", battery_capacity_kwh=87.0)
        env = EnvironmentalConditions()
        traffic = TrafficScenario(density=TrafficDensity.MEDIUM, num_vehicles=10)
        route = Route()
        
        return SimulationScenario(
            scenario_id="SIM-002",
            name="SUMO Test",
            description="Test scenario for SUMO",
            platform=SimulationPlatform.SUMO,
            ego_vehicle=vehicle,
            environment=env,
            traffic=traffic,
            route=route,
            duration_seconds=300.0
        )
    
    def test_exporter_initialization(self, exporter):
        """Test exporter initializes correctly."""
        assert exporter is not None
        assert exporter.output_dir.exists()
    
    def test_export_vehicle_types(self, exporter, sample_sim_scenario):
        """Test vehicle type file generation."""
        output_path = exporter.export_vehicle_types(sample_sim_scenario)
        
        assert Path(output_path).exists()
        assert output_path.endswith('.vtype.xml')
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '<additional' in content
        assert '<vType' in content
        assert sample_sim_scenario.ego_vehicle.model in content
    
    def test_export_routes(self, exporter, sample_sim_scenario):
        """Test route file generation."""
        output_path = exporter.export_routes(sample_sim_scenario)
        
        assert Path(output_path).exists()
        assert output_path.endswith('.rou.xml')
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '<routes' in content
        assert '<route' in content
        assert '<vehicle' in content
    
    def test_export_config(self, exporter, sample_sim_scenario):
        """Test configuration file generation."""
        output_path = exporter.export_config(
            sample_sim_scenario,
            network_file="test.net.xml",
            vtype_file="test.vtype.xml",
            route_file="test.rou.xml"
        )
        
        assert Path(output_path).exists()
        assert output_path.endswith('.sumocfg')
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '<configuration' in content
        assert '<input' in content
        assert '<time' in content
    
    def test_export_complete_scenario(self, exporter, sample_sim_scenario):
        """Test complete scenario export."""
        files = exporter.export_scenario(sample_sim_scenario)
        
        assert 'vtype' in files
        assert 'routes' in files
        assert 'config' in files
        
        # Verify all files exist
        for file_path in files.values():
            assert Path(file_path).exists()


class TestIntegration:
    """Integration tests for simulation export workflow."""
    
    def test_end_to_end_carla_export(self, tmp_path):
        """Test complete workflow: VTA -> Sim -> CARLA export."""
        # Create VTA scenario
        vta_scenario = {
            'scenario_id': 'E2E-001',
            'test_name': 'End-to-End Test',
            'test_type': 'performance',
            'applicable_platforms': ['EV'],
            'environmental_conditions': {
                'ambient_temperature_celsius': 20.0,
                'road_surface_condition': 'dry'
            },
            'estimated_duration_hours': 0.5
        }
        
        # Convert to simulation scenario
        converter = create_scenario_converter()
        sim_scenario = converter.convert_from_vta(vta_scenario, SimulationPlatform.CARLA)
        
        assert sim_scenario.platform == SimulationPlatform.CARLA
        
        # Export to CARLA
        exporter = create_carla_exporter(output_dir=str(tmp_path / "carla"))
        python_script = exporter.export_python_script(sim_scenario)
        
        assert Path(python_script).exists()
    
    def test_end_to_end_sumo_export(self, tmp_path):
        """Test complete workflow: VTA -> Sim -> SUMO export."""
        # Create VTA scenario
        vta_scenario = {
            'scenario_id': 'E2E-002',
            'test_name': 'End-to-End SUMO Test',
            'test_type': 'adas',
            'applicable_platforms': ['EV'],
            'environmental_conditions': {},
            'estimated_duration_hours': 1.0
        }
        
        # Convert to simulation scenario
        converter = create_scenario_converter()
        sim_scenario = converter.convert_from_vta(vta_scenario, SimulationPlatform.SUMO)
        
        assert sim_scenario.platform == SimulationPlatform.SUMO
        
        # Export to SUMO
        exporter = create_sumo_exporter(output_dir=str(tmp_path / "sumo"))
        files = exporter.export_scenario(sim_scenario)
        
        assert len(files) == 3  # vtype, routes, config
        assert all(Path(f).exists() for f in files.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

