"""
LangChain tools for VTA conversational AI.
Each tool provides specific functionality that the agent can use.
"""
import logging
from typing import Optional, Type, Dict, Any, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import LangChain
try:
    # Try langchain_core first (newer versions)
    try:
        from langchain_core.tools import BaseTool
    except ImportError:
        # Fallback to langchain.tools (older versions)
        from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
    logger.info("LangChain is available")
except (ImportError, ModuleNotFoundError):
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available")
    
    # Import Pydantic for type annotations
    from pydantic import BaseModel, Field
    from typing import Optional, Type
    
    # Stubs - Properly typed for Pydantic compatibility
    class BaseTool:
        """Base tool stub when LangChain is not available."""
        def __init__(self, **kwargs):
            # Allow setting attributes dynamically
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def _run(self, *args, **kwargs):
            return "Tool not available"


# Import VTA modules
from src.ai.recommender import create_recommender
from src.business.roi_calculator import create_roi_calculator
from src.business.metrics import create_metrics_tracker


class RecommendationInput(BaseModel):
    """Input for recommendation tool."""
    vehicle_model: str = Field(description="Vehicle model name (e.g., Ariya, Leaf)")
    platform: str = Field(description="Platform type: EV, HEV, or ICE")
    systems: str = Field(description="Comma-separated target systems (e.g., Battery,Powertrain)")
    top_k: int = Field(default=5, description="Number of recommendations")


# Tool description constants
_RECOMMENDATION_DESC = """
Get AI-powered test recommendations for a vehicle configuration.
Use this when the user asks for test suggestions or recommendations.
Input should include vehicle_model, platform, and systems.
Example: vehicle_model='Ariya', platform='EV', systems='Battery,Powertrain'
"""

class RecommendationTool(BaseTool):
    """Tool for getting test recommendations."""
    
    # Always define with type annotations for Pydantic compatibility
    name: str = "get_recommendations"
    description: str = _RECOMMENDATION_DESC
    args_schema: Type[BaseModel] = RecommendationInput
    
    def __init__(self, **kwargs):
        if LANGCHAIN_AVAILABLE:
            # Pass required fields to BaseTool
            super().__init__(name="get_recommendations", description=_RECOMMENDATION_DESC, args_schema=RecommendationInput, **kwargs)
        else:
            super().__init__()
            # Stub BaseTool - set instance attributes
            self.name = "get_recommendations"
            self.description = _RECOMMENDATION_DESC
            self.args_schema: Type[BaseModel] = RecommendationInput
    
    def _run(
        self,
        vehicle_model: str,
        platform: str,
        systems: str,
        top_k: int = 5
    ) -> str:
        """Execute the tool."""
        try:
            # Load scenarios
            scenarios_file = Path("src/data/test_scenarios.json")
            if not scenarios_file.exists():
                return "Error: Test scenarios file not found"
            
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                candidates = data.get('scenarios', [])
            
            # Parse systems
            systems_list = [s.strip() for s in systems.split(',')]
            
            # Get recommendations
            recommender = create_recommender()
            recommendations = recommender.recommend_for_vehicle(
                vehicle_model=vehicle_model,
                platform=platform,
                systems=systems_list,
                components=[],
                candidates=candidates,
                top_k=top_k
            )
            
            # Filter by standards if provided in params (from agent detection)
            # Note: This is a simple filter - in production, use graph queries for standards
            if hasattr(self, '_standards_filter'):
                standards_filter = getattr(self, '_standards_filter', None)
                if standards_filter:
                    filtered_recs = []
                    for rec in recommendations:
                        rec_standards = rec.get('metadata', {}).get('applicable_standards', [])
                        if any(std.upper() in str(rec_standards).upper() for std in standards_filter):
                            filtered_recs.append(rec)
                    if filtered_recs:
                        recommendations = filtered_recs[:top_k]
            
            # Format response
            if not recommendations:
                return f"No recommendations found for {vehicle_model} {platform}"
            
            response = f"Found {len(recommendations)} test recommendations for {vehicle_model} ({platform}):\n\n"
            
            for i, rec in enumerate(recommendations[:top_k], 1):
                response += f"**{i}. {rec['test_name']}**\n"
                response += f"   • Score: {rec['score']:.3f}\n"
                response += f"   • Type: {rec['test_type']}\n"
                response += f"   • Duration: {rec['metadata'].get('estimated_duration_hours', 0):.1f} hours\n"
                response += f"   • Cost: £{rec['metadata'].get('estimated_cost_gbp', 0):,.0f}\n"
                
                # Add standards if available
                standards = rec.get('metadata', {}).get('applicable_standards', [])
                if standards:
                    response += f"   • Standards: {', '.join(standards)}\n"
                
                # Add explanation summary
                explain = rec.get('explain', {})
                if explain:
                    response += f"   • Explanation: High relevance based on semantic similarity and graph relationships\n"
                
                response += "\n"
            
            return response
        
        except Exception as e:
            logger.error(f"Error in recommendation tool: {e}")
            return f"Error getting recommendations: {str(e)}"


class ROIInput(BaseModel):
    """Input for ROI calculation tool."""
    baseline_count: int = Field(description="Number of baseline test scenarios")
    optimization_rate: float = Field(description="Expected optimization rate (0.0-1.0, e.g., 0.25 for 25%)")


_ROI_DESC = """
Calculate return on investment for test optimization.
Use this when the user asks about costs, savings, or ROI.
Input should include baseline_count (number of tests) and optimization_rate (0-1).
Example: baseline_count=100, optimization_rate=0.25
"""

class ROICalculationTool(BaseTool):
    """Tool for calculating ROI."""
    
    # Always define with type annotations for Pydantic compatibility
    name: str = "calculate_roi"
    description: str = _ROI_DESC
    args_schema: Type[BaseModel] = ROIInput
    
    def __init__(self, **kwargs):
        if LANGCHAIN_AVAILABLE:
            super().__init__(name="calculate_roi", description=_ROI_DESC, args_schema=ROIInput, **kwargs)
        else:
            super().__init__()
            self.name = "calculate_roi"
            self.description = _ROI_DESC
            self.args_schema: Type[BaseModel] = ROIInput
    
    def _run(
        self,
        baseline_count: int,
        optimization_rate: float = 0.25
    ) -> str:
        """Execute the tool."""
        try:
            # Load scenarios
            scenarios_file = Path("src/data/test_scenarios.json")
            if not scenarios_file.exists():
                return "Error: Test scenarios file not found"
            
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                scenarios = data.get('scenarios', [])
            
            # Get subsets
            baseline = scenarios[:baseline_count]
            optimized_count = int(baseline_count * (1 - optimization_rate))
            optimized = scenarios[:optimized_count]
            
            # Calculate ROI
            calculator = create_roi_calculator()
            roi_analysis = calculator.calculate_roi(
                baseline_scenarios=baseline,
                optimized_scenarios=optimized,
                duplicates_eliminated=[],
                implementation_cost_gbp=50000.0,
                analysis_period_years=3
            )
            
            # Format response
            response = f"""ROI Analysis Results:

Baseline: {roi_analysis.baseline_num_tests} tests costing £{roi_analysis.baseline_total_cost_gbp:,.0f}
Optimized: {roi_analysis.optimized_num_tests} tests costing £{roi_analysis.optimized_total_cost_gbp:,.0f}

Annual Savings: £{roi_analysis.cost_savings_gbp:,.0f}
Time Saved: {roi_analysis.time_savings_hours:,.0f} hours
Tests Eliminated: {roi_analysis.tests_eliminated}

ROI: {roi_analysis.roi_percent:.1f}%
Payback Period: {roi_analysis.payback_period_months:.1f} months

The system will pay for itself in less than {roi_analysis.payback_period_months:.0f} months!
"""
            
            return response
        
        except Exception as e:
            logger.error(f"Error in ROI tool: {e}")
            return f"Error calculating ROI: {str(e)}"


class MetricsInput(BaseModel):
    """Input for metrics tool."""
    num_scenarios: int = Field(default=50, description="Number of scenarios to analyze")


_METRICS_DESC = """
Get comprehensive test suite metrics including coverage, efficiency, quality, and compliance.
Use this when the user asks about metrics, performance, or quality.
Input should include num_scenarios (number of scenarios to analyze).
Example: num_scenarios=50
"""

class MetricsTool(BaseTool):
    """Tool for calculating metrics."""
    
    # Always define with type annotations for Pydantic compatibility
    name: str = "get_metrics"
    description: str = _METRICS_DESC
    args_schema: Type[BaseModel] = MetricsInput
    
    def __init__(self, **kwargs):
        if LANGCHAIN_AVAILABLE:
            super().__init__(name="get_metrics", description=_METRICS_DESC, args_schema=MetricsInput, **kwargs)
        else:
            super().__init__()
            self.name = "get_metrics"
            self.description = _METRICS_DESC
            self.args_schema: Type[BaseModel] = MetricsInput
    
    def _run(self, num_scenarios: int = 50) -> str:
        """Execute the tool."""
        try:
            # Load scenarios
            scenarios_file = Path("src/data/test_scenarios.json")
            if not scenarios_file.exists():
                return "Error: Test scenarios file not found"
            
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                scenarios = data.get('scenarios', [])[:num_scenarios]
            
            # Calculate metrics
            tracker = create_metrics_tracker()
            
            all_components = ['Battery', 'Motor', 'Inverter', 'BMS', 'Charger', 'Thermal']
            all_systems = ['Powertrain', 'Battery', 'ADAS', 'Chassis', 'Thermal']
            all_platforms = ['EV', 'HEV', 'ICE']
            required_standards = ['UNECE_R100', 'ISO_6469', 'SAE_J2929', 'ISO_26262']
            
            summary = tracker.calculate_all_metrics(
                scenarios=scenarios,
                all_components=all_components,
                all_systems=all_systems,
                all_platforms=all_platforms,
                required_standards=required_standards,
                num_duplicates=5,
                optimization_rate=0.25
            )
            
            # Format response
            response = f"""Test Suite Metrics (analyzing {num_scenarios} scenarios):

Overall Score: {summary.overall_score:.1f}/100

Coverage:
- Components: {summary.coverage.component_coverage_percent:.1f}%
- Systems: {summary.coverage.system_coverage_percent:.1f}%
- Platforms: {summary.coverage.platform_coverage_percent:.1f}%
- Regulatory: {summary.coverage.regulatory_coverage_percent:.1f}%

Efficiency:
- Total Tests: {summary.efficiency.total_tests}
- Duplicate Rate: {summary.efficiency.duplicate_rate_percent:.1f}%
- Optimization Rate: {summary.efficiency.optimization_rate_percent:.1f}%
- Efficiency Score: {summary.efficiency.efficiency_score:.1f}/100

Quality:
- Pass Rate: {summary.quality.pass_rate_percent:.1f}%
- Critical Pass Rate: {summary.quality.critical_pass_rate_percent:.1f}%

Compliance:
- Standards Coverage: {summary.compliance.standards_coverage_percent:.1f}%
- Compliance Score: {summary.compliance.compliance_score:.1f}/100
"""
            
            if summary.compliance.compliance_gaps:
                response += f"\nCompliance Gaps: {', '.join(summary.compliance.compliance_gaps)}"
            
            return response
        
        except Exception as e:
            logger.error(f"Error in metrics tool: {e}")
            return f"Error calculating metrics: {str(e)}"


class ScenarioSearchInput(BaseModel):
    """Input for scenario search tool."""
    platform: Optional[str] = Field(default=None, description="Platform filter (EV, HEV, ICE)")
    test_type: Optional[str] = Field(default=None, description="Test type filter")
    limit: int = Field(default=10, description="Maximum number of results")


_SCENARIO_SEARCH_DESC = """
Search and list test scenarios with optional filters.
Use this when the user wants to browse or search for specific scenarios.
Input can include platform, test_type, and limit.
Example: platform='EV', test_type='performance', limit=10
"""

class ScenarioSearchTool(BaseTool):
    """Tool for searching scenarios."""
    
    # Always define with type annotations for Pydantic compatibility
    name: str = "search_scenarios"
    description: str = _SCENARIO_SEARCH_DESC
    args_schema: Type[BaseModel] = ScenarioSearchInput
    
    def __init__(self, **kwargs):
        if LANGCHAIN_AVAILABLE:
            super().__init__(name="search_scenarios", description=_SCENARIO_SEARCH_DESC, args_schema=ScenarioSearchInput, **kwargs)
        else:
            super().__init__()
            self.name = "search_scenarios"
            self.description = _SCENARIO_SEARCH_DESC
            self.args_schema: Type[BaseModel] = ScenarioSearchInput
    
    def _run(
        self,
        platform: Optional[str] = None,
        test_type: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Execute the tool."""
        try:
            # Load scenarios
            scenarios_file = Path("src/data/test_scenarios.json")
            if not scenarios_file.exists():
                return "Error: Test scenarios file not found"
            
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                scenarios = data.get('scenarios', [])
            
            # Apply filters
            filtered = scenarios
            
            if platform:
                filtered = [s for s in filtered if platform in s.get('applicable_platforms', [])]
            
            if test_type:
                filtered = [s for s in filtered if s.get('test_type') == test_type]
            
            filtered = filtered[:limit]
            
            # Format response
            if not filtered:
                return f"No scenarios found with the specified filters"
            
            response = f"Found {len(filtered)} scenarios"
            if platform:
                response += f" for {platform}"
            if test_type:
                response += f" of type {test_type}"
            response += ":\n\n"
            
            for i, scenario in enumerate(filtered, 1):
                response += f"{i}. {scenario['test_name']}\n"
                response += f"   ID: {scenario['scenario_id']}\n"
                response += f"   Type: {scenario['test_type']}\n"
                response += f"   Platforms: {', '.join(scenario.get('applicable_platforms', []))}\n"
                response += f"   Duration: {scenario.get('estimated_duration_hours', 0):.1f}h\n"
                response += f"   Cost: £{scenario.get('estimated_cost_gbp', 0):,.0f}\n\n"
            
            return response
        
        except Exception as e:
            logger.error(f"Error in scenario search tool: {e}")
            return f"Error searching scenarios: {str(e)}"


def get_vta_tools() -> List[BaseTool]:
    """
    Get all VTA tools for the agent.
    
    Returns:
        List of BaseTool instances
    """
    return [
        RecommendationTool(),
        ROICalculationTool(),
        MetricsTool(),
        ScenarioSearchTool()
    ]


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VTA TOOLS TEST")
    print("=" * 70)
    
    # Get tools
    print("\n[1/3] Getting VTA tools...")
    tools = get_vta_tools()
    print(f"[OK] Loaded {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:60]}...")
    
    # Test recommendation tool
    print("\n[2/3] Testing recommendation tool...")
    rec_tool = tools[0]
    result = rec_tool._run(
        vehicle_model="Ariya",
        platform="EV",
        systems="Battery,Powertrain",
        top_k=3
    )
    print(f"[OK] Result:\n{result[:300]}...")
    
    # Test ROI tool
    print("\n[3/3] Testing ROI tool...")
    roi_tool = tools[1]
    result = roi_tool._run(baseline_count=50, optimization_rate=0.25)
    print(f"[OK] Result:\n{result[:300]}...")
    
    print("\n[OK] VTA tools test complete")

