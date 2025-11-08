"""
CARLA simulation exporter.
Exports test scenarios to CARLA-compatible formats (Python scripts and OpenScenario XML).
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from src.sim.base import (
    SimulationScenario,
    SimulationPlatform,
    WeatherCondition,
    RoadType,
    TrafficDensity
)

logger = logging.getLogger(__name__)


class CARLAExporter:
    """
    Exports simulation scenarios to CARLA format.
    
    Supports:
    - Python script generation for CARLA API
    - OpenScenario 1.0 XML format
    - Weather and traffic configuration
    """
    
    def __init__(self, output_dir: str = "sim_output/carla"):
        """
        Initialize CARLA exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_python_script(
        self,
        scenario: SimulationScenario,
        filename: Optional[str] = None
    ) -> str:
        """
        Export scenario as CARLA Python script.
        
        Args:
            scenario: Simulation scenario
            filename: Output filename (default: scenario_id.py)
            
        Returns:
            Path to generated script
        """
        if filename is None:
            filename = f"{scenario.scenario_id}.py"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating CARLA Python script: {output_path}")
        
        # Generate script content
        script = self._generate_python_script(scenario)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        logger.info(f"CARLA script generated: {output_path}")
        
        return str(output_path)
    
    def _generate_python_script(self, scenario: SimulationScenario) -> str:
        """Generate Python script content for CARLA."""
        
        # Map weather conditions
        weather_map = self._get_weather_config(scenario.environment.weather)
        
        # Map traffic density to number of vehicles
        traffic_config = self._get_traffic_config(scenario.traffic)
        
        script = f'''#!/usr/bin/env python3
"""
CARLA Simulation Script: {scenario.name}
Generated from VTA Test Scenario: {scenario.scenario_id}

Description: {scenario.description}
"""

import carla
import random
import time
import math

def main():
    """Main simulation function."""
    # Connect to CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    try:
        # Get world
        world = client.get_world()
        
        # Configure weather
        weather = carla.WeatherParameters(
            cloudiness={weather_map['cloudiness']},
            precipitation={weather_map['precipitation']},
            precipitation_deposits={weather_map['precipitation_deposits']},
            wind_intensity={weather_map['wind_intensity']},
            sun_azimuth_angle={scenario.environment.sun_azimuth_angle},
            sun_altitude_angle={scenario.environment.sun_altitude_angle},
            fog_density={weather_map['fog_density']},
            fog_distance={weather_map['fog_distance']},
            wetness={weather_map['wetness']}
        )
        world.set_weather(weather)
        
        # Get blueprint library
        blueprint_library = world.get_blueprint_library()
        
        # Spawn ego vehicle
        ego_bp = blueprint_library.filter('{self._get_carla_vehicle_model(scenario.ego_vehicle.model)}')[0]
        spawn_points = world.get_map().get_spawn_points()
        
        if len(spawn_points) > 0:
            ego_vehicle = world.spawn_actor(ego_bp, spawn_points[0])
            print(f"Spawned ego vehicle: {{ego_vehicle.type_id}}")
            
            # Configure physics (if EV platform)
            if "{scenario.ego_vehicle.platform}" == "EV":
                physics_control = ego_vehicle.get_physics_control()
                physics_control.mass = {scenario.ego_vehicle.mass_kg}
                ego_vehicle.apply_physics_control(physics_control)
            
            # Spawn traffic vehicles
            traffic_vehicles = []
            vehicle_bps = blueprint_library.filter('vehicle.*')
            
            for i in range({traffic_config['num_vehicles']}):
                if i + 1 < len(spawn_points):
                    bp = random.choice(vehicle_bps)
                    vehicle = world.try_spawn_actor(bp, spawn_points[i + 1])
                    if vehicle:
                        traffic_vehicles.append(vehicle)
                        vehicle.set_autopilot(True)
            
            print(f"Spawned {{len(traffic_vehicles)}} traffic vehicles")
            
            # Enable autopilot for ego vehicle
            ego_vehicle.set_autopilot(True)
            
            # Run simulation
            duration = {scenario.duration_seconds}
            start_time = time.time()
            
            print(f"Running simulation for {{duration}} seconds...")
            
            while time.time() - start_time < duration:
                # Get ego vehicle state
                transform = ego_vehicle.get_transform()
                velocity = ego_vehicle.get_velocity()
                speed_kmh = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
                
                print(f"Time: {{time.time() - start_time:.1f}}s | "
                      f"Position: ({{transform.location.x:.1f}}, {{transform.location.y:.1f}}) | "
                      f"Speed: {{speed_kmh:.1f}} km/h")
                
                time.sleep(1.0)
            
            print("Simulation completed")
            
            # Cleanup
            ego_vehicle.destroy()
            for vehicle in traffic_vehicles:
                vehicle.destroy()
            
            print("Actors cleaned up")
        
        else:
            print("Error: No spawn points available")
    
    except Exception as e:
        print(f"Error during simulation: {{e}}")
    
    finally:
        print("Simulation finished")


if __name__ == '__main__':
    main()
'''
        
        return script
    
    def export_openscenario(
        self,
        scenario: SimulationScenario,
        filename: Optional[str] = None
    ) -> str:
        """
        Export scenario as OpenScenario XML.
        
        Args:
            scenario: Simulation scenario
            filename: Output filename (default: scenario_id.xosc)
            
        Returns:
            Path to generated XML file
        """
        if filename is None:
            filename = f"{scenario.scenario_id}.xosc"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating OpenScenario XML: {output_path}")
        
        # Generate XML content
        xml_content = self._generate_openscenario_xml(scenario)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"OpenScenario XML generated: {output_path}")
        
        return str(output_path)
    
    def _generate_openscenario_xml(self, scenario: SimulationScenario) -> str:
        """Generate OpenScenario 1.0 XML content."""
        
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
    <FileHeader revMajor="1" revMinor="0" date="2025-11-06" description="{scenario.name}" author="VTA"/>
    
    <ParameterDeclarations/>
    
    <CatalogLocations/>
    
    <RoadNetwork>
        <LogicFile filepath="Town01"/>
        <SceneGraphFile filepath=""/>
    </RoadNetwork>
    
    <Entities>
        <ScenarioObject name="Ego">
            <Vehicle name="{scenario.ego_vehicle.model}" vehicleCategory="car">
                <ParameterDeclarations/>
                <Performance maxSpeed="{scenario.ego_vehicle.max_speed_kmh / 3.6}" maxAcceleration="{scenario.ego_vehicle.acceleration_ms2}" maxDeceleration="10"/>
                <BoundingBox>
                    <Center x="1.5" y="0.0" z="0.9"/>
                    <Dimensions width="{scenario.ego_vehicle.track_width_m}" length="4.5" height="1.8"/>
                </BoundingBox>
                <Axles>
                    <FrontAxle maxSteering="0.5" wheelDiameter="0.6" trackWidth="{scenario.ego_vehicle.track_width_m}" positionX="{scenario.ego_vehicle.wheelbase_m}" positionZ="0.3"/>
                    <RearAxle maxSteering="0.0" wheelDiameter="0.6" trackWidth="{scenario.ego_vehicle.track_width_m}" positionX="0.0" positionZ="0.3"/>
                </Axles>
                <Properties>
                    <Property name="platform" value="{scenario.ego_vehicle.platform}"/>
                    <Property name="mass" value="{scenario.ego_vehicle.mass_kg}"/>
'''
        
        if scenario.ego_vehicle.battery_capacity_kwh:
            xml += f'                    <Property name="battery_capacity_kwh" value="{scenario.ego_vehicle.battery_capacity_kwh}"/>\n'
        
        xml += '''                </Properties>
            </Vehicle>
        </ScenarioObject>
    </Entities>
    
    <Storyboard>
        <Init>
            <Actions>
                <Private entityRef="Ego">
                    <PrivateAction>
                        <TeleportAction>
                            <Position>
                                <WorldPosition x="0.0" y="0.0" z="0.5" h="0.0"/>
                            </Position>
                        </TeleportAction>
                    </PrivateAction>
                </Private>
            </Actions>
        </Init>
        
        <Story name="TestStory">
            <Act name="TestAct">
'''
        
        # Add maneuvers
        for i, maneuver in enumerate(scenario.maneuvers):
            xml += f'''                <ManeuverGroup name="ManeuverGroup{i}" maximumExecutionCount="1">
                    <Actors selectTriggeringEntities="false">
                        <EntityRef entityRef="Ego"/>
                    </Actors>
                    <Maneuver name="{maneuver.maneuver_type}">
                        <Event name="{maneuver.maneuver_type}_Event" priority="overwrite">
                            <Action name="{maneuver.maneuver_type}_Action">
                                <PrivateAction>
                                    <LongitudinalAction>
                                        <SpeedAction>
                                            <SpeedActionDynamics dynamicsShape="step" value="0" dynamicsDimension="time"/>
                                            <SpeedActionTarget>
                                                <AbsoluteTargetSpeed value="15"/>
                                            </SpeedActionTarget>
                                        </SpeedAction>
                                    </LongitudinalAction>
                                </PrivateAction>
                            </Action>
                            <StartTrigger>
                                <ConditionGroup>
                                    <Condition name="StartCondition" delay="0" conditionEdge="rising">
                                        <ByValueCondition>
                                            <SimulationTimeCondition value="{maneuver.trigger_time_s}" rule="greaterThan"/>
                                        </ByValueCondition>
                                    </Condition>
                                </ConditionGroup>
                            </StartTrigger>
                        </Event>
                    </Maneuver>
                </ManeuverGroup>
'''
        
        xml += f'''                <StartTrigger>
                    <ConditionGroup>
                        <Condition name="ActStart" delay="0" conditionEdge="rising">
                            <ByValueCondition>
                                <SimulationTimeCondition value="0" rule="greaterThan"/>
                            </ByValueCondition>
                        </Condition>
                    </ConditionGroup>
                </StartTrigger>
                <StopTrigger>
                    <ConditionGroup>
                        <Condition name="ActEnd" delay="0" conditionEdge="rising">
                            <ByValueCondition>
                                <SimulationTimeCondition value="{scenario.duration_seconds}" rule="greaterThan"/>
                            </ByValueCondition>
                        </Condition>
                    </ConditionGroup>
                </StopTrigger>
            </Act>
        </Story>
        
        <StopTrigger/>
    </Storyboard>
</OpenSCENARIO>
'''
        
        return xml
    
    def _get_weather_config(self, weather: WeatherCondition) -> Dict[str, float]:
        """Map weather condition to CARLA parameters."""
        weather_configs = {
            WeatherCondition.CLEAR: {
                'cloudiness': 10.0,
                'precipitation': 0.0,
                'precipitation_deposits': 0.0,
                'wind_intensity': 5.0,
                'fog_density': 0.0,
                'fog_distance': 0.0,
                'wetness': 0.0
            },
            WeatherCondition.CLOUDY: {
                'cloudiness': 80.0,
                'precipitation': 0.0,
                'precipitation_deposits': 0.0,
                'wind_intensity': 10.0,
                'fog_density': 0.0,
                'fog_distance': 0.0,
                'wetness': 0.0
            },
            WeatherCondition.WET: {
                'cloudiness': 50.0,
                'precipitation': 0.0,
                'precipitation_deposits': 50.0,
                'wind_intensity': 10.0,
                'fog_density': 0.0,
                'fog_distance': 0.0,
                'wetness': 50.0
            },
            WeatherCondition.RAIN: {
                'cloudiness': 90.0,
                'precipitation': 30.0,
                'precipitation_deposits': 50.0,
                'wind_intensity': 20.0,
                'fog_density': 10.0,
                'fog_distance': 50.0,
                'wetness': 70.0
            },
            WeatherCondition.HEAVY_RAIN: {
                'cloudiness': 100.0,
                'precipitation': 80.0,
                'precipitation_deposits': 90.0,
                'wind_intensity': 50.0,
                'fog_density': 20.0,
                'fog_distance': 30.0,
                'wetness': 100.0
            },
            WeatherCondition.FOG: {
                'cloudiness': 60.0,
                'precipitation': 0.0,
                'precipitation_deposits': 0.0,
                'wind_intensity': 5.0,
                'fog_density': 70.0,
                'fog_distance': 10.0,
                'wetness': 0.0
            },
            WeatherCondition.SNOW: {
                'cloudiness': 100.0,
                'precipitation': 50.0,
                'precipitation_deposits': 100.0,
                'wind_intensity': 30.0,
                'fog_density': 30.0,
                'fog_distance': 20.0,
                'wetness': 20.0
            }
        }
        
        return weather_configs.get(weather, weather_configs[WeatherCondition.CLEAR])
    
    def _get_traffic_config(self, traffic) -> Dict[str, int]:
        """Map traffic density to vehicle counts."""
        return {
            'num_vehicles': traffic.num_vehicles,
            'num_pedestrians': traffic.num_pedestrians
        }
    
    def _get_carla_vehicle_model(self, model_name: str) -> str:
        """Map VTA vehicle model to CARLA blueprint."""
        # Map Nissan models to closest CARLA equivalents
        model_map = {
            'Ariya': 'vehicle.tesla.model3',
            'Leaf': 'vehicle.tesla.model3',
            'Qashqai': 'vehicle.audi.a2',
            'X-Trail': 'vehicle.audi.etron',
            'Juke': 'vehicle.mini.cooper_s',
            'Micra': 'vehicle.mini.cooper_s'
        }
        
        return model_map.get(model_name, 'vehicle.tesla.model3')
    
    def export_batch(
        self,
        scenarios: List[SimulationScenario],
        format: str = "python"
    ) -> List[str]:
        """
        Export multiple scenarios.
        
        Args:
            scenarios: List of simulation scenarios
            format: Export format ("python" or "openscenario")
            
        Returns:
            List of generated file paths
        """
        logger.info(f"Exporting {len(scenarios)} scenarios to CARLA {format} format...")
        
        exported_files = []
        
        for scenario in scenarios:
            try:
                if format == "python":
                    file_path = self.export_python_script(scenario)
                elif format == "openscenario":
                    file_path = self.export_openscenario(scenario)
                else:
                    raise ValueError(f"Unknown format: {format}")
                
                exported_files.append(file_path)
            
            except Exception as e:
                logger.error(f"Failed to export scenario {scenario.scenario_id}: {e}")
        
        logger.info(f"Exported {len(exported_files)}/{len(scenarios)} scenarios")
        
        return exported_files


def create_carla_exporter(output_dir: str = "sim_output/carla") -> CARLAExporter:
    """
    Create a CARLA exporter instance.
    
    Args:
        output_dir: Directory for output files
        
    Returns:
        CARLAExporter instance
    """
    return CARLAExporter(output_dir=output_dir)

