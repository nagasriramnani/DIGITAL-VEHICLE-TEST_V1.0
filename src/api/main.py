"""
FastAPI backend for Virtual Testing Assistant.
Provides REST API endpoints for recommendations, ROI analysis, metrics, and more.
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.ai.recommender import create_recommender
from src.ai.duplicate_detector import create_duplicate_detector, HDBSCAN_AVAILABLE
from src.business.roi_calculator import create_roi_calculator
from src.business.metrics import create_metrics_tracker
from src.business.governance import create_governance_reporter
from src.business.report_generator import create_report_generator
from src.sim.scenario_converter import create_scenario_converter
from src.sim.carla_exporter import create_carla_exporter
from src.sim.sumo_exporter import create_sumo_exporter
from src.orchestrators.vta_agent import create_vta_agent

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Virtual Testing Assistant API",
    description="AI-powered test scenario optimization for automotive testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recommender = create_recommender()
roi_calculator = create_roi_calculator()
metrics_tracker = create_metrics_tracker()
governance_reporter = create_governance_reporter()
report_generator = create_report_generator()
scenario_converter = create_scenario_converter()

# Duplicate detector (optional if HDBSCAN available)
duplicate_detector = create_duplicate_detector() if HDBSCAN_AVAILABLE else None

# VTA Conversational Agent (reads configuration from .env)
vta_agent = create_vta_agent(use_mock=None)  # None = read from settings


# ============================================================================
# Pydantic Models
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, bool]


class RecommendationRequest(BaseModel):
    """Request for test recommendations."""
    vehicle_model: str = Field(..., description="Vehicle model name")
    platform: str = Field(..., description="Platform type (EV/HEV/ICE)")
    systems: List[str] = Field(..., description="Target vehicle systems")
    components: List[str] = Field(..., description="Target components")
    top_k: int = Field(10, description="Number of recommendations", ge=1, le=100)


class RecommendationResponse(BaseModel):
    """Response with recommendations."""
    recommendations: List[Dict[str, Any]]
    query: Dict[str, Any]
    count: int


class ROIRequest(BaseModel):
    """Request for ROI analysis."""
    baseline_scenarios: List[Dict[str, Any]]
    optimized_scenarios: List[Dict[str, Any]]
    implementation_cost_gbp: float = Field(50000.0, ge=0)
    analysis_period_years: int = Field(3, ge=1, le=10)


class ROIResponse(BaseModel):
    """Response with ROI analysis."""
    roi_analysis: Dict[str, Any]
    summary: Dict[str, float]


class MetricsRequest(BaseModel):
    """Request for metrics calculation."""
    scenarios: List[Dict[str, Any]]
    all_components: List[str]
    all_systems: List[str]
    all_platforms: List[str]
    required_standards: List[str]
    num_duplicates: int = Field(0, ge=0)
    optimization_rate: float = Field(0.0, ge=0.0, le=1.0)


class MetricsResponse(BaseModel):
    """Response with metrics summary."""
    metrics_summary: Dict[str, Any]
    overall_score: float


class SimulationExportRequest(BaseModel):
    """Request for simulation export."""
    vta_scenario: Dict[str, Any]
    platform: str = Field("CARLA", description="Simulation platform (CARLA/SUMO)")
    format: str = Field("python", description="Export format")


class SimulationExportResponse(BaseModel):
    """Response with export file path."""
    file_path: str
    platform: str
    format: str


class ChatRequest(BaseModel):
    """Request for conversational agent."""
    message: str = Field(..., description="User's message/query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class ChatResponse(BaseModel):
    """Response from conversational agent."""
    response: str
    tool_used: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    status: str


# ============================================================================
# API Routes
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Virtual Testing Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services={
            "recommender": recommender is not None,
            "roi_calculator": roi_calculator is not None,
            "metrics_tracker": metrics_tracker is not None,
            "governance_reporter": governance_reporter is not None,
            "duplicate_detector": duplicate_detector is not None,
            "hdbscan_available": HDBSCAN_AVAILABLE
        }
    )


@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get test recommendations for a vehicle.
    
    Returns top-k recommended test scenarios based on vehicle configuration.
    """
    try:
        # Load test scenarios (in production, this would query a database)
        scenarios_file = Path("src/data/test_scenarios.json")
        if not scenarios_file.exists():
            raise HTTPException(status_code=404, detail="Test scenarios not found")
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            candidates = data.get('scenarios', [])
        
        # Get recommendations
        recommendations = recommender.recommend_for_vehicle(
            vehicle_model=request.vehicle_model,
            platform=request.platform,
            systems=request.systems,
            components=request.components,
            candidates=candidates,
            top_k=request.top_k
        )
        
        return RecommendationResponse(
            recommendations=recommendations,
            query=request.dict(),
            count=len(recommendations)
        )
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/roi", response_model=ROIResponse)
async def calculate_roi(request: ROIRequest):
    """
    Calculate ROI analysis for test optimization.
    
    Compares baseline vs. optimized test scenarios and calculates financial impact.
    """
    try:
        roi_analysis = roi_calculator.calculate_roi(
            baseline_scenarios=request.baseline_scenarios,
            optimized_scenarios=request.optimized_scenarios,
            duplicates_eliminated=[],
            implementation_cost_gbp=request.implementation_cost_gbp,
            analysis_period_years=request.analysis_period_years
        )
        
        roi_dict = roi_analysis.to_dict()
        
        return ROIResponse(
            roi_analysis=roi_dict,
            summary={
                'roi_percent': roi_analysis.roi_percent,
                'payback_months': roi_analysis.payback_period_months,
                'cost_savings_gbp': roi_analysis.cost_savings_gbp,
                'tests_eliminated': roi_analysis.tests_eliminated
            }
        )
    
    except Exception as e:
        logger.error(f"Error calculating ROI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/metrics", response_model=MetricsResponse)
async def calculate_metrics(request: MetricsRequest):
    """
    Calculate comprehensive metrics for test scenarios.
    
    Returns coverage, efficiency, quality, and compliance metrics.
    """
    try:
        summary = metrics_tracker.calculate_all_metrics(
            scenarios=request.scenarios,
            all_components=request.all_components,
            all_systems=request.all_systems,
            all_platforms=request.all_platforms,
            required_standards=request.required_standards,
            num_duplicates=request.num_duplicates,
            optimization_rate=request.optimization_rate
        )
        
        return MetricsResponse(
            metrics_summary=summary.to_dict(),
            overall_score=summary.overall_score
        )
    
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/governance/status", response_model=Dict[str, Any])
async def get_governance_status():
    """
    Get KTP project status.
    
    Returns current project progress, deliverables, and health status.
    """
    try:
        status = governance_reporter.get_status_summary()
        return status
    
    except Exception as e:
        logger.error(f"Error getting governance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/governance/lmc-report", response_model=Dict[str, Any])
async def generate_lmc_report(
    quarter: str = Query(..., description="Quarter identifier (e.g., Q1 2025)"),
    roi_analysis: Optional[Dict[str, Any]] = None,
    metrics_summary: Optional[Dict[str, Any]] = None
):
    """
    Generate LMC report for governance.
    
    Creates a comprehensive quarterly report for Local Management Committee.
    """
    try:
        report = governance_reporter.generate_lmc_report(
            quarter=quarter,
            roi_analysis=roi_analysis,
            metrics_summary=metrics_summary
        )
        
        return report.to_dict()
    
    except Exception as e:
        logger.error(f"Error generating LMC report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/simulation/export", response_model=SimulationExportResponse)
async def export_simulation_scenario(request: SimulationExportRequest):
    """
    Export test scenario to simulation format.
    
    Converts VTA test scenario to CARLA or SUMO format.
    """
    try:
        # Convert VTA scenario to simulation format
        from src.sim.base import SimulationPlatform
        platform = SimulationPlatform.CARLA if request.platform.upper() == "CARLA" else SimulationPlatform.SUMO
        
        sim_scenario = scenario_converter.convert_from_vta(
            request.vta_scenario,
            platform=platform
        )
        
        # Export based on platform
        if request.platform.upper() == "CARLA":
            exporter = create_carla_exporter()
            if request.format == "python":
                file_path = exporter.export_python_script(sim_scenario)
            elif request.format == "openscenario":
                file_path = exporter.export_openscenario(sim_scenario)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        elif request.platform.upper() == "SUMO":
            exporter = create_sumo_exporter()
            files = exporter.export_scenario(sim_scenario)
            file_path = files['config']  # Return config file path
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")
        
        return SimulationExportResponse(
            file_path=file_path,
            platform=request.platform,
            format=request.format
        )
    
    except Exception as e:
        logger.error(f"Error exporting simulation scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/scenarios", response_model=Dict[str, Any])
async def get_scenarios(
    limit: int = Query(10, ge=1, le=500),
    offset: int = Query(0, ge=0),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    test_type: Optional[str] = Query(None, description="Filter by test type")
):
    """
    Get test scenarios with pagination and filtering.
    
    Returns a list of test scenarios from the database.
    """
    try:
        scenarios_file = Path("src/data/test_scenarios.json")
        if not scenarios_file.exists():
            raise HTTPException(status_code=404, detail="Test scenarios not found")
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            scenarios = data.get('scenarios', [])
        
        # Apply filters
        if platform:
            scenarios = [s for s in scenarios if platform in s.get('applicable_platforms', [])]
        
        if test_type:
            scenarios = [s for s in scenarios if s.get('test_type') == test_type]
        
        # Apply pagination
        total = len(scenarios)
        scenarios = scenarios[offset:offset + limit]
        
        return {
            'scenarios': scenarios,
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(scenarios)
        }
    
    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/scenarios/{scenario_id}", response_model=Dict[str, Any])
async def get_scenario(scenario_id: str):
    """
    Get a specific test scenario by ID.
    
    Returns detailed information about a single test scenario.
    """
    try:
        scenarios_file = Path("src/data/test_scenarios.json")
        if not scenarios_file.exists():
            raise HTTPException(status_code=404, detail="Test scenarios not found")
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            scenarios = data.get('scenarios', [])
        
        # Find scenario
        scenario = next((s for s in scenarios if s.get('scenario_id') == scenario_id), None)
        
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        
        return scenario
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_vta(request: ChatRequest):
    """
    Chat with VTA conversational agent.
    
    Ask questions in natural language and get intelligent responses with tool integration.
    Example: "Which tests validate Ariya battery safety for UNECE R100?"
    """
    try:
        # Process query through agent
        result = vta_agent.process_query(request.message)
        
        # Extract recommendations if tool was used
        recommendations = None
        if result.get('tool_used') == 'get_recommendations':
            # Parse tool response to extract recommendations
            tool_response = result.get('response', '')
            # Try to load actual recommendations from the tool
            try:
                scenarios_file = Path("src/data/test_scenarios.json")
                if scenarios_file.exists():
                    with open(scenarios_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        candidates = data.get('scenarios', [])
                    
                    # Extract params and get real recommendations
                    params = result.get('tool_params', {})
                    if params:
                        from src.ai.recommender import create_recommender
                        recommender = create_recommender()
                        recommendations = recommender.recommend_for_vehicle(
                            vehicle_model=params.get('vehicle_model', 'Ariya'),
                            platform=params.get('platform', 'EV'),
                            systems=params.get('systems', 'Battery').split(',') if isinstance(params.get('systems'), str) else params.get('systems', ['Battery']),
                            components=[],
                            candidates=candidates,
                            top_k=params.get('top_k', 5)
                        )
            except Exception as e:
                logger.warning(f"Could not extract recommendations: {e}")
        
        return ChatResponse(
            response=result.get('conversational_response') or result.get('response', ''),
            tool_used=result.get('tool_used'),
            tool_params=result.get('tool_params'),
            recommendations=recommendations,
            status=result.get('status', 'success')
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats", response_model=Dict[str, Any])
async def get_statistics():
    """
    Get system statistics.
    
    Returns aggregate statistics about test scenarios, coverage, etc.
    """
    try:
        scenarios_file = Path("src/data/test_scenarios.json")
        if not scenarios_file.exists():
            return {"error": "Test scenarios not found"}
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            scenarios = data.get('scenarios', [])
        
        # Calculate statistics
        platforms = {}
        test_types = {}
        
        for scenario in scenarios:
            # Count platforms
            for platform in scenario.get('applicable_platforms', []):
                platforms[platform] = platforms.get(platform, 0) + 1
            
            # Count test types
            test_type = scenario.get('test_type', 'unknown')
            test_types[test_type] = test_types.get(test_type, 0) + 1
        
        return {
            'total_scenarios': len(scenarios),
            'platforms': platforms,
            'test_types': test_types,
            'avg_cost_gbp': sum(s.get('estimated_cost_gbp', 0) for s in scenarios) / len(scenarios) if scenarios else 0,
            'avg_duration_hours': sum(s.get('estimated_duration_hours', 0) for s in scenarios) / len(scenarios) if scenarios else 0
        }
    
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("Starting Virtual Testing Assistant API")
    print("=" * 70)
    print("\n📡 API Server starting...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Health: http://localhost:8000/health")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

