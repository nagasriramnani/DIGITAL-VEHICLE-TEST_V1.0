"""
Tests for Phase 8: API + Dashboard.
"""
import pytest
from fastapi.testclient import TestClient
import json

from src.api.main import app


class TestAPIBasics:
    """Test basic API functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
    
    def test_docs_available(self, client):
        """Test API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema


class TestRecommendationsAPI:
    """Test recommendations API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_request(self):
        """Create sample recommendation request."""
        return {
            "vehicle_model": "Ariya",
            "platform": "EV",
            "systems": ["Battery", "Powertrain"],
            "components": ["High_Voltage_Battery", "Electric_Motor"],
            "top_k": 5
        }
    
    def test_recommendations_endpoint(self, client, sample_request):
        """Test recommendations endpoint."""
        response = client.post("/api/v1/recommendations", json=sample_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "count" in data
        assert data["count"] <= sample_request["top_k"]
    
    def test_recommendations_validation(self, client):
        """Test request validation."""
        invalid_request = {
            "vehicle_model": "Ariya",
            "platform": "EV",
            # Missing required fields
        }
        
        response = client.post("/api/v1/recommendations", json=invalid_request)
        assert response.status_code == 422  # Validation error


class TestROIAPI:
    """Test ROI analysis API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_request(self):
        """Create sample ROI request."""
        baseline = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'estimated_duration_hours': 24.0,
                'complexity_score': 6,
                'certification_required': False
            }
            for i in range(10)
        ]
        
        optimized = baseline[:7]  # 30% reduction
        
        return {
            "baseline_scenarios": baseline,
            "optimized_scenarios": optimized,
            "implementation_cost_gbp": 50000.0,
            "analysis_period_years": 3
        }
    
    def test_roi_endpoint(self, client, sample_request):
        """Test ROI calculation endpoint."""
        response = client.post("/api/v1/roi", json=sample_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "roi_analysis" in data
        assert "summary" in data
        assert "roi_percent" in data["summary"]
        assert "payback_months" in data["summary"]
    
    def test_roi_calculation_accuracy(self, client, sample_request):
        """Test ROI calculation is reasonable."""
        response = client.post("/api/v1/roi", json=sample_request)
        
        data = response.json()
        summary = data["summary"]
        
        # Verify ROI metrics are reasonable
        assert summary["roi_percent"] > 0
        assert summary["payback_months"] > 0
        assert summary["cost_savings_gbp"] > 0


class TestMetricsAPI:
    """Test metrics API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_request(self):
        """Create sample metrics request."""
        scenarios = [
            {
                'scenario_id': f'TEST-{i:03d}',
                'target_components': ['Battery', 'Motor'],
                'target_systems': ['Powertrain'],
                'applicable_platforms': ['EV'],
                'regulatory_standards': ['UNECE_R100'],
                'estimated_duration_hours': 24.0,
                'estimated_cost_gbp': 8000.0,
                'historical_results': [{'passed': True}]
            }
            for i in range(10)
        ]
        
        return {
            "scenarios": scenarios,
            "all_components": ['Battery', 'Motor', 'Inverter'],
            "all_systems": ['Powertrain', 'Battery'],
            "all_platforms": ['EV', 'HEV', 'ICE'],
            "required_standards": ['UNECE_R100', 'ISO_6469'],
            "num_duplicates": 2,
            "optimization_rate": 0.2
        }
    
    def test_metrics_endpoint(self, client, sample_request):
        """Test metrics calculation endpoint."""
        response = client.post("/api/v1/metrics", json=sample_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics_summary" in data
        assert "overall_score" in data
        assert 0 <= data["overall_score"] <= 100
    
    def test_metrics_structure(self, client, sample_request):
        """Test metrics response structure."""
        response = client.post("/api/v1/metrics", json=sample_request)
        
        data = response.json()
        metrics = data["metrics_summary"]
        
        assert "coverage" in metrics
        assert "efficiency" in metrics
        assert "quality" in metrics
        assert "compliance" in metrics


class TestGovernanceAPI:
    """Test governance API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_governance_status_endpoint(self, client):
        """Test governance status endpoint."""
        response = client.get("/api/v1/governance/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "project_health" in data
        assert "completion_percent" in data
    
    def test_lmc_report_endpoint(self, client):
        """Test LMC report generation endpoint."""
        response = client.post(
            "/api/v1/governance/lmc-report",
            params={"quarter": "Q1 2025"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "quarter" in data
        assert "project" in data
        assert "progress" in data


class TestScenarioAPI:
    """Test scenario management API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_get_scenarios_endpoint(self, client):
        """Test get scenarios endpoint."""
        response = client.get("/api/v1/scenarios")
        
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "total" in data
        assert "limit" in data
    
    def test_scenarios_pagination(self, client):
        """Test scenarios pagination."""
        response = client.get("/api/v1/scenarios?limit=5&offset=0")
        
        data = response.json()
        assert len(data["scenarios"]) <= 5
        assert data["limit"] == 5
        assert data["offset"] == 0
    
    def test_scenarios_filtering(self, client):
        """Test scenarios filtering."""
        response = client.get("/api/v1/scenarios?platform=EV")
        
        data = response.json()
        # All returned scenarios should include EV platform
        for scenario in data["scenarios"]:
            assert "EV" in scenario.get("applicable_platforms", [])
    
    def test_get_scenario_by_id(self, client):
        """Test get specific scenario."""
        # First get list of scenarios
        response = client.get("/api/v1/scenarios?limit=1")
        data = response.json()
        
        if data["scenarios"]:
            scenario_id = data["scenarios"][0]["scenario_id"]
            
            # Get specific scenario
            response = client.get(f"/api/v1/scenarios/{scenario_id}")
            assert response.status_code == 200
            
            scenario = response.json()
            assert scenario["scenario_id"] == scenario_id
    
    def test_get_nonexistent_scenario(self, client):
        """Test getting non-existent scenario."""
        response = client.get("/api/v1/scenarios/NONEXISTENT")
        assert response.status_code == 404


class TestSimulationAPI:
    """Test simulation export API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_vta_scenario(self):
        """Create sample VTA scenario."""
        return {
            'scenario_id': 'TEST-001',
            'test_name': 'Battery Test',
            'test_type': 'performance',
            'applicable_platforms': ['EV'],
            'environmental_conditions': {
                'ambient_temperature_celsius': 20.0,
                'road_surface_condition': 'dry'
            },
            'estimated_duration_hours': 2.0
        }
    
    def test_simulation_export_carla(self, client, sample_vta_scenario):
        """Test CARLA simulation export."""
        request = {
            "vta_scenario": sample_vta_scenario,
            "platform": "CARLA",
            "format": "python"
        }
        
        response = client.post("/api/v1/simulation/export", json=request)
        
        assert response.status_code == 200
        data = response.json()
        assert "file_path" in data
        assert data["platform"] == "CARLA"
    
    def test_simulation_export_sumo(self, client, sample_vta_scenario):
        """Test SUMO simulation export."""
        request = {
            "vta_scenario": sample_vta_scenario,
            "platform": "SUMO",
            "format": "xml"
        }
        
        response = client.post("/api/v1/simulation/export", json=request)
        
        assert response.status_code == 200
        data = response.json()
        assert "file_path" in data
        assert data["platform"] == "SUMO"


class TestStatsAPI:
    """Test statistics API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_stats_endpoint(self, client):
        """Test statistics endpoint."""
        response = client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_scenarios" in data
        assert "platforms" in data
        assert "test_types" in data
    
    def test_stats_accuracy(self, client):
        """Test statistics are reasonable."""
        response = client.get("/api/v1/stats")
        
        data = response.json()
        assert data["total_scenarios"] > 0
        assert data["avg_cost_gbp"] > 0
        assert data["avg_duration_hours"] > 0


class TestErrorHandling:
    """Test API error handling."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_422_validation_error(self, client):
        """Test validation error handling."""
        invalid_request = {
            "vehicle_model": "Ariya",
            # Missing required fields
        }
        
        response = client.post("/api/v1/recommendations", json=invalid_request)
        assert response.status_code == 422
    
    def test_500_server_error_handling(self, client):
        """Test server error handling."""
        # Test with invalid data that should cause server error
        invalid_roi_request = {
            "baseline_scenarios": [],  # Empty list might cause issues
            "optimized_scenarios": [],
            "implementation_cost_gbp": -1000  # Negative cost
        }
        
        response = client.post("/api/v1/roi", json=invalid_roi_request)
        # Should either validate (422) or handle gracefully (500)
        assert response.status_code in [422, 500]


class TestIntegration:
    """Integration tests for API workflow."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_end_to_end_recommendation_workflow(self, client):
        """Test complete recommendation workflow."""
        # 1. Get scenarios
        response = client.get("/api/v1/scenarios?limit=50&platform=EV")
        assert response.status_code == 200
        scenarios = response.json()["scenarios"]
        assert len(scenarios) > 0
        
        # 2. Get recommendations
        request = {
            "vehicle_model": "Ariya",
            "platform": "EV",
            "systems": ["Battery"],
            "components": ["High_Voltage_Battery"],
            "top_k": 5
        }
        
        response = client.post("/api/v1/recommendations", json=request)
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        assert len(recommendations) > 0
    
    def test_end_to_end_roi_workflow(self, client):
        """Test complete ROI analysis workflow."""
        # 1. Get scenarios
        response = client.get("/api/v1/scenarios?limit=20")
        scenarios = response.json()["scenarios"]
        
        # 2. Calculate ROI
        roi_request = {
            "baseline_scenarios": scenarios,
            "optimized_scenarios": scenarios[:15],  # 25% reduction
            "implementation_cost_gbp": 50000.0,
            "analysis_period_years": 3
        }
        
        response = client.post("/api/v1/roi", json=roi_request)
        assert response.status_code == 200
        
        roi_data = response.json()
        assert roi_data["summary"]["roi_percent"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

