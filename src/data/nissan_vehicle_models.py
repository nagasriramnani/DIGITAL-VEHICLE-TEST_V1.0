"""
Nissan vehicle models, platforms, and component definitions.
Represents realistic vehicle architectures for EV, HEV, and ICE platforms.
"""
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


class Platform(str, Enum):
    """Vehicle platform types."""
    EV = "EV"  # Battery Electric Vehicle
    HEV = "HEV"  # Hybrid Electric Vehicle
    ICE = "ICE"  # Internal Combustion Engine


class VehicleSystem(str, Enum):
    """Major vehicle systems."""
    POWERTRAIN = "Powertrain"
    BATTERY = "Battery"
    ADAS = "ADAS"
    CHASSIS = "Chassis"
    HVAC = "HVAC"
    INFOTAINMENT = "Infotainment"
    ELECTRICAL = "Electrical"
    BODY = "Body"
    THERMAL = "Thermal"


@dataclass
class VehicleComponent:
    """Represents a vehicle component."""
    name: str
    system: VehicleSystem
    applicable_platforms: Set[Platform]
    criticality: str  # "critical", "high", "medium", "low"
    
    def __hash__(self):
        return hash(self.name)


# Nissan Vehicle Models mapped to platforms
NISSAN_MODELS: Dict[str, Platform] = {
    # EV Models
    "Ariya": Platform.EV,
    "Leaf": Platform.EV,
    
    # HEV Models
    "Qashqai_epower": Platform.HEV,
    "X-Trail_epower": Platform.HEV,
    
    # ICE Models
    "Qashqai": Platform.ICE,
    "X-Trail": Platform.ICE,
    "Juke": Platform.ICE,
    "Micra": Platform.ICE,
}


# Component Database - Organized by System
COMPONENTS: List[VehicleComponent] = [
    # Powertrain Components
    VehicleComponent("Electric_Motor", VehicleSystem.POWERTRAIN, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("Inverter", VehicleSystem.POWERTRAIN, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("Reducer_Gearbox", VehicleSystem.POWERTRAIN, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("ICE_Engine", VehicleSystem.POWERTRAIN, {Platform.ICE, Platform.HEV}, "critical"),
    VehicleComponent("Transmission_CVT", VehicleSystem.POWERTRAIN, {Platform.ICE}, "critical"),
    VehicleComponent("Transmission_Auto", VehicleSystem.POWERTRAIN, {Platform.ICE, Platform.HEV}, "critical"),
    VehicleComponent("Fuel_System", VehicleSystem.POWERTRAIN, {Platform.ICE, Platform.HEV}, "high"),
    VehicleComponent("Exhaust_System", VehicleSystem.POWERTRAIN, {Platform.ICE, Platform.HEV}, "high"),
    VehicleComponent("Turbocharger", VehicleSystem.POWERTRAIN, {Platform.ICE, Platform.HEV}, "medium"),
    
    # Battery System Components
    VehicleComponent("High_Voltage_Battery", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("Battery_Management_System", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("Charging_Port", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "high"),
    VehicleComponent("DC_DC_Converter", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "high"),
    VehicleComponent("Onboard_Charger", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "high"),
    VehicleComponent("Battery_Thermal_Management", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("12V_Battery", VehicleSystem.BATTERY, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    
    # ADAS Components
    VehicleComponent("Forward_Camera", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Radar_Front", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Radar_Rear", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Lidar", VehicleSystem.ADAS, {Platform.EV}, "high"),
    VehicleComponent("Ultrasonic_Sensors", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("ADAS_ECU", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Lane_Keep_Assist", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Adaptive_Cruise_Control", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Emergency_Brake_System", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Blind_Spot_Monitor", VehicleSystem.ADAS, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    
    # Chassis Components
    VehicleComponent("Brake_System_Hydraulic", VehicleSystem.CHASSIS, {Platform.ICE}, "critical"),
    VehicleComponent("Brake_System_Regenerative", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV}, "critical"),
    VehicleComponent("Electronic_Stability_Control", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Power_Steering", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Front_Suspension", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Rear_Suspension", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Traction_Control", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("ABS_Module", VehicleSystem.CHASSIS, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    
    # HVAC Components
    VehicleComponent("HVAC_System", VehicleSystem.HVAC, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Heat_Pump", VehicleSystem.HVAC, {Platform.EV, Platform.HEV}, "high"),
    VehicleComponent("Climate_Control_ECU", VehicleSystem.HVAC, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("Cabin_Air_Filter", VehicleSystem.HVAC, {Platform.EV, Platform.HEV, Platform.ICE}, "low"),
    
    # Infotainment Components
    VehicleComponent("Head_Unit", VehicleSystem.INFOTAINMENT, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("Navigation_System", VehicleSystem.INFOTAINMENT, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("Connectivity_Module", VehicleSystem.INFOTAINMENT, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("Instrument_Cluster", VehicleSystem.INFOTAINMENT, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("HMI_Touchscreen", VehicleSystem.INFOTAINMENT, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    
    # Electrical/Electronic Architecture
    VehicleComponent("CAN_Bus", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Gateway_ECU", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Body_Control_Module", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Wiring_Harness", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Power_Distribution_Unit", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("OTA_Update_Module", VehicleSystem.ELECTRICAL, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    
    # Body Components
    VehicleComponent("Airbag_System", VehicleSystem.BODY, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Seatbelt_Pretensioners", VehicleSystem.BODY, {Platform.EV, Platform.HEV, Platform.ICE}, "critical"),
    VehicleComponent("Lighting_System", VehicleSystem.BODY, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("Door_Locks", VehicleSystem.BODY, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    VehicleComponent("Power_Windows", VehicleSystem.BODY, {Platform.EV, Platform.HEV, Platform.ICE}, "medium"),
    
    # Thermal Management
    VehicleComponent("Radiator", VehicleSystem.THERMAL, {Platform.ICE, Platform.HEV}, "high"),
    VehicleComponent("Coolant_System", VehicleSystem.THERMAL, {Platform.EV, Platform.HEV, Platform.ICE}, "high"),
    VehicleComponent("EV_Thermal_System", VehicleSystem.THERMAL, {Platform.EV, Platform.HEV}, "critical"),
]


def get_components_for_platform(platform: Platform) -> List[VehicleComponent]:
    """Return all components applicable to a given platform."""
    return [c for c in COMPONENTS if platform in c.applicable_platforms]


def get_components_by_system(system: VehicleSystem, platform: Platform = None) -> List[VehicleComponent]:
    """Return components for a specific system, optionally filtered by platform."""
    components = [c for c in COMPONENTS if c.system == system]
    if platform:
        components = [c for c in components if platform in c.applicable_platforms]
    return components


def get_critical_components(platform: Platform = None) -> List[VehicleComponent]:
    """Return all critical components, optionally filtered by platform."""
    components = [c for c in COMPONENTS if c.criticality == "critical"]
    if platform:
        components = [c for c in components if platform in c.applicable_platforms]
    return components


def get_platform_for_model(model_name: str) -> Platform:
    """Get the platform type for a given vehicle model."""
    return NISSAN_MODELS.get(model_name, Platform.ICE)


def get_models_by_platform(platform: Platform) -> List[str]:
    """Get all vehicle models for a given platform."""
    return [model for model, plat in NISSAN_MODELS.items() if plat == platform]


if __name__ == "__main__":
    # Test the vehicle model definitions
    print("=" * 60)
    print("NISSAN VEHICLE MODELS & COMPONENTS")
    print("=" * 60)
    
    for platform in Platform:
        models = get_models_by_platform(platform)
        components = get_components_for_platform(platform)
        critical = get_critical_components(platform)
        
        print(f"\n{platform.value} Platform:")
        print(f"  Models: {', '.join(models)}")
        print(f"  Total Components: {len(components)}")
        print(f"  Critical Components: {len(critical)}")
        
        # Show component breakdown by system
        systems_breakdown = {}
        for comp in components:
            systems_breakdown[comp.system.value] = systems_breakdown.get(comp.system.value, 0) + 1
        
        print(f"  Component Distribution:")
        for system, count in sorted(systems_breakdown.items()):
            print(f"    - {system}: {count}")
    
    print(f"\n[OK] Total unique components defined: {len(COMPONENTS)}")
    print(f"[OK] Total vehicle models: {len(NISSAN_MODELS)}")

