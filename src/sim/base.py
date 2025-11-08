"""
Base data structures for simulation scenarios.
Supports CARLA and SUMO simulation platforms.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class SimulationPlatform(Enum):
    """Supported simulation platforms."""
    CARLA = "CARLA"
    SUMO = "SUMO"


class WeatherCondition(Enum):
    """Weather conditions for simulation."""
    CLEAR = "Clear"
    CLOUDY = "Cloudy"
    WET = "Wet"
    RAIN = "Rain"
    HEAVY_RAIN = "HeavyRain"
    FOG = "Fog"
    SNOW = "Snow"


class RoadType(Enum):
    """Road surface types."""
    DRY_ASPHALT = "DryAsphalt"
    WET_ASPHALT = "WetAsphalt"
    SNOW = "Snow"
    ICE = "Ice"
    GRAVEL = "Gravel"


class TrafficDensity(Enum):
    """Traffic density levels."""
    EMPTY = "Empty"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "VeryHigh"


@dataclass
class VehicleConfiguration:
    """Vehicle configuration for simulation."""
    model: str
    platform: str  # EV, HEV, ICE
    mass_kg: float = 1500.0
    max_speed_kmh: float = 180.0
    acceleration_ms2: float = 3.0
    wheelbase_m: float = 2.7
    track_width_m: float = 1.6
    cog_height_m: float = 0.6
    battery_capacity_kwh: Optional[float] = None
    engine_power_kw: Optional[float] = None


@dataclass
class EnvironmentalConditions:
    """Environmental conditions for simulation."""
    weather: WeatherCondition = WeatherCondition.CLEAR
    road_surface: RoadType = RoadType.DRY_ASPHALT
    temperature_celsius: float = 20.0
    humidity_percent: float = 50.0
    wind_speed_ms: float = 0.0
    time_of_day: str = "noon"  # dawn, morning, noon, afternoon, dusk, night
    sun_azimuth_angle: float = 180.0
    sun_altitude_angle: float = 45.0


@dataclass
class TrafficScenario:
    """Traffic scenario configuration."""
    density: TrafficDensity = TrafficDensity.MEDIUM
    num_vehicles: int = 10
    num_pedestrians: int = 5
    aggressive_drivers_percent: float = 10.0
    spawn_radius_m: float = 50.0


@dataclass
class Route:
    """Route definition for simulation."""
    waypoints: List[Tuple[float, float, float]] = field(default_factory=list)  # (x, y, z)
    speed_limits_kmh: List[float] = field(default_factory=list)
    total_distance_m: float = 0.0
    route_type: str = "urban"  # urban, highway, rural, mixed


@dataclass
class TestManeuver:
    """Test maneuver definition."""
    maneuver_type: str  # lane_change, overtake, emergency_brake, acceleration, cornering
    trigger_time_s: float
    duration_s: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationScenario:
    """
    Complete simulation scenario.
    
    This is the base format that can be exported to CARLA, SUMO, or other platforms.
    """
    scenario_id: str
    name: str
    description: str
    platform: SimulationPlatform
    
    # Vehicle configuration
    ego_vehicle: VehicleConfiguration
    
    # Environment
    environment: EnvironmentalConditions
    
    # Traffic
    traffic: TrafficScenario
    
    # Route
    route: Route
    
    # Test maneuvers
    maneuvers: List[TestManeuver] = field(default_factory=list)
    
    # Duration
    duration_seconds: float = 300.0
    
    # Success criteria
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'description': self.description,
            'platform': self.platform.value,
            'ego_vehicle': {
                'model': self.ego_vehicle.model,
                'platform': self.ego_vehicle.platform,
                'mass_kg': self.ego_vehicle.mass_kg,
                'max_speed_kmh': self.ego_vehicle.max_speed_kmh,
                'acceleration_ms2': self.ego_vehicle.acceleration_ms2,
                'wheelbase_m': self.ego_vehicle.wheelbase_m,
                'track_width_m': self.ego_vehicle.track_width_m,
                'cog_height_m': self.ego_vehicle.cog_height_m,
                'battery_capacity_kwh': self.ego_vehicle.battery_capacity_kwh,
                'engine_power_kw': self.ego_vehicle.engine_power_kw,
            },
            'environment': {
                'weather': self.environment.weather.value,
                'road_surface': self.environment.road_surface.value,
                'temperature_celsius': self.environment.temperature_celsius,
                'humidity_percent': self.environment.humidity_percent,
                'wind_speed_ms': self.environment.wind_speed_ms,
                'time_of_day': self.environment.time_of_day,
                'sun_azimuth_angle': self.environment.sun_azimuth_angle,
                'sun_altitude_angle': self.environment.sun_altitude_angle,
            },
            'traffic': {
                'density': self.traffic.density.value,
                'num_vehicles': self.traffic.num_vehicles,
                'num_pedestrians': self.traffic.num_pedestrians,
                'aggressive_drivers_percent': self.traffic.aggressive_drivers_percent,
                'spawn_radius_m': self.traffic.spawn_radius_m,
            },
            'route': {
                'waypoints': self.route.waypoints,
                'speed_limits_kmh': self.route.speed_limits_kmh,
                'total_distance_m': self.route.total_distance_m,
                'route_type': self.route.route_type,
            },
            'maneuvers': [
                {
                    'maneuver_type': m.maneuver_type,
                    'trigger_time_s': m.trigger_time_s,
                    'duration_s': m.duration_s,
                    'parameters': m.parameters
                }
                for m in self.maneuvers
            ],
            'duration_seconds': self.duration_seconds,
            'success_criteria': self.success_criteria,
            'metadata': self.metadata
        }


@dataclass
class SimulationResult:
    """Results from simulation execution."""
    scenario_id: str
    platform: SimulationPlatform
    success: bool
    duration_seconds: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'scenario_id': self.scenario_id,
            'platform': self.platform.value,
            'success': self.success,
            'duration_seconds': self.duration_seconds,
            'metrics': self.metrics,
            'errors': self.errors,
            'warnings': self.warnings
        }

