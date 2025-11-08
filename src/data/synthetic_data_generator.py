"""
Synthetic test scenario generator for Nissan VTA.
Generates realistic test scenarios across multiple categories with proper constraints.
"""
import json
import random
import uuid
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add project root to Python path to allow imports
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.data.nissan_vehicle_models import (
    NISSAN_MODELS, COMPONENTS, Platform, VehicleSystem,
    get_components_for_platform, get_components_by_system
)


@dataclass
class EnvironmentalConditions:
    """Environmental test conditions."""
    temperature_celsius: float
    humidity_percent: float
    altitude_meters: float
    road_surface: str  # "dry", "wet", "snow", "ice", "gravel"
    weather: str  # "clear", "rain", "snow", "fog"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VehicleLoadProfile:
    """Vehicle loading and operational profile."""
    load_percent: float  # 0-100
    speed_profile: str  # "urban", "highway", "mixed", "sport", "eco"
    driver_behavior: str  # "normal", "aggressive", "conservative"
    duration_hours: float
    distance_km: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HistoricalTestResult:
    """Historical test execution result."""
    test_id: str
    execution_date: str
    passed: bool
    failure_mode: Optional[str]
    fix_hours: float
    engineer_notes: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestScenario:
    """Complete test scenario definition."""
    scenario_id: str
    test_name: str
    test_type: str  # "performance", "durability", "safety", "regulatory", "adas", "emissions"
    description: str
    
    # Vehicle Context
    applicable_models: List[str]
    applicable_platforms: List[str]
    target_components: List[str]
    target_systems: List[str]
    
    # Test Parameters
    environmental_conditions: EnvironmentalConditions
    load_profile: VehicleLoadProfile
    test_steps: List[str]
    
    # Regulatory & Standards
    regulatory_standards: List[str]
    certification_required: bool
    
    # Resource Estimation
    estimated_duration_hours: float
    estimated_cost_gbp: float
    required_equipment: List[str]
    required_personnel: int
    facility_type: str  # "lab", "test_track", "climatic_chamber", "emc_chamber", "proving_ground"
    
    # Risk & Complexity
    complexity_score: int  # 1-10
    risk_level: str  # "low", "medium", "high", "critical"
    
    # Historical Context
    execution_count: int
    historical_results: List[HistoricalTestResult]
    
    # Metadata
    created_date: str
    last_updated: str
    version: str
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["environmental_conditions"] = self.environmental_conditions.to_dict()
        data["load_profile"] = self.load_profile.to_dict()
        data["historical_results"] = [hr.to_dict() for hr in self.historical_results]
        return data


class SyntheticDataGenerator:
    """Generates synthetic test scenarios with realistic constraints."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Regulatory standards by platform and system
        self.regulatory_standards = {
            (Platform.EV, VehicleSystem.BATTERY): ["UNECE_R100", "ISO_6469", "SAE_J2929", "IEC_62660"],
            (Platform.EV, VehicleSystem.POWERTRAIN): ["ISO_8854", "SAE_J1772", "IEC_61851"],
            (Platform.EV, VehicleSystem.ADAS): ["UNECE_R157", "ISO_26262", "NCAP_AEB_2023"],
            (Platform.HEV, VehicleSystem.BATTERY): ["UNECE_R100", "ISO_6469"],
            (Platform.HEV, VehicleSystem.POWERTRAIN): ["WLTP_Class3b", "EPA_FTP75", "EURO_6E"],
            (Platform.ICE, VehicleSystem.POWERTRAIN): ["WLTP_Class3b", "EPA_FTP75", "EURO_6E", "RDE"],
            (Platform.ICE, VehicleSystem.CHASSIS): ["UNECE_R13H", "FMVSS_135"],
            "emissions": ["WLTP", "RDE", "EURO_6E", "LEV_III"],
            "safety": ["NCAP_5Star", "FMVSS_208", "UNECE_R94", "ISO_26262_ASIL_D"],
            "adas": ["UNECE_R157", "NCAP_AEB_Urban", "NCAP_AEB_InterUrban", "ISO_26262"],
        }
        
        # Test type templates
        self.test_templates = {
            "performance": self._generate_performance_test,
            "durability": self._generate_durability_test,
            "safety": self._generate_safety_test,
            "regulatory": self._generate_regulatory_test,
            "adas": self._generate_adas_test,
            "emissions": self._generate_emissions_test,
        }
    
    def generate_scenarios(self, target_count: int = 500) -> List[TestScenario]:
        """Generate a diverse set of test scenarios."""
        scenarios = []
        
        # Distribution across test types
        type_distribution = {
            "performance": 0.20,
            "durability": 0.25,
            "safety": 0.20,
            "regulatory": 0.15,
            "adas": 0.15,
            "emissions": 0.05,
        }
        
        for test_type, proportion in type_distribution.items():
            count = int(target_count * proportion)
            generator_func = self.test_templates[test_type]
            
            for _ in range(count):
                scenario = generator_func()
                scenarios.append(scenario)
        
        return scenarios
    
    def _generate_performance_test(self) -> TestScenario:
        """Generate a performance test scenario."""
        model = random.choice(list(NISSAN_MODELS.keys()))
        platform = NISSAN_MODELS[model]
        
        # Select relevant components
        if platform == Platform.EV:
            system = random.choice([VehicleSystem.POWERTRAIN, VehicleSystem.BATTERY, VehicleSystem.THERMAL])
        else:
            system = random.choice([VehicleSystem.POWERTRAIN, VehicleSystem.CHASSIS])
        
        components = get_components_by_system(system, platform)
        target_components = random.sample([c.name for c in components], k=min(3, len(components)))
        
        test_names = [
            "Acceleration_0_100_kph",
            "Top_Speed_Measurement",
            "Power_Output_Validation",
            "Thermal_Performance_Under_Load",
            "Energy_Efficiency_Test",
            "Motor_Torque_Curve_Validation",
            "Battery_Discharge_Profile",
            "Regenerative_Braking_Efficiency",
        ]
        
        test_name = random.choice(test_names)
        
        env_conditions = self._generate_environmental_conditions()
        load_profile = self._generate_load_profile("sport" if "Acceleration" in test_name else "mixed")
        
        steps = [
            f"Prepare {model} with instrumentation",
            f"Verify {', '.join(target_components[:2])} functionality",
            f"Execute {test_name} protocol",
            "Record performance metrics",
            "Validate against specification",
        ]
        
        standards = self._get_regulatory_standards(platform, system)
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}_{system.value}",
            test_type="performance",
            description=f"Validate {system.value} performance characteristics for {model} under specified conditions",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[system.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=standards[:2] if standards else [],
            certification_required=random.choice([True, False]),
            estimated_duration_hours=np.random.lognormal(2.0, 0.5),
            estimated_cost_gbp=np.random.lognormal(7.5, 0.8),
            required_equipment=self._get_required_equipment("performance"),
            required_personnel=random.randint(2, 4),
            facility_type=random.choice(["test_track", "lab", "proving_ground"]),
            complexity_score=random.randint(4, 8),
            risk_level=random.choice(["low", "medium", "high"]),
            execution_count=random.randint(0, 15),
            historical_results=self._generate_historical_results(random.randint(0, 5)),
            created_date=self._random_date(days_ago=180),
            last_updated=self._random_date(days_ago=30),
            version="1.0",
            tags=[platform.value, system.value, "performance", model],
        )
    
    def _generate_durability_test(self) -> TestScenario:
        """Generate a durability/endurance test scenario."""
        model = random.choice(list(NISSAN_MODELS.keys()))
        platform = NISSAN_MODELS[model]
        
        system = random.choice(list(VehicleSystem))
        components = get_components_by_system(system, platform)
        
        if not components:
            components = get_components_for_platform(platform)
            system = components[0].system if components else VehicleSystem.POWERTRAIN
        
        target_components = random.sample([c.name for c in components], k=min(2, len(components)))
        
        test_names = [
            "Lifecycle_Endurance_100k_km",
            "Thermal_Cycling_Test",
            "Vibration_Durability",
            "Corrosion_Resistance",
            "Component_Fatigue_Test",
            "Extended_Load_Durability",
            "Environmental_Stress_Screening",
        ]
        
        test_name = random.choice(test_names)
        
        env_conditions = self._generate_environmental_conditions(extreme=True)
        load_profile = self._generate_load_profile("mixed", duration_multiplier=10)
        
        steps = [
            f"Mount {model} on test rig",
            f"Install sensors on {', '.join(target_components)}",
            "Execute durability cycle protocol",
            "Monitor for failures and degradation",
            "Perform teardown inspection",
            "Document wear patterns",
        ]
        
        standards = self._get_regulatory_standards(platform, system)
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}_{system.value}",
            test_type="durability",
            description=f"Long-term durability validation of {system.value} components for {model}",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[system.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=standards[:1] if standards else [],
            certification_required=random.choice([True, False]),
            estimated_duration_hours=np.random.lognormal(4.0, 0.7),
            estimated_cost_gbp=np.random.lognormal(9.0, 0.9),
            required_equipment=self._get_required_equipment("durability"),
            required_personnel=random.randint(3, 6),
            facility_type=random.choice(["lab", "climatic_chamber", "proving_ground"]),
            complexity_score=random.randint(6, 10),
            risk_level=random.choice(["medium", "high"]),
            execution_count=random.randint(0, 8),
            historical_results=self._generate_historical_results(random.randint(0, 3)),
            created_date=self._random_date(days_ago=365),
            last_updated=self._random_date(days_ago=60),
            version="1.0",
            tags=[platform.value, system.value, "durability", "long_term", model],
        )
    
    def _generate_safety_test(self) -> TestScenario:
        """Generate a safety test scenario."""
        model = random.choice(list(NISSAN_MODELS.keys()))
        platform = NISSAN_MODELS[model]
        
        system = random.choice([VehicleSystem.CHASSIS, VehicleSystem.BODY, VehicleSystem.ADAS])
        components = get_components_by_system(system, platform)
        target_components = random.sample([c.name for c in components], k=min(3, len(components)))
        
        test_names = [
            "Frontal_Impact_Test",
            "Side_Impact_Test",
            "Rollover_Stability",
            "Airbag_Deployment_Validation",
            "Seatbelt_Load_Test",
            "Emergency_Braking_Performance",
            "Pedestrian_Protection",
        ]
        
        test_name = random.choice(test_names)
        
        env_conditions = self._generate_environmental_conditions()
        load_profile = self._generate_load_profile("normal")
        
        steps = [
            "Prepare test vehicle with crash dummies",
            "Install impact sensors and cameras",
            f"Execute {test_name} protocol",
            "Measure deceleration and intrusion",
            "Assess occupant injury criteria",
            "Generate safety rating report",
        ]
        
        standards = self.regulatory_standards.get("safety", [])
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}",
            test_type="safety",
            description=f"Safety validation test: {test_name} for {model}",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[system.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=random.sample(standards, k=min(3, len(standards))),
            certification_required=True,
            estimated_duration_hours=np.random.lognormal(2.5, 0.6),
            estimated_cost_gbp=np.random.lognormal(10.0, 1.0),
            required_equipment=self._get_required_equipment("safety"),
            required_personnel=random.randint(4, 8),
            facility_type="test_track",
            complexity_score=random.randint(7, 10),
            risk_level="critical",
            execution_count=random.randint(0, 5),
            historical_results=self._generate_historical_results(random.randint(0, 2)),
            created_date=self._random_date(days_ago=400),
            last_updated=self._random_date(days_ago=90),
            version="1.0",
            tags=[platform.value, "safety", "certification", model],
        )
    
    def _generate_regulatory_test(self) -> TestScenario:
        """Generate a regulatory compliance test scenario."""
        model = random.choice(list(NISSAN_MODELS.keys()))
        platform = NISSAN_MODELS[model]
        
        if platform == Platform.EV:
            system = random.choice([VehicleSystem.BATTERY, VehicleSystem.ADAS, VehicleSystem.ELECTRICAL])
        elif platform == Platform.HEV:
            system = random.choice([VehicleSystem.BATTERY, VehicleSystem.POWERTRAIN])
        else:
            system = random.choice([VehicleSystem.POWERTRAIN, VehicleSystem.CHASSIS])
        
        components = get_components_by_system(system, platform)
        target_components = [c.name for c in components[:3]]
        
        standards = self._get_regulatory_standards(platform, system)
        test_name = f"Regulatory_Compliance_{standards[0] if standards else 'Generic'}"
        
        env_conditions = self._generate_environmental_conditions()
        load_profile = self._generate_load_profile("regulatory")
        
        steps = [
            f"Configure {model} per regulatory specification",
            f"Calibrate measurement equipment for {standards[0] if standards else 'test'}",
            "Execute standardized test protocol",
            "Record all required parameters",
            "Generate compliance report",
            "Submit for certification",
        ]
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}",
            test_type="regulatory",
            description=f"Regulatory compliance testing for {model} against {standards[0] if standards else 'standards'}",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[system.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=standards,
            certification_required=True,
            estimated_duration_hours=np.random.lognormal(3.0, 0.5),
            estimated_cost_gbp=np.random.lognormal(8.5, 0.8),
            required_equipment=self._get_required_equipment("regulatory"),
            required_personnel=random.randint(3, 5),
            facility_type=random.choice(["lab", "test_track", "emc_chamber"]),
            complexity_score=random.randint(6, 9),
            risk_level="high",
            execution_count=random.randint(1, 10),
            historical_results=self._generate_historical_results(random.randint(1, 4)),
            created_date=self._random_date(days_ago=300),
            last_updated=self._random_date(days_ago=45),
            version="1.0",
            tags=[platform.value, system.value, "regulatory", "compliance", model],
        )
    
    def _generate_adas_test(self) -> TestScenario:
        """Generate an ADAS test scenario."""
        model = random.choice(list(NISSAN_MODELS.keys()))
        platform = NISSAN_MODELS[model]
        
        components = get_components_by_system(VehicleSystem.ADAS, platform)
        target_components = [c.name for c in components[:4]]
        
        test_names = [
            "AEB_Urban_Scenario",
            "AEB_InterUrban_Scenario",
            "Lane_Keep_Assist_Validation",
            "Adaptive_Cruise_Control_Test",
            "Blind_Spot_Detection",
            "Parking_Assist_Validation",
            "Traffic_Sign_Recognition",
        ]
        
        test_name = random.choice(test_names)
        
        env_conditions = self._generate_environmental_conditions()
        load_profile = self._generate_load_profile("urban")
        
        steps = [
            f"Configure {model} ADAS systems",
            "Set up target vehicles/obstacles",
            f"Execute {test_name} scenario",
            "Measure system response times",
            "Validate intervention accuracy",
            "Document edge cases",
        ]
        
        standards = self.regulatory_standards.get("adas", [])
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}",
            test_type="adas",
            description=f"ADAS functionality test: {test_name} for {model}",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[VehicleSystem.ADAS.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=random.sample(standards, k=min(2, len(standards))),
            certification_required=True,
            estimated_duration_hours=np.random.lognormal(2.2, 0.5),
            estimated_cost_gbp=np.random.lognormal(8.0, 0.7),
            required_equipment=self._get_required_equipment("adas"),
            required_personnel=random.randint(3, 5),
            facility_type="test_track",
            complexity_score=random.randint(6, 9),
            risk_level=random.choice(["medium", "high"]),
            execution_count=random.randint(2, 12),
            historical_results=self._generate_historical_results(random.randint(1, 5)),
            created_date=self._random_date(days_ago=250),
            last_updated=self._random_date(days_ago=20),
            version="1.0",
            tags=[platform.value, "adas", "active_safety", model],
        )
    
    def _generate_emissions_test(self) -> TestScenario:
        """Generate an emissions test scenario."""
        # Emissions mainly for ICE and HEV
        platform = random.choice([Platform.ICE, Platform.HEV])
        models = [m for m, p in NISSAN_MODELS.items() if p == platform]
        model = random.choice(models) if models else "Qashqai"
        
        components = get_components_by_system(VehicleSystem.POWERTRAIN, platform)
        target_components = [c.name for c in components[:3]]
        
        test_names = [
            "WLTP_Cycle",
            "RDE_Real_Driving_Emissions",
            "Cold_Start_Emissions",
            "Evaporative_Emissions",
            "OBD_Emissions_Monitoring",
        ]
        
        test_name = random.choice(test_names)
        
        env_conditions = self._generate_environmental_conditions()
        load_profile = self._generate_load_profile("regulatory")
        
        steps = [
            "Precondition vehicle per WLTP/RDE protocol",
            "Install PEMS (Portable Emissions Measurement System)",
            f"Execute {test_name} drive cycle",
            "Measure CO2, NOx, PM, HC emissions",
            "Calculate conformity factor",
            "Generate emissions certificate",
        ]
        
        standards = self.regulatory_standards.get("emissions", [])
        
        return TestScenario(
            scenario_id=str(uuid.uuid4()),
            test_name=f"{model}_{test_name}",
            test_type="emissions",
            description=f"Emissions compliance test: {test_name} for {model}",
            applicable_models=[model],
            applicable_platforms=[platform.value],
            target_components=target_components,
            target_systems=[VehicleSystem.POWERTRAIN.value],
            environmental_conditions=env_conditions,
            load_profile=load_profile,
            test_steps=steps,
            regulatory_standards=random.sample(standards, k=min(3, len(standards))),
            certification_required=True,
            estimated_duration_hours=np.random.lognormal(2.8, 0.6),
            estimated_cost_gbp=np.random.lognormal(8.8, 0.8),
            required_equipment=self._get_required_equipment("emissions"),
            required_personnel=random.randint(2, 4),
            facility_type=random.choice(["lab", "test_track"]),
            complexity_score=random.randint(7, 9),
            risk_level="high",
            execution_count=random.randint(3, 15),
            historical_results=self._generate_historical_results(random.randint(2, 6)),
            created_date=self._random_date(days_ago=350),
            last_updated=self._random_date(days_ago=50),
            version="1.0",
            tags=[platform.value, "emissions", "regulatory", model],
        )
    
    def _generate_environmental_conditions(self, extreme: bool = False) -> EnvironmentalConditions:
        """Generate realistic environmental conditions."""
        if extreme:
            temp = random.choice([
                np.random.uniform(-40, -20),
                np.random.uniform(40, 55)
            ])
        else:
            temp = np.random.uniform(-20, 50)
        
        return EnvironmentalConditions(
            temperature_celsius=round(temp, 1),
            humidity_percent=round(np.random.uniform(10, 95), 1),
            altitude_meters=round(random.choice([0, 100, 500, 1000, 2000]), 0),
            road_surface=random.choice(["dry", "wet", "wet", "snow", "ice", "gravel"]),
            weather=random.choice(["clear", "clear", "rain", "snow", "fog"]),
        )
    
    def _generate_load_profile(
        self, 
        profile_type: str, 
        duration_multiplier: float = 1.0
    ) -> VehicleLoadProfile:
        """Generate vehicle load profile."""
        profiles = {
            "urban": {"speed": "urban", "load": (20, 60), "duration": (1, 4), "distance": (10, 50)},
            "highway": {"speed": "highway", "load": (50, 90), "duration": (2, 6), "distance": (100, 300)},
            "mixed": {"speed": "mixed", "load": (30, 80), "duration": (2, 8), "distance": (50, 200)},
            "sport": {"speed": "sport", "load": (70, 100), "duration": (0.5, 2), "distance": (10, 50)},
            "eco": {"speed": "eco", "load": (10, 50), "duration": (2, 6), "distance": (50, 150)},
            "regulatory": {"speed": "mixed", "load": (40, 70), "duration": (1, 3), "distance": (23, 120)},
            "normal": {"speed": "mixed", "load": (30, 70), "duration": (1, 4), "distance": (20, 100)},
        }
        
        config = profiles.get(profile_type, profiles["normal"])
        
        return VehicleLoadProfile(
            load_percent=round(np.random.uniform(*config["load"]), 1),
            speed_profile=config["speed"],
            driver_behavior=random.choice(["normal", "normal", "aggressive", "conservative"]),
            duration_hours=round(np.random.uniform(*config["duration"]) * duration_multiplier, 2),
            distance_km=round(np.random.uniform(*config["distance"]) * duration_multiplier, 1),
        )
    
    def _get_regulatory_standards(self, platform: Platform, system: VehicleSystem) -> List[str]:
        """Get applicable regulatory standards."""
        standards = self.regulatory_standards.get((platform, system), [])
        if not standards:
            # Fallback to general standards
            if system == VehicleSystem.ADAS:
                standards = self.regulatory_standards.get("adas", [])
        return standards
    
    def _get_required_equipment(self, test_type: str) -> List[str]:
        """Get required equipment based on test type."""
        equipment_db = {
            "performance": ["Dynamometer", "Data_Logger", "Speed_Sensor", "Power_Analyzer"],
            "durability": ["Vibration_Rig", "Climatic_Chamber", "Data_Logger", "Torque_Sensor"],
            "safety": ["Crash_Dummies", "High_Speed_Cameras", "Deceleration_Sled", "Force_Sensors"],
            "regulatory": ["Calibrated_Instruments", "PEMS", "Chassis_Dyno", "Data_Logger"],
            "adas": ["Target_Vehicles", "GNSS_RTK", "Sensor_Targets", "Data_Logger"],
            "emissions": ["PEMS", "Gas_Analyzer", "Chassis_Dyno", "Weather_Station"],
        }
        
        base_equipment = equipment_db.get(test_type, ["Data_Logger"])
        return random.sample(base_equipment, k=min(random.randint(2, 4), len(base_equipment)))
    
    def _generate_historical_results(self, count: int) -> List[HistoricalTestResult]:
        """Generate historical test execution results."""
        results = []
        
        failure_modes = [
            "Component_Failure", "Out_of_Spec", "Software_Bug", "Sensor_Drift",
            "Calibration_Error", "Environmental_Interference", None
        ]
        
        for i in range(count):
            passed = random.random() > 0.25  # 75% pass rate
            failure = None if passed else random.choice(failure_modes[:-1])
            
            results.append(HistoricalTestResult(
                test_id=str(uuid.uuid4()),
                execution_date=self._random_date(days_ago=random.randint(30, 700)),
                passed=passed,
                failure_mode=failure,
                fix_hours=0.0 if passed else round(np.random.lognormal(2.5, 1.0), 1),
                engineer_notes=f"Test {'passed' if passed else 'failed'} - {failure if failure else 'nominal performance'}",
            ))
        
        return results
    
    def _random_date(self, days_ago: int) -> str:
        """Generate a random date in the past."""
        date = datetime.now() - timedelta(days=random.randint(0, days_ago))
        return date.strftime("%Y-%m-%d")
    
    def save_to_json(self, scenarios: List[TestScenario], output_path: str) -> None:
        """Save scenarios to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "generator_version": "1.0",
                "scenario_count": len(scenarios),
                "seed": self.seed,
            },
            "scenarios": [s.to_dict() for s in scenarios]
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Generated {len(scenarios)} scenarios -> {output_path}")


def main():
    """Generate synthetic test scenarios."""
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate 500 scenarios (can be adjusted)
    scenarios = generator.generate_scenarios(target_count=500)
    
    # Save to file
    output_path = "src/data/test_scenarios.json"
    generator.save_to_json(scenarios, output_path)
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("SYNTHETIC DATA GENERATION SUMMARY")
    print("=" * 60)
    
    by_type = {}
    by_platform = {}
    for s in scenarios:
        by_type[s.test_type] = by_type.get(s.test_type, 0) + 1
        for p in s.applicable_platforms:
            by_platform[p] = by_platform.get(p, 0) + 1
    
    print(f"\nTotal Scenarios: {len(scenarios)}")
    print(f"\nBy Test Type:")
    for test_type, count in sorted(by_type.items()):
        print(f"  {test_type:15s}: {count:4d}")
    
    print(f"\nBy Platform:")
    for platform, count in sorted(by_platform.items()):
        print(f"  {platform:15s}: {count:4d}")
    
    # Cost and duration stats
    total_duration = sum(s.estimated_duration_hours for s in scenarios)
    total_cost = sum(s.estimated_cost_gbp for s in scenarios)
    
    print(f"\nResource Estimates:")
    print(f"  Total Test Duration: {total_duration:,.0f} hours")
    print(f"  Total Estimated Cost: £{total_cost:,.0f}")
    print(f"  Avg Duration/Test:   {total_duration/len(scenarios):.1f} hours")
    print(f"  Avg Cost/Test:       £{total_cost/len(scenarios):,.0f}")


if __name__ == "__main__":
    main()

