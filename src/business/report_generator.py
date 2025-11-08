"""
Automated report generation for business impact and governance.
Generates reports in JSON, Markdown, and HTML formats.
"""
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate formatted reports from business data.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_roi_report_json(
        self,
        roi_analysis: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate ROI report in JSON format.
        
        Args:
            roi_analysis: ROI analysis dictionary
            filename: Output filename
            
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating ROI report (JSON): {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(roi_analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"ROI report generated: {output_path}")
        
        return str(output_path)
    
    def generate_roi_report_markdown(
        self,
        roi_analysis: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate ROI report in Markdown format.
        
        Args:
            roi_analysis: ROI analysis dictionary
            filename: Output filename
            
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"roi_report_{timestamp}.md"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating ROI report (Markdown): {output_path}")
        
        # Extract data
        baseline = roi_analysis.get('baseline', {})
        optimized = roi_analysis.get('optimized', {})
        savings = roi_analysis.get('savings', {})
        roi = roi_analysis.get('roi', {})
        
        # Generate Markdown
        md = f'''# ROI Analysis Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Analysis Date**: {roi_analysis.get('analysis_date', 'N/A')}

---

## Executive Summary

This report presents the Return on Investment (ROI) analysis for the Virtual Testing Assistant (VTA) system implementation.

### Key Findings

- **ROI**: {roi.get('roi_percent', 0):.1f}%
- **Payback Period**: {roi.get('payback_period_months', 0):.1f} months
- **Annual Savings**: £{savings.get('cost_savings_gbp', 0):,.0f}
- **Tests Eliminated**: {savings.get('tests_eliminated', 0)} ({savings.get('reduction_percent', 0):.1f}% reduction)

---

## Baseline vs Optimized

### Baseline (Before VTA)

| Metric | Value |
|--------|-------|
| Number of Tests | {baseline.get('num_tests', 0)} |
| Total Cost | £{baseline.get('total_cost_gbp', 0):,.0f} |
| Total Time | {baseline.get('total_time_hours', 0):,.0f} hours ({baseline.get('total_time_hours', 0) / 24:.1f} days) |
| Average Cost per Test | £{baseline.get('avg_cost_per_test_gbp', 0):,.0f} |

### Optimized (With VTA)

| Metric | Value |
|--------|-------|
| Number of Tests | {optimized.get('num_tests', 0)} |
| Total Cost | £{optimized.get('total_cost_gbp', 0):,.0f} |
| Total Time | {optimized.get('total_time_hours', 0):,.0f} hours ({optimized.get('total_time_hours', 0) / 24:.1f} days) |
| Average Cost per Test | £{optimized.get('avg_cost_per_test_gbp', 0):,.0f} |

---

## Savings Analysis

### Annual Savings

- **Cost Savings**: £{savings.get('cost_savings_gbp', 0):,.0f}
- **Time Savings**: {savings.get('time_savings_hours', 0):,.0f} hours ({savings.get('time_savings_days', 0):.1f} days)
- **Tests Eliminated**: {savings.get('tests_eliminated', 0)}
- **Reduction**: {savings.get('reduction_percent', 0):.1f}%

### ROI Metrics

- **Implementation Cost**: £{roi.get('implementation_cost_gbp', 0):,.0f}
- **Net Benefit (Year 1)**: £{roi.get('net_benefit_gbp', 0):,.0f}
- **ROI**: {roi.get('roi_percent', 0):.1f}%
- **Payback Period**: {roi.get('payback_period_months', 0):.1f} months

---

## Cost-Benefit Breakdown

The VTA system provides substantial cost savings through:

1. **Duplicate Elimination**: Reducing redundant tests through AI-powered deduplication
2. **Test Optimization**: Intelligent test selection and prioritization
3. **Simulation Integration**: Moving appropriate tests to simulation (95% cost reduction)
4. **Process Automation**: Automated scenario generation and export

---

## Conclusion

The Virtual Testing Assistant delivers significant ROI with a payback period of less than {roi.get('payback_period_months', 0):.0f} months. 
The system is expected to save £{savings.get('cost_savings_gbp', 0):,.0f} annually while improving test coverage and quality.

### Recommendations

1. Proceed with full deployment across all vehicle platforms
2. Expand simulation integration to maximize cost savings
3. Continue training engineers on VTA capabilities
4. Monitor and track actual savings vs. projected

---

**Report Generated By**: Virtual Testing Assistant ROI Calculator  
**Contact**: Nissan NTCE + Cranfield University KTP Team
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info(f"ROI report generated: {output_path}")
        
        return str(output_path)
    
    def generate_metrics_report_markdown(
        self,
        metrics_summary: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate metrics report in Markdown format.
        
        Args:
            metrics_summary: Metrics summary dictionary
            filename: Output filename
            
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_report_{timestamp}.md"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating metrics report (Markdown): {output_path}")
        
        # Extract data
        coverage = metrics_summary.get('coverage', {})
        efficiency = metrics_summary.get('efficiency', {})
        quality = metrics_summary.get('quality', {})
        compliance = metrics_summary.get('compliance', {})
        
        # Generate Markdown
        md = f'''# Test Optimization Metrics Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Timestamp**: {metrics_summary.get('timestamp', 'N/A')}

---

## Overall Score: {metrics_summary.get('overall_score', 0):.1f}/100

---

## 1. Coverage Metrics

Test coverage across components, systems, and platforms.

| Metric | Value |
|--------|-------|
| Component Coverage | {coverage.get('component_coverage_percent', 0):.1f}% |
| System Coverage | {coverage.get('system_coverage_percent', 0):.1f}% |
| Platform Coverage | {coverage.get('platform_coverage_percent', 0):.1f}% |
| Regulatory Coverage | {coverage.get('regulatory_coverage_percent', 0):.1f}% |
| **Overall Coverage** | **{coverage.get('overall_coverage_percent', 0):.1f}%** |

### Coverage Analysis

{"✅ Excellent coverage" if coverage.get('overall_coverage_percent', 0) >= 80 else "⚠️ Needs improvement" if coverage.get('overall_coverage_percent', 0) >= 60 else "❌ Insufficient coverage"}

---

## 2. Efficiency Metrics

Test suite efficiency and optimization.

| Metric | Value |
|--------|-------|
| Total Tests | {efficiency.get('total_tests', 0)} |
| Average Duration | {efficiency.get('avg_duration_hours', 0):.1f} hours |
| Average Cost | £{efficiency.get('avg_cost_gbp', 0):,.0f} |
| Duplicate Rate | {efficiency.get('duplicate_rate_percent', 0):.1f}% |
| Optimization Rate | {efficiency.get('optimization_rate_percent', 0):.1f}% |
| **Efficiency Score** | **{efficiency.get('efficiency_score', 0):.1f}/100** |

### Efficiency Analysis

{"✅ Highly efficient" if efficiency.get('efficiency_score', 0) >= 80 else "⚠️ Can be improved" if efficiency.get('efficiency_score', 0) >= 60 else "❌ Needs optimization"}

---

## 3. Quality Metrics

Test execution quality and reliability.

| Metric | Value |
|--------|-------|
| Pass Rate | {quality.get('pass_rate_percent', 0):.1f}% |
| Failure Rate | {quality.get('failure_rate_percent', 0):.1f}% |
| Critical Pass Rate | {quality.get('critical_pass_rate_percent', 0):.1f}% |
| Confidence Score | {quality.get('avg_confidence_score', 0):.2f} |

### Quality Analysis

{"✅ High quality" if quality.get('pass_rate_percent', 0) >= 90 else "⚠️ Monitor failures" if quality.get('pass_rate_percent', 0) >= 75 else "❌ Quality concerns"}

---

## 4. Compliance Metrics

Regulatory and certification compliance.

| Metric | Value |
|--------|-------|
| Standards Coverage | {compliance.get('standards_coverage_percent', 0):.1f}% |
| Certification Progress | {compliance.get('certification_progress_percent', 0):.1f}% |
| **Compliance Score** | **{compliance.get('compliance_score', 0):.1f}/100** |

### Compliance Gaps

{chr(10).join(f"- {gap}" for gap in compliance.get('compliance_gaps', [])) if compliance.get('compliance_gaps') else "No gaps identified ✅"}

### Compliance Analysis

{"✅ Fully compliant" if compliance.get('compliance_score', 0) >= 90 else "⚠️ Minor gaps" if compliance.get('compliance_score', 0) >= 70 else "❌ Significant gaps"}

---

## Summary

The test suite achieves an overall score of **{metrics_summary.get('overall_score', 0):.1f}/100**.

### Strengths

- {"High coverage across all dimensions" if coverage.get('overall_coverage_percent', 0) >= 70 else ""}
- {"Efficient test execution" if efficiency.get('efficiency_score', 0) >= 70 else ""}
- {"Strong quality metrics" if quality.get('pass_rate_percent', 0) >= 85 else ""}
- {"Good compliance status" if compliance.get('compliance_score', 0) >= 70 else ""}

### Recommendations

1. {"Maintain current coverage levels" if coverage.get('overall_coverage_percent', 0) >= 70 else "Increase test coverage for underrepresented areas"}
2. {"Continue duplicate elimination efforts" if efficiency.get('duplicate_rate_percent', 0) > 5 else "Maintain low duplicate rate"}
3. {"Investigate and address failing tests" if quality.get('failure_rate_percent', 0) > 10 else "Continue quality practices"}
4. {"Address compliance gaps" if compliance.get('compliance_gaps') else "Maintain compliance standards"}

---

**Report Generated By**: Virtual Testing Assistant Metrics Tracker  
**Contact**: Nissan NTCE + Cranfield University KTP Team
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info(f"Metrics report generated: {output_path}")
        
        return str(output_path)
    
    def generate_lmc_report_markdown(
        self,
        lmc_report: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        Generate LMC report in Markdown format.
        
        Args:
            lmc_report: LMC report dictionary
            filename: Output filename
            
        Returns:
            Path to generated file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            quarter = lmc_report.get('quarter', 'Q1').replace(' ', '_')
            filename = f"lmc_report_{quarter}_{timestamp}.md"
        
        output_path = self.output_dir / filename
        
        logger.info(f"Generating LMC report (Markdown): {output_path}")
        
        # Extract data
        project = lmc_report.get('project', {})
        progress = lmc_report.get('progress', {})
        business = lmc_report.get('business_impact', {})
        risks = lmc_report.get('risks_and_issues', {})
        skills = lmc_report.get('skills_transfer', {})
        research = lmc_report.get('research_output', {})
        
        # Generate Markdown
        md = f'''# Local Management Committee Report

**Quarter**: {lmc_report.get('quarter', 'N/A')}  
**Report Date**: {lmc_report.get('report_date', 'N/A')}

---

## Project Overview

**Project Name**: {project.get('name', 'N/A')}  
**KTP Number**: {project.get('ktp_number', 'N/A')}  
**Company Partner**: {project.get('company', 'N/A')}  
**University Partner**: {project.get('university', 'N/A')}

---

## Project Health

| Metric | Value | Status |
|--------|-------|--------|
| Completion | {project.get('completion_percent', 0):.1f}% | {"✅ On Track" if project.get('is_on_track') else "⚠️ At Risk"} |
| Time Elapsed | {project.get('time_elapsed_percent', 0):.1f}% | {project.get('months_elapsed', 0)} months |
| Months Remaining | {project.get('months_remaining', 0)} months | - |

**Overall Status**: {"✅ ON TRACK" if project.get('is_on_track') else "⚠️ AT RISK"}

---

## Progress Summary

### Completed Phases: {progress.get('completed_phases', 0)}/{progress.get('total_phases', 0)}

**Current Phase**: {lmc_report.get('current_phase', 'N/A')}

### Deliverables

- **Complete**: {progress.get('deliverables_complete', 0)}/{progress.get('deliverables_total', 0)}
- **At Risk**: {progress.get('deliverables_at_risk', 0)}

---

## Technical Achievements

{chr(10).join(lmc_report.get('technical_achievements', []))}

---

## Next Milestones

{chr(10).join(f"{i+1}. {milestone}" for i, milestone in enumerate(lmc_report.get('next_milestones', [])))}

---

## Business Impact

### ROI Analysis

{f"- **ROI**: {business.get('roi_analysis', {}).get('roi_percent', 0):.1f}%" if business.get('roi_analysis') else "Pending"}
{f"- **Payback Period**: {business.get('roi_analysis', {}).get('payback_months', 0):.1f} months" if business.get('roi_analysis') else ""}

### Metrics Summary

{f"- **Overall Score**: {business.get('metrics_summary', {}).get('overall_score', 0):.1f}/100" if business.get('metrics_summary') else "Pending"}

---

## Risks and Issues

### Risks

{chr(10).join(f"- {risk}" for risk in risks.get('risks', [])) if risks.get('risks') else "No significant risks identified"}

### Issues

{chr(10).join(f"- {issue}" for issue in risks.get('issues', [])) if risks.get('issues') else "No issues reported"}

### Mitigations

{chr(10).join(f"- {mit}" for mit in risks.get('mitigations', [])) if risks.get('mitigations') else "N/A"}

---

## Skills Transfer

### Training Completed

{chr(10).join(f"- {training}" for training in skills.get('training_completed', [])) if skills.get('training_completed') else "N/A"}

**Knowledge Sharing Sessions**: {skills.get('knowledge_sharing_sessions', 0)}

---

## Research Output

### Publications

{chr(10).join(f"- {pub}" for pub in research.get('publications', [])) if research.get('publications') else "None yet"}

**Patents Filed**: {research.get('patents_filed', 0)}

---

## Recommendations

1. Continue momentum on current deliverables
2. Monitor at-risk deliverables closely
3. Maintain regular communication with stakeholders
4. Plan for knowledge transfer activities

---

**Prepared By**: KTP Associate  
**Reviewed By**: Academic Supervisor + Company Supervisor  
**Distribution**: LMC Members, Innovate UK
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        logger.info(f"LMC report generated: {output_path}")
        
        return str(output_path)


def create_report_generator(output_dir: str = "reports") -> ReportGenerator:
    """
    Create a report generator instance.
    
    Args:
        output_dir: Directory for output reports
        
    Returns:
        ReportGenerator instance
    """
    return ReportGenerator(output_dir=output_dir)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("REPORT GENERATOR TEST")
    print("=" * 70)
    
    # Create generator
    print("\n[1/3] Creating report generator...")
    generator = create_report_generator(output_dir="reports_test")
    print("[OK] Generator created")
    
    # Generate ROI report
    print("\n[2/3] Generating ROI report...")
    roi_data = {
        'baseline': {'num_tests': 100, 'total_cost_gbp': 1000000, 'total_time_hours': 2400},
        'optimized': {'num_tests': 75, 'total_cost_gbp': 750000, 'total_time_hours': 1800},
        'savings': {'cost_savings_gbp': 250000, 'time_savings_hours': 600, 'tests_eliminated': 25, 'reduction_percent': 25.0},
        'roi': {'roi_percent': 400.0, 'payback_period_months': 2.4, 'implementation_cost_gbp': 50000},
        'analysis_date': datetime.now().isoformat()
    }
    
    roi_report = generator.generate_roi_report_markdown(roi_data)
    print(f"[OK] ROI report: {roi_report}")
    
    # Generate metrics report
    print("\n[3/3] Generating metrics report...")
    metrics_data = {
        'overall_score': 75.0,
        'coverage': {'overall_coverage_percent': 80.0},
        'efficiency': {'efficiency_score': 70.0, 'total_tests': 75},
        'quality': {'pass_rate_percent': 95.0},
        'compliance': {'compliance_score': 85.0, 'compliance_gaps': []},
        'timestamp': datetime.now().isoformat()
    }
    
    metrics_report = generator.generate_metrics_report_markdown(metrics_data)
    print(f"[OK] Metrics report: {metrics_report}")
    
    print("\n[OK] Report generator test complete")

