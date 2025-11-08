"""
ROI (Return on Investment) calculator for test optimization.
Calculates cost savings, time savings, and business impact metrics.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class TestCost:
    """Cost breakdown for a test scenario."""
    facility_cost_gbp: float = 0.0
    labor_cost_gbp: float = 0.0
    equipment_cost_gbp: float = 0.0
    material_cost_gbp: float = 0.0
    certification_cost_gbp: float = 0.0
    
    @property
    def total_cost_gbp(self) -> float:
        """Calculate total cost."""
        return (
            self.facility_cost_gbp +
            self.labor_cost_gbp +
            self.equipment_cost_gbp +
            self.material_cost_gbp +
            self.certification_cost_gbp
        )


@dataclass
class TestEfficiency:
    """Efficiency metrics for test execution."""
    duration_hours: float
    setup_time_hours: float = 0.0
    teardown_time_hours: float = 0.0
    
    @property
    def total_time_hours(self) -> float:
        """Calculate total time including setup and teardown."""
        return self.duration_hours + self.setup_time_hours + self.teardown_time_hours


@dataclass
class ROIAnalysis:
    """Complete ROI analysis results."""
    # Baseline (before optimization)
    baseline_num_tests: int
    baseline_total_cost_gbp: float
    baseline_total_time_hours: float
    
    # Optimized (after optimization)
    optimized_num_tests: int
    optimized_total_cost_gbp: float
    optimized_total_time_hours: float
    
    # Savings
    cost_savings_gbp: float
    time_savings_hours: float
    tests_eliminated: int
    
    # ROI metrics
    roi_percent: float
    payback_period_months: float
    
    # AI/ML investment
    implementation_cost_gbp: float = 0.0
    
    # Metadata
    analysis_date: datetime = field(default_factory=datetime.now)
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'baseline': {
                'num_tests': self.baseline_num_tests,
                'total_cost_gbp': self.baseline_total_cost_gbp,
                'total_time_hours': self.baseline_total_time_hours,
                'avg_cost_per_test_gbp': self.baseline_total_cost_gbp / self.baseline_num_tests if self.baseline_num_tests > 0 else 0
            },
            'optimized': {
                'num_tests': self.optimized_num_tests,
                'total_cost_gbp': self.optimized_total_cost_gbp,
                'total_time_hours': self.optimized_total_time_hours,
                'avg_cost_per_test_gbp': self.optimized_total_cost_gbp / self.optimized_num_tests if self.optimized_num_tests > 0 else 0
            },
            'savings': {
                'cost_savings_gbp': self.cost_savings_gbp,
                'time_savings_hours': self.time_savings_hours,
                'time_savings_days': self.time_savings_hours / 24,
                'tests_eliminated': self.tests_eliminated,
                'reduction_percent': (self.tests_eliminated / self.baseline_num_tests * 100) if self.baseline_num_tests > 0 else 0
            },
            'roi': {
                'roi_percent': self.roi_percent,
                'payback_period_months': self.payback_period_months,
                'implementation_cost_gbp': self.implementation_cost_gbp,
                'net_benefit_gbp': self.cost_savings_gbp - self.implementation_cost_gbp
            },
            'analysis_date': self.analysis_date.isoformat(),
            'notes': self.notes
        }


class ROICalculator:
    """
    Calculate ROI and business impact of test optimization.
    """
    
    def __init__(
        self,
        hourly_labor_rate_gbp: float = 75.0,
        facility_hourly_rate_gbp: float = 150.0,
        simulation_cost_factor: float = 0.05
    ):
        """
        Initialize ROI calculator.
        
        Args:
            hourly_labor_rate_gbp: Cost per hour for test engineers
            facility_hourly_rate_gbp: Cost per hour for test facilities
            simulation_cost_factor: Cost factor for simulation vs physical testing (0.05 = 5%)
        """
        self.hourly_labor_rate_gbp = hourly_labor_rate_gbp
        self.facility_hourly_rate_gbp = facility_hourly_rate_gbp
        self.simulation_cost_factor = simulation_cost_factor
    
    def estimate_test_cost(
        self,
        scenario: Dict[str, Any],
        include_certification: bool = True
    ) -> TestCost:
        """
        Estimate cost for a single test scenario.
        
        Args:
            scenario: Test scenario dictionary
            include_certification: Include certification costs
            
        Returns:
            TestCost with breakdown
        """
        # Get duration
        duration_hours = scenario.get('estimated_duration_hours', 10.0)
        
        # Estimate setup/teardown (20% of test duration)
        setup_teardown_hours = duration_hours * 0.2
        total_hours = duration_hours + setup_teardown_hours
        
        # Calculate costs
        labor_cost = total_hours * self.hourly_labor_rate_gbp * 2  # 2 engineers
        facility_cost = total_hours * self.facility_hourly_rate_gbp
        
        # Equipment cost (depends on complexity)
        complexity = scenario.get('complexity_score', 5)
        equipment_cost = complexity * 500.0  # £500 per complexity point
        
        # Material cost (test-specific)
        material_cost = 1000.0  # Default
        
        # Certification cost
        cert_cost = 0.0
        if include_certification and scenario.get('certification_required', False):
            cert_cost = 5000.0  # Fixed certification cost
        
        return TestCost(
            facility_cost_gbp=facility_cost,
            labor_cost_gbp=labor_cost,
            equipment_cost_gbp=equipment_cost,
            material_cost_gbp=material_cost,
            certification_cost_gbp=cert_cost
        )
    
    def calculate_baseline_metrics(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate baseline metrics for current test suite.
        
        Args:
            scenarios: List of test scenarios
            
        Returns:
            Dictionary with baseline metrics
        """
        total_cost = 0.0
        total_time = 0.0
        
        for scenario in scenarios:
            cost = self.estimate_test_cost(scenario)
            total_cost += cost.total_cost_gbp
            total_time += scenario.get('estimated_duration_hours', 10.0)
        
        num_tests = len(scenarios)
        
        return {
            'num_tests': num_tests,
            'total_cost_gbp': total_cost,
            'total_time_hours': total_time,
            'avg_cost_per_test_gbp': total_cost / num_tests if num_tests > 0 else 0,
            'avg_time_per_test_hours': total_time / num_tests if num_tests > 0 else 0
        }
    
    def calculate_duplicate_savings(
        self,
        duplicates: List[Dict[str, Any]],
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate savings from eliminating duplicate tests.
        
        Args:
            duplicates: List of duplicate test groups
            scenarios: Full list of test scenarios
            
        Returns:
            Dictionary with savings metrics
        """
        scenario_lookup = {s['scenario_id']: s for s in scenarios}
        
        total_cost_saved = 0.0
        total_time_saved = 0.0
        tests_eliminated = 0
        
        for dup_group in duplicates:
            # Get canonical and duplicates
            canonical_id = dup_group.get('canonical_id')
            duplicate_ids = [d['scenario_id'] for d in dup_group.get('duplicates', [])]
            
            # Calculate cost of duplicates (assuming 80% can be eliminated)
            for dup_id in duplicate_ids:
                if dup_id in scenario_lookup:
                    scenario = scenario_lookup[dup_id]
                    cost = self.estimate_test_cost(scenario)
                    total_cost_saved += cost.total_cost_gbp * 0.8  # 80% savings
                    total_time_saved += scenario.get('estimated_duration_hours', 10.0) * 0.8
                    tests_eliminated += 1
        
        return {
            'cost_saved_gbp': total_cost_saved,
            'time_saved_hours': total_time_saved,
            'tests_eliminated': tests_eliminated
        }
    
    def calculate_simulation_savings(
        self,
        scenarios_moved_to_sim: int,
        avg_physical_test_cost_gbp: float = 8000.0,
        avg_physical_test_hours: float = 24.0
    ) -> Dict[str, float]:
        """
        Calculate savings from moving tests to simulation.
        
        Args:
            scenarios_moved_to_sim: Number of scenarios moved to simulation
            avg_physical_test_cost_gbp: Average cost of physical test
            avg_physical_test_hours: Average duration of physical test
            
        Returns:
            Dictionary with simulation savings
        """
        # Simulation cost is fraction of physical
        sim_cost_per_test = avg_physical_test_cost_gbp * self.simulation_cost_factor
        sim_time_per_test = avg_physical_test_hours * 0.1  # 10% of physical time
        
        # Calculate savings
        cost_saved = (avg_physical_test_cost_gbp - sim_cost_per_test) * scenarios_moved_to_sim
        time_saved = (avg_physical_test_hours - sim_time_per_test) * scenarios_moved_to_sim
        
        return {
            'scenarios_moved': scenarios_moved_to_sim,
            'cost_saved_gbp': cost_saved,
            'time_saved_hours': time_saved,
            'cost_per_sim_test_gbp': sim_cost_per_test,
            'time_per_sim_test_hours': sim_time_per_test
        }
    
    def calculate_roi(
        self,
        baseline_scenarios: List[Dict[str, Any]],
        optimized_scenarios: List[Dict[str, Any]],
        duplicates_eliminated: List[Dict[str, Any]],
        implementation_cost_gbp: float = 50000.0,
        annual_maintenance_cost_gbp: float = 10000.0,
        analysis_period_years: int = 3
    ) -> ROIAnalysis:
        """
        Calculate comprehensive ROI analysis.
        
        Args:
            baseline_scenarios: Original test scenarios
            optimized_scenarios: Optimized test scenarios after deduplication
            duplicates_eliminated: List of eliminated duplicates
            implementation_cost_gbp: Cost to implement VTA system
            annual_maintenance_cost_gbp: Annual maintenance cost
            analysis_period_years: Period for ROI calculation
            
        Returns:
            ROIAnalysis with complete metrics
        """
        logger.info("Calculating ROI analysis...")
        
        # Calculate baseline
        baseline = self.calculate_baseline_metrics(baseline_scenarios)
        
        # Calculate optimized
        optimized = self.calculate_baseline_metrics(optimized_scenarios)
        
        # Calculate duplicate savings
        dup_savings = self.calculate_duplicate_savings(
            duplicates_eliminated,
            baseline_scenarios
        )
        
        # Calculate annual savings (assuming tests run once per year)
        annual_cost_savings = baseline['total_cost_gbp'] - optimized['total_cost_gbp']
        annual_time_savings = baseline['total_time_hours'] - optimized['total_time_hours']
        
        # Calculate multi-year benefits and costs
        total_savings = annual_cost_savings * analysis_period_years
        total_cost = implementation_cost_gbp + (annual_maintenance_cost_gbp * analysis_period_years)
        
        # Calculate ROI
        roi_percent = ((total_savings - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        # Calculate payback period
        if annual_cost_savings > 0:
            payback_months = (implementation_cost_gbp / annual_cost_savings) * 12
        else:
            payback_months = float('inf')
        
        # Create analysis
        analysis = ROIAnalysis(
            baseline_num_tests=baseline['num_tests'],
            baseline_total_cost_gbp=baseline['total_cost_gbp'],
            baseline_total_time_hours=baseline['total_time_hours'],
            optimized_num_tests=optimized['num_tests'],
            optimized_total_cost_gbp=optimized['total_cost_gbp'],
            optimized_total_time_hours=optimized['total_time_hours'],
            cost_savings_gbp=annual_cost_savings,
            time_savings_hours=annual_time_savings,
            tests_eliminated=baseline['num_tests'] - optimized['num_tests'],
            roi_percent=roi_percent,
            payback_period_months=payback_months,
            implementation_cost_gbp=implementation_cost_gbp
        )
        
        # Add notes
        analysis.notes = [
            f"Baseline: {baseline['num_tests']} tests costing £{baseline['total_cost_gbp']:,.0f}",
            f"Optimized: {optimized['num_tests']} tests costing £{optimized['total_cost_gbp']:,.0f}",
            f"Annual savings: £{annual_cost_savings:,.0f} and {annual_time_savings:.0f} hours",
            f"ROI: {roi_percent:.1f}% over {analysis_period_years} years",
            f"Payback period: {payback_months:.1f} months"
        ]
        
        logger.info(f"ROI analysis complete: {roi_percent:.1f}% ROI, {payback_months:.1f} month payback")
        
        return analysis
    
    def estimate_annual_savings(
        self,
        scenarios: List[Dict[str, Any]],
        optimization_rate: float = 0.25,
        test_frequency_per_year: int = 1
    ) -> Dict[str, float]:
        """
        Estimate annual savings from test optimization.
        
        Args:
            scenarios: Test scenarios
            optimization_rate: Expected optimization rate (0.25 = 25% reduction)
            test_frequency_per_year: How many times tests are run per year
            
        Returns:
            Dictionary with annual savings estimates
        """
        baseline = self.calculate_baseline_metrics(scenarios)
        
        # Calculate savings
        annual_cost_savings = baseline['total_cost_gbp'] * optimization_rate * test_frequency_per_year
        annual_time_savings = baseline['total_time_hours'] * optimization_rate * test_frequency_per_year
        tests_eliminated = int(baseline['num_tests'] * optimization_rate)
        
        return {
            'annual_cost_savings_gbp': annual_cost_savings,
            'annual_time_savings_hours': annual_time_savings,
            'annual_time_savings_days': annual_time_savings / 24,
            'tests_eliminated_per_cycle': tests_eliminated,
            'test_frequency_per_year': test_frequency_per_year,
            'optimization_rate': optimization_rate
        }


def create_roi_calculator(
    hourly_labor_rate_gbp: float = 75.0,
    facility_hourly_rate_gbp: float = 150.0
) -> ROICalculator:
    """
    Create an ROI calculator instance.
    
    Args:
        hourly_labor_rate_gbp: Hourly rate for labor
        facility_hourly_rate_gbp: Hourly rate for facilities
        
    Returns:
        ROICalculator instance
    """
    return ROICalculator(
        hourly_labor_rate_gbp=hourly_labor_rate_gbp,
        facility_hourly_rate_gbp=facility_hourly_rate_gbp
    )


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ROI CALCULATOR TEST")
    print("=" * 70)
    
    # Create calculator
    print("\n[1/3] Creating ROI calculator...")
    calculator = create_roi_calculator()
    print("[OK] Calculator created")
    
    # Create sample scenarios
    print("\n[2/3] Creating sample scenarios...")
    baseline_scenarios = [
        {
            'scenario_id': f'TEST-{i:03d}',
            'estimated_duration_hours': 24.0,
            'complexity_score': 6,
            'certification_required': i % 5 == 0
        }
        for i in range(100)
    ]
    
    optimized_scenarios = baseline_scenarios[:75]  # 25% reduction
    
    print(f"[OK] Baseline: {len(baseline_scenarios)} tests")
    print(f"[OK] Optimized: {len(optimized_scenarios)} tests")
    
    # Calculate ROI
    print("\n[3/3] Calculating ROI...")
    roi_analysis = calculator.calculate_roi(
        baseline_scenarios=baseline_scenarios,
        optimized_scenarios=optimized_scenarios,
        duplicates_eliminated=[],
        implementation_cost_gbp=50000.0
    )
    
    print(f"[OK] ROI Analysis Complete:\n")
    print(f"  Baseline: {roi_analysis.baseline_num_tests} tests, £{roi_analysis.baseline_total_cost_gbp:,.0f}")
    print(f"  Optimized: {roi_analysis.optimized_num_tests} tests, £{roi_analysis.optimized_total_cost_gbp:,.0f}")
    print(f"  Savings: £{roi_analysis.cost_savings_gbp:,.0f}, {roi_analysis.time_savings_hours:.0f} hours")
    print(f"  ROI: {roi_analysis.roi_percent:.1f}%")
    print(f"  Payback: {roi_analysis.payback_period_months:.1f} months")
    
    print("\n[OK] ROI calculator test complete")

