"""
Converts VTA test scenarios to simulation scenarios (CARLA/SUMO format).
"""
import logging
from typing import Dict, Any, List, Optional
import json

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

logger = logging.getLogger(__name__)


class ScenarioConverter:
    """
    Converts VTA test scenarios to simulation-ready scenarios.
    """
    
    def __init__(self):
        """Initialize scenario converter."""
        pass
    
    def convert_from_vta(
        self,
        vta_scenario: Dict[str, Any],
        platform: SimulationPlatform = SimulationPlatform.CARLA
    ) -> SimulationScenario:
        """
        Convert VTA test scenario to simulation scenario.
        
        Args:
            vta_scenario: VTA test scenario dictionary
            platform: Target simulation platform
            
        Returns:
            SimulationScenario instance
        """
        logger.info(f"Converting VTA scenario {vta_scenario.get('scenario_id')} to {platform.value}")
        
        # Extract vehicle configuration
        ego_vehicle = self._extract_vehicle_config(vta_scenario)
        
        # Extract environmental conditions
        environment = self._extract_environment(vta_scenario)
        
        # Extract traffic scenario
        traffic = self._extract_traffic(vta_scenario)
        
        # Generate route
        route = self._generate_route(vta_scenario)
        
        # Extract test maneuvers
        maneuvers = self._extract_maneuvers(vta_scenario)
        
        # Create simulation scenario
        sim_scenario = SimulationScenario(
            scenario_id=vta_scenario.get('scenario_id', 'UNKNOWN'),
            name=vta_scenario.get('test_name', 'Unnamed Test'),
            description=vta_scenario.get('description', ''),
            platform=platform,
            ego_vehicle=ego_vehicle,
            environment=environment,
            traffic=traffic,
            route=route,
            maneuvers=maneuvers,
            duration_seconds=vta_scenario.get('estimated_duration_hours', 1.0) * 3600,
            success_criteria=self._extract_success_criteria(vta_scenario),
            metadata=self._extract_metadata(vta_scenario)
        )
        
        logger.info(f"Converted scenario: {sim_scenario.name}")
        
        return sim_scenario
    
    def _extract_vehicle_config(self, vta_scenario: Dict[str, Any]) -> VehicleConfiguration:
        """Extract vehicle configuration from VTA scenario."""
        
        # Get vehicle model and platform
        platforms = vta_scenario.get('applicable_platforms', ['EV'])
        platform = platforms[0] if platforms else 'EV'
        
        # Get components to estimate vehicle specs
        components = vta_scenario.get('target_components', [])
        
        # Estimate battery capacity for EVs
        battery_capacity = None
        if platform == 'EV':
            battery_capacity = 60.0  # Default 60 kWh
            if 'High_Voltage_Battery' in components:
                battery_capacity = 87.0  # Ariya-like capacity
        
        # Estimate engine power
        engine_power = None
        if platform == 'ICE':
            engine_power = 120.0  # kW
        elif platform == 'HEV':
            engine_power = 100.0  # kW (combined)
        elif platform == 'EV':
            engine_power = 160.0  # kW (Ariya-like)
        
        # Default vehicle model
        model = "Ariya" if platform == 'EV' else "Qashqai"
        
        return VehicleConfiguration(
            model=model,
            platform=platform,
            mass_kg=1800.0 if platform == 'EV' else 1500.0,
            max_speed_kmh=180.0,
            acceleration_ms2=3.5 if platform == 'EV' else 2.8,
            wheelbase_m=2.775 if platform == 'EV' else 2.705,
            track_width_m=1.850,
            cog_height_m=0.600 if platform == 'EV' else 0.700,
            battery_capacity_kwh=battery_capacity,
            engine_power_kw=engine_power
        )
    
    def _extract_environment(self, vta_scenario: Dict[str, Any]) -> EnvironmentalConditions:
        """Extract environmental conditions from VTA scenario."""
        
        conditions = vta_scenario.get('environmental_conditions', {})
        
        # Map temperature to weather
        temp = conditions.get('ambient_temperature_celsius', 20.0)
        humidity = conditions.get('humidity_percent', 50.0)
        
        # Determine weather from conditions
        weather = WeatherCondition.CLEAR
        road_surface = RoadType.DRY_ASPHALT
        
        surface_condition = conditions.get('road_surface_condition', 'dry')
        if 'wet' in surface_condition.lower():
            weather = WeatherCondition.WET
            road_surface = RoadType.WET_ASPHALT
        elif 'rain' in surface_condition.lower():
            weather = WeatherCondition.RAIN
            road_surface = RoadType.WET_ASPHALT
        elif 'snow' in surface_condition.lower():
            weather = WeatherCondition.SNOW
            road_surface = RoadType.SNOW
        elif 'ice' in surface_condition.lower():
            weather = WeatherCondition.CLEAR
            road_surface = RoadType.ICE
        
        # Determine time of day from temperature and conditions
        time_of_day = "noon"
        if temp < 5.0:
            time_of_day = "night"
        elif temp < 15.0:
            time_of_day = "morning"
        
        return EnvironmentalConditions(
            weather=weather,
            road_surface=road_surface,
            temperature_celsius=temp,
            humidity_percent=humidity,
            wind_speed_ms=0.0,
            time_of_day=time_of_day,
            sun_azimuth_angle=180.0,
            sun_altitude_angle=45.0 if time_of_day in ['noon', 'afternoon'] else 15.0
        )
    
    def _extract_traffic(self, vta_scenario: Dict[str, Any]) -> TrafficScenario:
        """Extract traffic scenario from VTA scenario."""
        
        # Default to medium traffic
        density = TrafficDensity.MEDIUM
        
        test_type = vta_scenario.get('test_type', '')
        
        # Adjust based on test type
        if 'performance' in test_type.lower() or 'acceleration' in test_type.lower():
            density = TrafficDensity.EMPTY
        elif 'adas' in test_type.lower() or 'safety' in test_type.lower():
            density = TrafficDensity.HIGH
        elif 'durability' in test_type.lower():
            density = TrafficDensity.LOW
        
        # Map density to vehicle counts
        density_vehicles = {
            TrafficDensity.EMPTY: 0,
            TrafficDensity.LOW: 5,
            TrafficDensity.MEDIUM: 15,
            TrafficDensity.HIGH: 30,
            TrafficDensity.VERY_HIGH: 50
        }
        
        num_vehicles = density_vehicles.get(density, 15)
        
        return TrafficScenario(
            density=density,
            num_vehicles=num_vehicles,
            num_pedestrians=5 if density in [TrafficDensity.MEDIUM, TrafficDensity.HIGH] else 0,
            aggressive_drivers_percent=10.0,
            spawn_radius_m=100.0
        )
    
    def _generate_route(self, vta_scenario: Dict[str, Any]) -> Route:
        """Generate route from VTA scenario."""
        
        # Default route type based on test type
        test_type = vta_scenario.get('test_type', '')
        route_type = "urban"
        
        if 'highway' in test_type.lower() or 'performance' in test_type.lower():
            route_type = "highway"
        elif 'durability' in test_type.lower():
            route_type = "mixed"
        
        # Generate simple waypoints (placeholder)
        waypoints = [
            (0.0, 0.0, 0.5),
            (100.0, 0.0, 0.5),
            (200.0, 50.0, 0.5),
            (300.0, 50.0, 0.5),
            (400.0, 0.0, 0.5)
        ]
        
        # Speed limits based on route type
        if route_type == "highway":
            speed_limits = [120.0] * len(waypoints)
        elif route_type == "urban":
            speed_limits = [50.0] * len(waypoints)
        else:
            speed_limits = [80.0] * len(waypoints)
        
        total_distance = 2000.0  # meters (placeholder)
        
        return Route(
            waypoints=waypoints,
            speed_limits_kmh=speed_limits,
            total_distance_m=total_distance,
            route_type=route_type
        )
    
    def _extract_maneuvers(self, vta_scenario: Dict[str, Any]) -> List[TestManeuver]:
        """Extract test maneuvers from VTA scenario."""
        
        maneuvers = []
        test_type = vta_scenario.get('test_type', '').lower()
        
        # Create maneuvers based on test type
        if 'acceleration' in test_type or 'performance' in test_type:
            maneuvers.append(TestManeuver(
                maneuver_type='acceleration',
                trigger_time_s=10.0,
                duration_s=15.0,
                parameters={'target_speed_kmh': 100.0}
            ))
        
        if 'brake' in test_type or 'safety' in test_type:
            maneuvers.append(TestManeuver(
                maneuver_type='emergency_brake',
                trigger_time_s=30.0,
                duration_s=5.0,
                parameters={'initial_speed_kmh': 80.0}
            ))
        
        if 'lane' in test_type or 'adas' in test_type:
            maneuvers.append(TestManeuver(
                maneuver_type='lane_change',
                trigger_time_s=20.0,
                duration_s=8.0,
                parameters={'direction': 'left'}
            ))
        
        if 'overtake' in test_type:
            maneuvers.append(TestManeuver(
                maneuver_type='overtake',
                trigger_time_s=40.0,
                duration_s=12.0,
                parameters={'target_vehicle_speed_kmh': 60.0}
            ))
        
        return maneuvers
    
    def _extract_success_criteria(self, vta_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Extract success criteria from VTA scenario."""
        
        criteria = {
            'no_collisions': True,
            'max_lateral_acceleration_ms2': 5.0,
            'max_longitudinal_acceleration_ms2': 8.0,
            'min_safety_distance_m': 2.0
        }
        
        # Add test-specific criteria
        test_type = vta_scenario.get('test_type', '').lower()
        
        if 'performance' in test_type:
            criteria['min_top_speed_kmh'] = 100.0
            criteria['max_0_100_time_s'] = 10.0
        
        if 'adas' in test_type:
            criteria['adas_alerts_required'] = True
            criteria['min_detection_range_m'] = 50.0
        
        if 'emissions' in test_type:
            criteria['max_co2_g_km'] = 120.0
        
        return criteria
    
    def _extract_metadata(self, vta_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from VTA scenario."""
        
        return {
            'test_type': vta_scenario.get('test_type'),
            'complexity_score': vta_scenario.get('complexity_score'),
            'risk_level': vta_scenario.get('risk_level'),
            'regulatory_standards': vta_scenario.get('regulatory_standards', []),
            'target_systems': vta_scenario.get('target_systems', []),
            'target_components': vta_scenario.get('target_components', []),
            'estimated_cost_gbp': vta_scenario.get('estimated_cost_gbp'),
            'certification_required': vta_scenario.get('certification_required', False)
        }
    
    def convert_batch(
        self,
        vta_scenarios: List[Dict[str, Any]],
        platform: SimulationPlatform = SimulationPlatform.CARLA
    ) -> List[SimulationScenario]:
        """
        Convert multiple VTA scenarios.
        
        Args:
            vta_scenarios: List of VTA test scenarios
            platform: Target simulation platform
            
        Returns:
            List of SimulationScenario instances
        """
        logger.info(f"Converting {len(vta_scenarios)} VTA scenarios to {platform.value}...")
        
        sim_scenarios = []
        
        for vta_scenario in vta_scenarios:
            try:
                sim_scenario = self.convert_from_vta(vta_scenario, platform)
                sim_scenarios.append(sim_scenario)
            
            except Exception as e:
                logger.error(f"Failed to convert scenario {vta_scenario.get('scenario_id')}: {e}")
        
        logger.info(f"Converted {len(sim_scenarios)}/{len(vta_scenarios)} scenarios")
        
        return sim_scenarios
    
    def load_vta_scenarios(self, json_file: str) -> List[Dict[str, Any]]:
        """
        Load VTA scenarios from JSON file.
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            List of VTA scenario dictionaries
        """
        logger.info(f"Loading VTA scenarios from {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scenarios = data.get('scenarios', [])
        
        logger.info(f"Loaded {len(scenarios)} scenarios")
        
        return scenarios


def create_scenario_converter() -> ScenarioConverter:
    """
    Create a scenario converter instance.
    
    Returns:
        ScenarioConverter instance
    """
    return ScenarioConverter()

