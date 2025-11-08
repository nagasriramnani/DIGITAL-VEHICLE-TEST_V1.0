"""
SUMO simulation exporter.
Exports test scenarios to SUMO-compatible XML format (routes, vehicles, config).
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

from src.sim.base import (
    SimulationScenario,
    SimulationPlatform,
    WeatherCondition,
    RoadType,
    TrafficDensity
)

logger = logging.getLogger(__name__)


class SUMOExporter:
    """
    Exports simulation scenarios to SUMO format.
    
    Generates:
    - Route files (.rou.xml)
    - Vehicle type definitions (.vtype.xml)
    - Network files (.net.xml) - references
    - Configuration files (.sumocfg)
    """
    
    def __init__(self, output_dir: str = "sim_output/sumo"):
        """
        Initialize SUMO exporter.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_scenario(
        self,
        scenario: SimulationScenario,
        network_file: str = "Town01.net.xml"
    ) -> Dict[str, str]:
        """
        Export complete scenario to SUMO format.
        
        Args:
            scenario: Simulation scenario
            network_file: SUMO network file to use
            
        Returns:
            Dictionary of generated file paths
        """
        logger.info(f"Exporting scenario {scenario.scenario_id} to SUMO format...")
        
        files = {}
        
        # Export vehicle types
        vtype_file = self.export_vehicle_types(scenario)
        files['vtype'] = vtype_file
        
        # Export routes
        route_file = self.export_routes(scenario)
        files['routes'] = route_file
        
        # Export configuration
        config_file = self.export_config(scenario, network_file, vtype_file, route_file)
        files['config'] = config_file
        
        logger.info(f"SUMO scenario exported: {len(files)} files")
        
        return files
    
    def export_vehicle_types(
        self,
        scenario: SimulationScenario,
        filename: Optional[str] = None
    ) -> str:
        """
        Export vehicle type definitions.
        
        Args:
            scenario: Simulation scenario
            filename: Output filename (default: scenario_id.vtype.xml)
            
        Returns:
            Path to generated file
        """
        if filename is None:
            filename = f"{scenario.scenario_id}.vtype.xml"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating SUMO vehicle types: {output_path}")
        
        # Create XML structure
        root = ET.Element('additional')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/additional_file.xsd')
        
        # Add ego vehicle type
        ego_vtype = ET.SubElement(root, 'vType')
        ego_vtype.set('id', f'ego_{scenario.ego_vehicle.model}')
        ego_vtype.set('vClass', self._get_sumo_vclass(scenario.ego_vehicle.platform))
        ego_vtype.set('accel', str(scenario.ego_vehicle.acceleration_ms2))
        ego_vtype.set('decel', '4.5')
        ego_vtype.set('sigma', '0.5')
        ego_vtype.set('length', '4.5')
        ego_vtype.set('width', str(scenario.ego_vehicle.track_width_m))
        ego_vtype.set('maxSpeed', str(scenario.ego_vehicle.max_speed_kmh / 3.6))
        ego_vtype.set('color', '0,255,0')  # Green for ego
        
        # Add parameters
        ego_param = ET.SubElement(ego_vtype, 'param')
        ego_param.set('key', 'platform')
        ego_param.set('value', scenario.ego_vehicle.platform)
        
        if scenario.ego_vehicle.battery_capacity_kwh:
            battery_param = ET.SubElement(ego_vtype, 'param')
            battery_param.set('key', 'batteryCapacity')
            battery_param.set('value', str(scenario.ego_vehicle.battery_capacity_kwh))
        
        # Add standard traffic vehicle types
        traffic_vtypes = [
            ('passenger_car', 'passenger', 2.6, 4.5, 'sedan'),
            ('suv', 'passenger', 2.4, 4.8, 'SUV'),
            ('small_car', 'passenger', 2.8, 3.7, 'hatchback'),
        ]
        
        for vtype_id, vclass, accel, decel, shape in traffic_vtypes:
            vtype = ET.SubElement(root, 'vType')
            vtype.set('id', vtype_id)
            vtype.set('vClass', vclass)
            vtype.set('accel', str(accel))
            vtype.set('decel', str(decel))
            vtype.set('sigma', '0.5')
            vtype.set('length', '4.5')
            vtype.set('maxSpeed', '50')
            vtype.set('guiShape', shape)
        
        # Write to file
        self._write_xml(root, output_path)
        
        logger.info(f"SUMO vehicle types generated: {output_path}")
        
        return str(output_path)
    
    def export_routes(
        self,
        scenario: SimulationScenario,
        filename: Optional[str] = None
    ) -> str:
        """
        Export route definitions.
        
        Args:
            scenario: Simulation scenario
            filename: Output filename (default: scenario_id.rou.xml)
            
        Returns:
            Path to generated file
        """
        if filename is None:
            filename = f"{scenario.scenario_id}.rou.xml"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating SUMO routes: {output_path}")
        
        # Create XML structure
        root = ET.Element('routes')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/routes_file.xsd')
        
        # Define route for ego vehicle
        route = ET.SubElement(root, 'route')
        route.set('id', 'ego_route')
        # Note: In real scenario, this would be actual edge IDs from the network
        route.set('edges', 'edge1 edge2 edge3 edge4 edge5')
        
        # Define ego vehicle
        vehicle = ET.SubElement(root, 'vehicle')
        vehicle.set('id', 'ego')
        vehicle.set('type', f'ego_{scenario.ego_vehicle.model}')
        vehicle.set('route', 'ego_route')
        vehicle.set('depart', '0')
        vehicle.set('departLane', 'best')
        vehicle.set('departSpeed', 'max')
        vehicle.set('color', '0,255,0')
        
        # Add traffic vehicles with varying departure times
        traffic_config = self._get_traffic_config(scenario.traffic)
        
        for i in range(traffic_config['num_vehicles']):
            traffic_vehicle = ET.SubElement(root, 'vehicle')
            traffic_vehicle.set('id', f'traffic_{i}')
            traffic_vehicle.set('type', f'passenger_car')
            traffic_vehicle.set('route', 'ego_route')
            traffic_vehicle.set('depart', str(i * 2))  # Stagger departures
            traffic_vehicle.set('departLane', 'random')
            traffic_vehicle.set('departSpeed', 'random')
        
        # Add traffic flow (continuous generation)
        flow = ET.SubElement(root, 'flow')
        flow.set('id', 'traffic_flow')
        flow.set('type', 'passenger_car')
        flow.set('route', 'ego_route')
        flow.set('begin', '0')
        flow.set('end', str(scenario.duration_seconds))
        flow.set('vehsPerHour', str(traffic_config['flow_rate']))
        flow.set('departLane', 'best')
        flow.set('departSpeed', 'max')
        
        # Write to file
        self._write_xml(root, output_path)
        
        logger.info(f"SUMO routes generated: {output_path}")
        
        return str(output_path)
    
    def export_config(
        self,
        scenario: SimulationScenario,
        network_file: str,
        vtype_file: str,
        route_file: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Export SUMO configuration file.
        
        Args:
            scenario: Simulation scenario
            network_file: Network file path
            vtype_file: Vehicle types file path
            route_file: Routes file path
            filename: Output filename (default: scenario_id.sumocfg)
            
        Returns:
            Path to generated file
        """
        if filename is None:
            filename = f"{scenario.scenario_id}.sumocfg"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating SUMO config: {output_path}")
        
        # Create XML structure
        root = ET.Element('configuration')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation', 'http://sumo.dlr.de/xsd/sumoConfiguration.xsd')
        
        # Input section
        input_elem = ET.SubElement(root, 'input')
        
        net_file = ET.SubElement(input_elem, 'net-file')
        net_file.set('value', network_file)
        
        route_files = ET.SubElement(input_elem, 'route-files')
        route_files.set('value', f'{Path(vtype_file).name},{Path(route_file).name}')
        
        # Time section
        time_elem = ET.SubElement(root, 'time')
        
        begin = ET.SubElement(time_elem, 'begin')
        begin.set('value', '0')
        
        end = ET.SubElement(time_elem, 'end')
        end.set('value', str(scenario.duration_seconds))
        
        step_length = ET.SubElement(time_elem, 'step-length')
        step_length.set('value', '0.1')
        
        # Processing section
        processing = ET.SubElement(root, 'processing')
        
        collision_action = ET.SubElement(processing, 'collision.action')
        collision_action.set('value', 'warn')
        
        # Output section
        output = ET.SubElement(root, 'output')
        
        summary = ET.SubElement(output, 'summary-output')
        summary.set('value', f'{scenario.scenario_id}_summary.xml')
        
        tripinfo = ET.SubElement(output, 'tripinfo-output')
        tripinfo.set('value', f'{scenario.scenario_id}_tripinfo.xml')
        
        # GUI settings (optional)
        gui = ET.SubElement(root, 'gui_only')
        
        start_gui = ET.SubElement(gui, 'start')
        start_gui.set('value', 'true')
        
        quit_on_end = ET.SubElement(gui, 'quit-on-end')
        quit_on_end.set('value', 'false')
        
        # Write to file
        self._write_xml(root, output_path)
        
        logger.info(f"SUMO config generated: {output_path}")
        
        return str(output_path)
    
    def _get_sumo_vclass(self, platform: str) -> str:
        """Map vehicle platform to SUMO vehicle class."""
        # All passenger vehicles in SUMO
        return 'passenger'
    
    def _get_traffic_config(self, traffic) -> Dict[str, Any]:
        """Map traffic scenario to SUMO parameters."""
        # Map density to flow rate (vehicles per hour)
        density_map = {
            TrafficDensity.EMPTY: 0,
            TrafficDensity.LOW: 300,
            TrafficDensity.MEDIUM: 1000,
            TrafficDensity.HIGH: 2000,
            TrafficDensity.VERY_HIGH: 3000
        }
        
        return {
            'num_vehicles': traffic.num_vehicles,
            'flow_rate': density_map.get(traffic.density, 1000)
        }
    
    def _write_xml(self, root: ET.Element, output_path: Path) -> None:
        """Write XML element to file with pretty formatting."""
        # Convert to string
        xml_str = ET.tostring(root, encoding='utf-8')
        
        # Pretty print
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='    ', encoding='utf-8')
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(pretty_xml)
    
    def export_batch(
        self,
        scenarios: List[SimulationScenario],
        network_file: str = "Town01.net.xml"
    ) -> Dict[str, Dict[str, str]]:
        """
        Export multiple scenarios.
        
        Args:
            scenarios: List of simulation scenarios
            network_file: SUMO network file to use
            
        Returns:
            Dictionary mapping scenario IDs to generated file paths
        """
        logger.info(f"Exporting {len(scenarios)} scenarios to SUMO format...")
        
        exported = {}
        
        for scenario in scenarios:
            try:
                files = self.export_scenario(scenario, network_file)
                exported[scenario.scenario_id] = files
            
            except Exception as e:
                logger.error(f"Failed to export scenario {scenario.scenario_id}: {e}")
        
        logger.info(f"Exported {len(exported)}/{len(scenarios)} scenarios")
        
        return exported


def create_sumo_exporter(output_dir: str = "sim_output/sumo") -> SUMOExporter:
    """
    Create a SUMO exporter instance.
    
    Args:
        output_dir: Directory for output files
        
    Returns:
        SUMOExporter instance
    """
    return SUMOExporter(output_dir=output_dir)

