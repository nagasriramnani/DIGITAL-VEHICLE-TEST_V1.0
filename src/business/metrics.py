"""
Test optimization metrics tracking and analysis.
Tracks coverage, efficiency, quality, and compliance metrics.
"""
import logging
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Test coverage metrics."""
    total_components: int
    covered_components: int
    total_systems: int
    covered_systems: int
    total_platforms: int
    covered_platforms: int
    regulatory_coverage_percent: float = 0.0
    
    @property
    def component_coverage_percent(self) -> float:
        """Calculate component coverage percentage."""
        return (self.covered_components / self.total_components * 100) if self.total_components > 0 else 0
    
    @property
    def system_coverage_percent(self) -> float:
        """Calculate system coverage percentage."""
        return (self.covered_systems / self.total_systems * 100) if self.total_systems > 0 else 0
    
    @property
    def platform_coverage_percent(self) -> float:
        """Calculate platform coverage percentage."""
        return (self.covered_platforms / self.total_platforms * 100) if self.total_platforms > 0 else 0
    
    @property
    def overall_coverage_percent(self) -> float:
        """Calculate overall coverage percentage."""
        return (
            self.component_coverage_percent * 0.4 +
            self.system_coverage_percent * 0.3 +
            self.platform_coverage_percent * 0.2 +
            self.regulatory_coverage_percent * 0.1
        )


@dataclass
class EfficiencyMetrics:
    """Test efficiency metrics."""
    total_tests: int
    avg_duration_hours: float
    avg_cost_gbp: float
    tests_per_component: float
    duplicate_rate_percent: float = 0.0
    optimization_rate_percent: float = 0.0
    
    @property
    def efficiency_score(self) -> float:
        """
        Calculate efficiency score (0-100).
        Higher is better (fewer duplicates, higher optimization).
        """
        return (
            (100 - self.duplicate_rate_percent) * 0.6 +
            self.optimization_rate_percent * 0.4
        )


@dataclass
class QualityMetrics:
    """Test quality metrics."""
    total_tests_executed: int
    passed_tests: int
    failed_tests: int
    avg_confidence_score: float = 0.0
    critical_tests_passed: int = 0
    critical_tests_total: int = 0
    
    @property
    def pass_rate_percent(self) -> float:
        """Calculate pass rate percentage."""
        return (self.passed_tests / self.total_tests_executed * 100) if self.total_tests_executed > 0 else 0
    
    @property
    def failure_rate_percent(self) -> float:
        """Calculate failure rate percentage."""
        return (self.failed_tests / self.total_tests_executed * 100) if self.total_tests_executed > 0 else 0
    
    @property
    def critical_pass_rate_percent(self) -> float:
        """Calculate critical test pass rate."""
        return (self.critical_tests_passed / self.critical_tests_total * 100) if self.critical_tests_total > 0 else 0


@dataclass
class ComplianceMetrics:
    """Regulatory compliance metrics."""
    total_standards: int
    covered_standards: int
    certification_tests_completed: int
    certification_tests_total: int
    compliance_gaps: List[str] = field(default_factory=list)
    
    @property
    def standards_coverage_percent(self) -> float:
        """Calculate standards coverage percentage."""
        return (self.covered_standards / self.total_standards * 100) if self.total_standards > 0 else 0
    
    @property
    def certification_progress_percent(self) -> float:
        """Calculate certification progress percentage."""
        return (self.certification_tests_completed / self.certification_tests_total * 100) if self.certification_tests_total > 0 else 0
    
    @property
    def compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)."""
        gap_penalty = len(self.compliance_gaps) * 5  # 5% penalty per gap
        base_score = (
            self.standards_coverage_percent * 0.6 +
            self.certification_progress_percent * 0.4
        )
        return max(0, base_score - gap_penalty)


@dataclass
class MetricsSummary:
    """Complete metrics summary."""
    coverage: CoverageMetrics
    efficiency: EfficiencyMetrics
    quality: QualityMetrics
    compliance: ComplianceMetrics
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall score (0-100)."""
        return (
            self.coverage.overall_coverage_percent * 0.30 +
            self.efficiency.efficiency_score * 0.25 +
            self.quality.pass_rate_percent * 0.25 +
            self.compliance.compliance_score * 0.20
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'overall_score': self.overall_score,
            'timestamp': self.timestamp.isoformat(),
            'coverage': {
                'component_coverage_percent': self.coverage.component_coverage_percent,
                'system_coverage_percent': self.coverage.system_coverage_percent,
                'platform_coverage_percent': self.coverage.platform_coverage_percent,
                'regulatory_coverage_percent': self.coverage.regulatory_coverage_percent,
                'overall_coverage_percent': self.coverage.overall_coverage_percent
            },
            'efficiency': {
                'total_tests': self.efficiency.total_tests,
                'avg_duration_hours': self.efficiency.avg_duration_hours,
                'avg_cost_gbp': self.efficiency.avg_cost_gbp,
                'duplicate_rate_percent': self.efficiency.duplicate_rate_percent,
                'optimization_rate_percent': self.efficiency.optimization_rate_percent,
                'efficiency_score': self.efficiency.efficiency_score
            },
            'quality': {
                'pass_rate_percent': self.quality.pass_rate_percent,
                'failure_rate_percent': self.quality.failure_rate_percent,
                'critical_pass_rate_percent': self.quality.critical_pass_rate_percent,
                'avg_confidence_score': self.quality.avg_confidence_score
            },
            'compliance': {
                'standards_coverage_percent': self.compliance.standards_coverage_percent,
                'certification_progress_percent': self.compliance.certification_progress_percent,
                'compliance_score': self.compliance.compliance_score,
                'compliance_gaps': self.compliance.compliance_gaps
            }
        }


class MetricsTracker:
    """
    Track and analyze test optimization metrics.
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        pass
    
    def calculate_coverage(
        self,
        scenarios: List[Dict[str, Any]],
        all_components: List[str],
        all_systems: List[str],
        all_platforms: List[str],
        required_standards: List[str]
    ) -> CoverageMetrics:
        """
        Calculate test coverage metrics.
        
        Args:
            scenarios: List of test scenarios
            all_components: All possible components
            all_systems: All possible systems
            all_platforms: All possible platforms
            required_standards: Required regulatory standards
            
        Returns:
            CoverageMetrics
        """
        logger.info("Calculating coverage metrics...")
        
        # Track coverage
        covered_components: Set[str] = set()
        covered_systems: Set[str] = set()
        covered_platforms: Set[str] = set()
        covered_standards: Set[str] = set()
        
        for scenario in scenarios:
            # Add components
            for comp in scenario.get('target_components', []):
                covered_components.add(comp)
            
            # Add systems
            for sys in scenario.get('target_systems', []):
                covered_systems.add(sys)
            
            # Add platforms
            for plat in scenario.get('applicable_platforms', []):
                covered_platforms.add(plat)
            
            # Add standards
            for std in scenario.get('regulatory_standards', []):
                covered_standards.add(std)
        
        # Calculate regulatory coverage
        reg_coverage = (len(covered_standards) / len(required_standards) * 100) if required_standards else 0
        
        return CoverageMetrics(
            total_components=len(all_components),
            covered_components=len(covered_components),
            total_systems=len(all_systems),
            covered_systems=len(covered_systems),
            total_platforms=len(all_platforms),
            covered_platforms=len(covered_platforms),
            regulatory_coverage_percent=reg_coverage
        )
    
    def calculate_efficiency(
        self,
        scenarios: List[Dict[str, Any]],
        num_components: int,
        num_duplicates: int = 0,
        optimization_rate: float = 0.0
    ) -> EfficiencyMetrics:
        """
        Calculate efficiency metrics.
        
        Args:
            scenarios: List of test scenarios
            num_components: Total number of components
            num_duplicates: Number of duplicate tests
            optimization_rate: Optimization rate achieved (0-1)
            
        Returns:
            EfficiencyMetrics
        """
        logger.info("Calculating efficiency metrics...")
        
        num_tests = len(scenarios)
        
        # Calculate averages
        total_duration = sum(s.get('estimated_duration_hours', 0) for s in scenarios)
        total_cost = sum(s.get('estimated_cost_gbp', 0) for s in scenarios)
        
        avg_duration = total_duration / num_tests if num_tests > 0 else 0
        avg_cost = total_cost / num_tests if num_tests > 0 else 0
        
        # Tests per component
        tests_per_comp = num_tests / num_components if num_components > 0 else 0
        
        # Duplicate rate
        dup_rate = (num_duplicates / num_tests * 100) if num_tests > 0 else 0
        
        return EfficiencyMetrics(
            total_tests=num_tests,
            avg_duration_hours=avg_duration,
            avg_cost_gbp=avg_cost,
            tests_per_component=tests_per_comp,
            duplicate_rate_percent=dup_rate,
            optimization_rate_percent=optimization_rate * 100
        )
    
    def calculate_quality(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> QualityMetrics:
        """
        Calculate quality metrics based on historical results.
        
        Args:
            scenarios: List of test scenarios with historical_results
            
        Returns:
            QualityMetrics
        """
        logger.info("Calculating quality metrics...")
        
        total_executed = 0
        passed = 0
        failed = 0
        critical_passed = 0
        critical_total = 0
        confidence_scores = []
        
        for scenario in scenarios:
            historical = scenario.get('historical_results', [])
            
            if historical:
                total_executed += len(historical)
                
                for result in historical:
                    if result.get('passed', False):
                        passed += 1
                    else:
                        failed += 1
                
                # Track critical tests
                if scenario.get('risk_level') == 'critical':
                    critical_total += 1
                    # Check if latest result passed
                    if historical and historical[-1].get('passed', False):
                        critical_passed += 1
                
                # Confidence score (based on consistency)
                if len(historical) >= 3:
                    pass_count = sum(1 for r in historical if r.get('passed', False))
                    confidence = pass_count / len(historical)
                    confidence_scores.append(confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return QualityMetrics(
            total_tests_executed=total_executed,
            passed_tests=passed,
            failed_tests=failed,
            avg_confidence_score=avg_confidence,
            critical_tests_passed=critical_passed,
            critical_tests_total=critical_total
        )
    
    def calculate_compliance(
        self,
        scenarios: List[Dict[str, Any]],
        required_standards: List[str]
    ) -> ComplianceMetrics:
        """
        Calculate compliance metrics.
        
        Args:
            scenarios: List of test scenarios
            required_standards: Required regulatory standards
            
        Returns:
            ComplianceMetrics
        """
        logger.info("Calculating compliance metrics...")
        
        # Track covered standards
        covered_standards: Set[str] = set()
        for scenario in scenarios:
            for std in scenario.get('regulatory_standards', []):
                covered_standards.add(std)
        
        # Count certification tests
        cert_total = sum(1 for s in scenarios if s.get('certification_required', False))
        cert_completed = sum(
            1 for s in scenarios
            if s.get('certification_required', False) and
            s.get('historical_results', []) and
            any(r.get('passed', False) for r in s['historical_results'])
        )
        
        # Identify compliance gaps
        gaps = [std for std in required_standards if std not in covered_standards]
        
        return ComplianceMetrics(
            total_standards=len(required_standards),
            covered_standards=len(covered_standards),
            certification_tests_completed=cert_completed,
            certification_tests_total=cert_total,
            compliance_gaps=gaps
        )
    
    def calculate_all_metrics(
        self,
        scenarios: List[Dict[str, Any]],
        all_components: List[str],
        all_systems: List[str],
        all_platforms: List[str],
        required_standards: List[str],
        num_duplicates: int = 0,
        optimization_rate: float = 0.0
    ) -> MetricsSummary:
        """
        Calculate all metrics and return summary.
        
        Args:
            scenarios: List of test scenarios
            all_components: All possible components
            all_systems: All possible systems
            all_platforms: All possible platforms
            required_standards: Required standards
            num_duplicates: Number of duplicates found
            optimization_rate: Optimization rate achieved
            
        Returns:
            MetricsSummary with all metrics
        """
        logger.info("Calculating all metrics...")
        
        coverage = self.calculate_coverage(
            scenarios,
            all_components,
            all_systems,
            all_platforms,
            required_standards
        )
        
        efficiency = self.calculate_efficiency(
            scenarios,
            len(all_components),
            num_duplicates,
            optimization_rate
        )
        
        quality = self.calculate_quality(scenarios)
        
        compliance = self.calculate_compliance(scenarios, required_standards)
        
        summary = MetricsSummary(
            coverage=coverage,
            efficiency=efficiency,
            quality=quality,
            compliance=compliance
        )
        
        logger.info(f"Metrics summary: Overall score {summary.overall_score:.1f}/100")
        
        return summary


def create_metrics_tracker() -> MetricsTracker:
    """
    Create a metrics tracker instance.
    
    Returns:
        MetricsTracker instance
    """
    return MetricsTracker()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("METRICS TRACKER TEST")
    print("=" * 70)
    
    # Create tracker
    print("\n[1/2] Creating metrics tracker...")
    tracker = create_metrics_tracker()
    print("[OK] Tracker created")
    
    # Create sample data
    print("\n[2/2] Calculating metrics...")
    
    scenarios = [
        {
            'scenario_id': f'TEST-{i:03d}',
            'target_components': ['Battery', 'Motor'],
            'target_systems': ['Powertrain'],
            'applicable_platforms': ['EV'],
            'regulatory_standards': ['UNECE_R100'],
            'estimated_duration_hours': 24.0,
            'estimated_cost_gbp': 8000.0,
            'certification_required': i % 5 == 0,
            'risk_level': 'high' if i % 10 == 0 else 'medium',
            'historical_results': [{'passed': True}, {'passed': True}]
        }
        for i in range(50)
    ]
    
    all_components = ['Battery', 'Motor', 'Inverter', 'BMS', 'Charger']
    all_systems = ['Powertrain', 'Battery', 'Thermal']
    all_platforms = ['EV', 'HEV', 'ICE']
    required_standards = ['UNECE_R100', 'ISO_6469', 'SAE_J2929']
    
    summary = tracker.calculate_all_metrics(
        scenarios,
        all_components,
        all_systems,
        all_platforms,
        required_standards,
        num_duplicates=5,
        optimization_rate=0.25
    )
    
    print(f"[OK] Metrics calculated:\n")
    print(f"  Overall Score: {summary.overall_score:.1f}/100")
    print(f"  Coverage: {summary.coverage.overall_coverage_percent:.1f}%")
    print(f"  Efficiency: {summary.efficiency.efficiency_score:.1f}/100")
    print(f"  Quality (Pass Rate): {summary.quality.pass_rate_percent:.1f}%")
    print(f"  Compliance: {summary.compliance.compliance_score:.1f}/100")
    
    print("\n[OK] Metrics tracker test complete")

