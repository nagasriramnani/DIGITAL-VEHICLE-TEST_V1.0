"""
Tests for Phase 7: Business Impact + Governance.
"""
import pytest
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any

from src.business.roi_calculator import (
    ROICalculator,
    TestCost,
    TestEfficiency,
    ROIAnalysis,
    create_roi_calculator
)
from src.business.metrics import (
    MetricsTracker,
    CoverageMetrics,
    EfficiencyMetrics,
    QualityMetrics,
    ComplianceMetrics,
    MetricsSummary,
    create_metrics_tracker
)
from src.business.governance import (
    GovernanceReporter,
    Deliverable,
    KTPProgress,
    LMCReport,
    DeliverableStatus,
    ProjectPhase,
    create_governance_reporter
)
from src.business.report_generator import (
    ReportGenerator,
    create_report_generator
)


class TestROICalculator:
    """Test ROI calculator."""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return create_roi_calculator()
    
    @pytest.fixture
    def sample_scenarios(self):
        """Create sample test scenarios."""
        return [
            {
                'scenario_id': f'TEST-{i:03d}',
                'estimated_duration_hours': 24.0,
                'complexity_score': 6,
                'certification_required': i % 5 == 0
            }
            for i in range(10)
        ]
    
    def test_calculator_initialization(self, calculator):
        """Test calculator initializes correctly."""
        assert calculator is not None
        assert calculator.hourly_labor_rate_gbp == 75.0
        assert calculator.facility_hourly_rate_gbp == 150.0
    
    def test_estimate_test_cost(self, calculator, sample_scenarios):
        """Test test cost estimation."""
        scenario = sample_scenarios[0]
        cost = calculator.estimate_test_cost(scenario)
        
        assert isinstance(cost, TestCost)
        assert cost.total_cost_gbp > 0
        assert cost.labor_cost_gbp > 0
        assert cost.facility_cost_gbp > 0
    
    def test_calculate_baseline_metrics(self, calculator, sample_scenarios):
        """Test baseline metrics calculation."""
        baseline = calculator.calculate_baseline_metrics(sample_scenarios)
        
        assert 'num_tests' in baseline
        assert baseline['num_tests'] == len(sample_scenarios)
        assert baseline['total_cost_gbp'] > 0
        assert baseline['total_time_hours'] > 0
    
    def test_calculate_roi(self, calculator, sample_scenarios):
        """Test ROI calculation."""
        optimized = sample_scenarios[:7]  # 30% reduction
        
        roi_analysis = calculator.calculate_roi(
            baseline_scenarios=sample_scenarios,
            optimized_scenarios=optimized,
            duplicates_eliminated=[],
            implementation_cost_gbp=50000.0
        )
        
        assert isinstance(roi_analysis, ROIAnalysis)
        assert roi_analysis.baseline_num_tests == len(sample_scenarios)
        assert roi_analysis.optimized_num_tests == len(optimized)
        assert roi_analysis.cost_savings_gbp > 0
        assert roi_analysis.roi_percent > 0
    
    def test_estimate_annual_savings(self, calculator, sample_scenarios):
        """Test annual savings estimation."""
        savings = calculator.estimate_annual_savings(
            sample_scenarios,
            optimization_rate=0.25,
            test_frequency_per_year=2
        )
        
        assert 'annual_cost_savings_gbp' in savings
        assert 'annual_time_savings_hours' in savings
        assert savings['annual_cost_savings_gbp'] > 0


class TestMetricsTracker:
    """Test metrics tracker."""
    
    @pytest.fixture
    def tracker(self):
        """Create tracker instance."""
        return create_metrics_tracker()
    
    @pytest.fixture
    def sample_scenarios(self):
        """Create sample scenarios."""
        return [
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
            for i in range(20)
        ]
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initializes correctly."""
        assert tracker is not None
    
    def test_calculate_coverage(self, tracker, sample_scenarios):
        """Test coverage calculation."""
        all_components = ['Battery', 'Motor', 'Inverter', 'BMS']
        all_systems = ['Powertrain', 'Battery', 'Thermal']
        all_platforms = ['EV', 'HEV', 'ICE']
        required_standards = ['UNECE_R100', 'ISO_6469']
        
        coverage = tracker.calculate_coverage(
            sample_scenarios,
            all_components,
            all_systems,
            all_platforms,
            required_standards
        )
        
        assert isinstance(coverage, CoverageMetrics)
        assert coverage.total_components == len(all_components)
        assert coverage.covered_components > 0
        assert 0 <= coverage.overall_coverage_percent <= 100
    
    def test_calculate_efficiency(self, tracker, sample_scenarios):
        """Test efficiency calculation."""
        efficiency = tracker.calculate_efficiency(
            sample_scenarios,
            num_components=10,
            num_duplicates=2,
            optimization_rate=0.2
        )
        
        assert isinstance(efficiency, EfficiencyMetrics)
        assert efficiency.total_tests == len(sample_scenarios)
        assert efficiency.avg_duration_hours > 0
        assert 0 <= efficiency.efficiency_score <= 100
    
    def test_calculate_quality(self, tracker, sample_scenarios):
        """Test quality metrics calculation."""
        quality = tracker.calculate_quality(sample_scenarios)
        
        assert isinstance(quality, QualityMetrics)
        assert quality.total_tests_executed > 0
        assert 0 <= quality.pass_rate_percent <= 100
    
    def test_calculate_compliance(self, tracker, sample_scenarios):
        """Test compliance calculation."""
        required_standards = ['UNECE_R100', 'ISO_6469', 'SAE_J2929']
        
        compliance = tracker.calculate_compliance(
            sample_scenarios,
            required_standards
        )
        
        assert isinstance(compliance, ComplianceMetrics)
        assert compliance.total_standards == len(required_standards)
        assert 0 <= compliance.compliance_score <= 100
    
    def test_calculate_all_metrics(self, tracker, sample_scenarios):
        """Test calculating all metrics."""
        all_components = ['Battery', 'Motor', 'Inverter']
        all_systems = ['Powertrain', 'Battery']
        all_platforms = ['EV', 'HEV']
        required_standards = ['UNECE_R100', 'ISO_6469']
        
        summary = tracker.calculate_all_metrics(
            sample_scenarios,
            all_components,
            all_systems,
            all_platforms,
            required_standards,
            num_duplicates=2,
            optimization_rate=0.2
        )
        
        assert isinstance(summary, MetricsSummary)
        assert 0 <= summary.overall_score <= 100
        assert summary.coverage is not None
        assert summary.efficiency is not None
        assert summary.quality is not None
        assert summary.compliance is not None


class TestGovernanceReporter:
    """Test governance reporter."""
    
    @pytest.fixture
    def reporter(self):
        """Create reporter instance."""
        return create_governance_reporter()
    
    def test_reporter_initialization(self, reporter):
        """Test reporter initializes correctly."""
        assert reporter is not None
        assert reporter.ktp_progress is not None
    
    def test_ktp_progress(self, reporter):
        """Test KTP progress tracking."""
        progress = reporter.ktp_progress
        
        assert progress.total_phases == 12
        assert progress.completed_phases == 6
        assert 0 <= progress.completion_percent <= 100
        assert progress.project_name == "Virtual Testing Assistant"
    
    def test_deliverables(self, reporter):
        """Test deliverables tracking."""
        progress = reporter.ktp_progress
        
        assert len(progress.deliverables) > 0
        assert progress.deliverables_complete >= 0
        
        # Check deliverable status
        completed = [d for d in progress.deliverables if d.status == DeliverableStatus.COMPLETE]
        assert len(completed) >= 6
    
    def test_generate_lmc_report(self, reporter):
        """Test LMC report generation."""
        roi_data = {'roi_percent': 400.0, 'payback_months': 2.0}
        metrics_data = {'overall_score': 75.0}
        
        report = reporter.generate_lmc_report(
            quarter="Q1 2025",
            roi_analysis=roi_data,
            metrics_summary=metrics_data
        )
        
        assert isinstance(report, LMCReport)
        assert report.quarter == "Q1 2025"
        assert len(report.technical_achievements) > 0
        assert len(report.next_milestones) > 0
    
    def test_get_status_summary(self, reporter):
        """Test status summary."""
        summary = reporter.get_status_summary()
        
        assert 'project_health' in summary
        assert 'completion_percent' in summary
        assert 'months_remaining' in summary


class TestReportGenerator:
    """Test report generator."""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator instance with temp directory."""
        return create_report_generator(output_dir=str(tmp_path / "reports"))
    
    @pytest.fixture
    def sample_roi_data(self):
        """Create sample ROI data."""
        return {
            'baseline': {'num_tests': 100, 'total_cost_gbp': 1000000, 'total_time_hours': 2400},
            'optimized': {'num_tests': 75, 'total_cost_gbp': 750000, 'total_time_hours': 1800},
            'savings': {'cost_savings_gbp': 250000, 'time_savings_hours': 600, 'tests_eliminated': 25},
            'roi': {'roi_percent': 400.0, 'payback_period_months': 2.4, 'implementation_cost_gbp': 50000},
            'analysis_date': datetime.now().isoformat()
        }
    
    @pytest.fixture
    def sample_metrics_data(self):
        """Create sample metrics data."""
        return {
            'overall_score': 75.0,
            'coverage': {'overall_coverage_percent': 80.0},
            'efficiency': {'efficiency_score': 70.0, 'total_tests': 75},
            'quality': {'pass_rate_percent': 95.0},
            'compliance': {'compliance_score': 85.0, 'compliance_gaps': []},
            'timestamp': datetime.now().isoformat()
        }
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly."""
        assert generator is not None
        assert generator.output_dir.exists()
    
    def test_generate_roi_report_json(self, generator, sample_roi_data):
        """Test JSON ROI report generation."""
        output_path = generator.generate_roi_report_json(sample_roi_data)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.json'
    
    def test_generate_roi_report_markdown(self, generator, sample_roi_data):
        """Test Markdown ROI report generation."""
        output_path = generator.generate_roi_report_markdown(sample_roi_data)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.md'
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'ROI Analysis Report' in content
        assert '£250,000' in content  # Savings
    
    def test_generate_metrics_report_markdown(self, generator, sample_metrics_data):
        """Test Markdown metrics report generation."""
        output_path = generator.generate_metrics_report_markdown(sample_metrics_data)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.md'
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'Test Optimization Metrics Report' in content
        assert '75.0/100' in content  # Overall score
    
    def test_generate_lmc_report_markdown(self, generator):
        """Test Markdown LMC report generation."""
        lmc_data = {
            'quarter': 'Q1 2025',
            'report_date': '2025-01-15',
            'project': {
                'name': 'Virtual Testing Assistant',
                'ktp_number': 'KTP014567',
                'company': 'Nissan NTCE',
                'university': 'Cranfield University',
                'completion_percent': 50.0,
                'is_on_track': True
            },
            'progress': {
                'completed_phases': 6,
                'total_phases': 12,
                'deliverables_complete': 6,
                'deliverables_total': 12
            },
            'current_phase': 'Phase 7: Business Impact',
            'technical_achievements': ['Achievement 1', 'Achievement 2'],
            'next_milestones': ['Milestone 1', 'Milestone 2'],
            'risks_and_issues': {'risks': [], 'issues': [], 'mitigations': []},
            'skills_transfer': {'training_completed': [], 'knowledge_sharing_sessions': 10},
            'research_output': {'publications': [], 'patents_filed': 0}
        }
        
        output_path = generator.generate_lmc_report_markdown(lmc_data)
        
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.md'
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'Local Management Committee Report' in content
        assert 'Q1 2025' in content


class TestIntegration:
    """Integration tests for business impact workflow."""
    
    def test_end_to_end_roi_analysis(self, tmp_path):
        """Test complete ROI analysis workflow."""
        # Create test scenarios
        baseline_scenarios = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'estimated_duration_hours': 24.0,
                'complexity_score': 6,
                'certification_required': False
            }
            for i in range(50)
        ]
        
        optimized_scenarios = baseline_scenarios[:40]  # 20% reduction
        
        # Calculate ROI
        calculator = create_roi_calculator()
        roi_analysis = calculator.calculate_roi(
            baseline_scenarios,
            optimized_scenarios,
            [],
            implementation_cost_gbp=50000.0
        )
        
        # Generate report
        generator = create_report_generator(output_dir=str(tmp_path / "reports"))
        roi_dict = roi_analysis.to_dict()
        report_path = generator.generate_roi_report_markdown(roi_dict)
        
        assert Path(report_path).exists()
        assert roi_analysis.roi_percent > 0
    
    def test_end_to_end_metrics_tracking(self, tmp_path):
        """Test complete metrics tracking workflow."""
        # Create scenarios
        scenarios = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'target_components': ['Battery'],
                'target_systems': ['Powertrain'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['UNECE_R100'],
                'estimated_duration_hours': 24.0,
                'estimated_cost_gbp': 8000.0,
                'historical_results': [{'passed': True}]
            }
            for i in range(30)
        ]
        
        # Calculate metrics
        tracker = create_metrics_tracker()
        summary = tracker.calculate_all_metrics(
            scenarios,
            ['Battery', 'Motor'],
            ['Powertrain', 'Battery'],
            ['EV', 'HEV'],
            ['UNECE_R100', 'ISO_6469']
        )
        
        # Generate report
        generator = create_report_generator(output_dir=str(tmp_path / "reports"))
        metrics_dict = summary.to_dict()
        report_path = generator.generate_metrics_report_markdown(metrics_dict)
        
        assert Path(report_path).exists()
        assert summary.overall_score > 0
    
    def test_end_to_end_governance_reporting(self, tmp_path):
        """Test complete governance reporting workflow."""
        # Create reporter
        reporter = create_governance_reporter()
        
        # Generate LMC report
        report = reporter.generate_lmc_report("Q1 2025")
        
        # Generate markdown
        generator = create_report_generator(output_dir=str(tmp_path / "reports"))
        report_dict = report.to_dict()
        report_path = generator.generate_lmc_report_markdown(report_dict)
        
        assert Path(report_path).exists()
        assert report.ktp_progress.completion_percent > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

