# 🚗 Virtual Testing Assistant (VTA) - Complete Project Overview

## 📋 Executive Summary

**Virtual Testing Assistant (VTA)** is an enterprise-grade AI system for automotive test optimization, developed as a Knowledge Transfer Partnership (KTP) project between **Nissan NTCE** and **Cranfield University**.

### Core Purpose
Optimize automotive testing workflows by:
- Reducing physical testing costs by 30-50%
- Accelerating test planning by 40-60%
- Ensuring 95%+ regulatory compliance
- Providing real-time ROI tracking and governance

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Streamlit Dashboard (Frontend)                  │
│         Port: 8501 | Interactive UI + Visualizations        │
└──────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (API Layer)                     │
│         Port: 8000 | REST API + LangChain Agent              │
└──┬────────┬─────────┬──────────┬───────────┬────────────────┘
   │        │         │          │           │
   ▼        ▼         ▼          ▼           ▼
┌─────┐ ┌──────┐ ┌─────────┐ ┌──────┐ ┌──────────┐
│Neo4j│ │pgvec │ │ Redis   │ │Torch │ │Sentence  │
│ KG  │ │tor   │ │ Cache   │ │ ML   │ │Transform │
└─────┘ └──────┘ └─────────┘ └──────┘ └──────────┘
```

### Technology Stack

#### **Frontend**
- **Streamlit** - Interactive dashboard with futuristic white theme
- **Plotly** - Interactive charts and visualizations
- **Custom CSS** - Glass morphism effects, modern UI

#### **Backend**
- **FastAPI** - High-performance REST API framework
- **Python 3.11** - Core language
- **Pydantic** - Data validation and settings

#### **AI/ML**
- **PyTorch** - Deep learning framework
- **SentenceTransformers** - Text embeddings (`all-mpnet-base-v2`)
- **HDBSCAN** - Density-based clustering for duplicate detection
- **LangChain** - LLM orchestration and conversational agents
- **HuggingFace Transformers** - Local LLM support

#### **Databases**
- **Neo4j 5.14** - Graph database for knowledge representation
- **PostgreSQL + pgvector** - Vector similarity search
- **Redis** - Caching and session management

#### **Semantic Web**
- **RDFLib** - RDF graph manipulation
- **PyShacl** - SHACL validation
- **OWL/SPARQL** - Ontology and query standards

#### **Simulation**
- **CARLA** - Autonomous driving simulation
- **SUMO** - Traffic simulation

#### **DevOps**
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD automation
- **Pytest** - Comprehensive testing

---

## 📁 Project Structure

```
DRIVING-TEST-SIMULATION/
├── src/
│   ├── api/                    # FastAPI REST API
│   │   └── main.py             # API endpoints, routes
│   │
│   ├── dashboard/              # Streamlit Frontend
│   │   ├── app.py              # Main dashboard application
│   │   ├── components.py       # Custom UI components
│   │   └── futuristic_theme.css # Advanced CSS styling
│   │
│   ├── ai/                     # AI/ML Components
│   │   ├── recommender.py      # Test recommendation engine
│   │   ├── duplicate_detector.py # Duplicate test detection
│   │   ├── embeddings.py       # Text embedding generation
│   │   └── similarity.py       # Similarity calculations
│   │
│   ├── graph/                  # Knowledge Graph
│   │   ├── neo4j_connector.py  # Neo4j database connection
│   │   ├── graph_operations.py # Graph queries and operations
│   │   ├── ontology_design.py  # Ontology structure
│   │   ├── semantic_bridge.py  # RDF/OWL integration
│   │   └── jsonld.py          # JSON-LD processing
│   │
│   ├── vector/                 # Vector Database
│   │   └── pgvector_ops.py    # pgvector operations
│   │
│   ├── business/               # Business Logic
│   │   ├── roi_calculator.py  # ROI analysis and calculations
│   │   ├── metrics.py         # KPI tracking and metrics
│   │   ├── governance.py      # KTP governance reporting
│   │   └── report_generator.py # Report generation
│   │
│   ├── sim/                    # Simulation Export
│   │   ├── scenario_converter.py # VTA to simulation format
│   │   ├── carla_exporter.py  # CARLA export
│   │   ├── sumo_exporter.py   # SUMO export
│   │   └── base.py            # Base simulation classes
│   │
│   ├── orchestrators/          # LangChain Agents
│   │   ├── conversation_chain.py # Conversational AI
│   │   ├── vta_tools.py       # Agent tools
│   │   └── llm_setup.py       # LLM configuration
│   │
│   ├── config/                 # Configuration
│   │   └── settings.py        # Pydantic settings
│   │
│   └── data/                   # Data Management
│       ├── synthetic_data_generator.py # Test data generation
│       └── nissan_vehicle_models.py    # Vehicle model definitions
│
├── tests/                      # Test Suite
│   ├── test_api.py            # API tests
│   ├── test_ai.py             # AI component tests
│   ├── test_business.py       # Business logic tests
│   ├── test_graph.py          # Graph operations tests
│   └── test_sim.py            # Simulation tests
│
├── scripts/                    # Utility Scripts
│   ├── deploy.sh/.ps1         # Deployment automation
│   ├── setup_conda.sh/.ps1    # Conda environment setup
│   └── run_phase2_ingestion.py # Neo4j data ingestion
│
├── semantic/                   # Semantic Web
│   └── ontologies/            # OWL ontologies and SHACL shapes
│
├── sim_output/                 # Generated Simulation Files
│   ├── carla/                 # CARLA Python scripts
│   └── sumo/                  # SUMO XML configurations
│
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Multi-stage Docker build
├── requirements.txt           # Python dependencies
├── environment.yml            # Conda environment
└── README.md                  # Main documentation
```

---

## 🔄 System Workflow

### 1. **Test Recommendation Flow**

```
User Input (Vehicle Model, Platform, Systems, Components)
    ↓
FastAPI Endpoint: /api/v1/recommendations
    ↓
AI Recommender Engine
    ├── Semantic Search (SentenceTransformers)
    ├── Graph Proximity (Neo4j)
    ├── Rule-Based Filtering
    └── Historical Patterns
    ↓
Ensemble Scoring & Ranking
    ↓
Top-K Recommendations with Explanations
    ↓
Streamlit Dashboard Display
```

### 2. **ROI Analysis Flow**

```
Baseline vs Optimized Scenarios
    ↓
ROI Calculator
    ├── Cost Calculation
    ├── Time Savings
    ├── Duplicate Elimination
    └── Multi-year Projections
    ↓
Financial Metrics
    ├── ROI Percentage
    ├── Payback Period
    ├── Cost Savings
    └── NPV Calculation
    ↓
Dashboard Visualization
```

### 3. **Simulation Export Flow**

```
VTA Test Scenario
    ↓
Scenario Converter
    ├── Platform Detection (CARLA/SUMO)
    ├── Parameter Mapping
    └── Format Conversion
    ↓
Simulation Exporter
    ├── CARLA: Python Script + OpenScenario XML
    └── SUMO: XML Configuration Files
    ↓
sim_output/ Directory
```

### 4. **Knowledge Graph Flow**

```
Test Scenarios Data
    ↓
Neo4j Ingestion
    ├── Node Creation (Vehicles, Components, Tests)
    ├── Relationship Mapping
    └── Property Assignment
    ↓
Graph Queries
    ├── Cypher Queries
    ├── Graph Algorithms
    └── Path Finding
    ↓
Semantic Reasoning
    ├── RDF/OWL Ontologies
    ├── SPARQL Queries
    └── SHACL Validation
```

---

## 🎯 Key Features & Components

### 1. **AI-Powered Recommendations** (`src/ai/recommender.py`)

**Purpose**: Intelligent test scenario recommendations

**Methods**:
- **Semantic Similarity**: Uses SentenceTransformers to find similar tests
- **Graph Proximity**: Leverages Neo4j relationships
- **Rule-Based**: Applies business rules and constraints
- **Historical Patterns**: Considers past test selections

**Output**: Ranked recommendations with explainable scores

### 2. **Duplicate Detection** (`src/ai/duplicate_detector.py`)

**Purpose**: Identify redundant test scenarios

**Methods**:
- **HDBSCAN Clustering**: Density-based clustering
- **Multi-dimensional Similarity**: Combines semantic, graph, and metadata
- **Threshold-based Filtering**: Configurable similarity thresholds

**Output**: Duplicate groups and elimination recommendations

### 3. **Knowledge Graph** (`src/graph/`)

**Purpose**: Represent automotive knowledge as a graph

**Components**:
- **Neo4j Connector**: Database connection and operations
- **Graph Operations**: Cypher queries, path finding
- **Ontology Design**: Vehicle, component, test relationships
- **Semantic Bridge**: RDF/OWL integration

**Data Model**:
- **Nodes**: Vehicles, Components, Systems, Tests, Standards
- **Relationships**: HAS_COMPONENT, REQUIRES_TEST, COMPLIES_WITH

### 4. **Vector Search** (`src/vector/pgvector_ops.py`)

**Purpose**: Fast semantic similarity search

**Technology**: PostgreSQL + pgvector extension

**Features**:
- Embedding storage
- Cosine similarity search
- Hybrid search (vector + metadata)

### 5. **ROI Calculator** (`src/business/roi_calculator.py`)

**Purpose**: Calculate financial impact of test optimization

**Metrics**:
- **ROI Percentage**: Return on investment
- **Payback Period**: Months to recover costs
- **Cost Savings**: Total GBP saved
- **NPV**: Net present value

**Inputs**:
- Baseline scenarios
- Optimized scenarios
- Implementation costs
- Analysis period

### 6. **Metrics Tracker** (`src/business/metrics.py`)

**Purpose**: Track test coverage and quality metrics

**KPIs**:
- **Coverage**: Component, system, platform, regulatory
- **Efficiency**: Test execution efficiency
- **Quality**: Test quality scores
- **Compliance**: Regulatory compliance percentage

### 7. **Governance Reporter** (`src/business/governance.py`)

**Purpose**: KTP project governance and reporting

**Features**:
- **Status Tracking**: Project progress, phases, deliverables
- **LMC Reports**: Quarterly Local Management Committee reports
- **Risk Management**: Issue tracking and mitigation

### 8. **Simulation Export** (`src/sim/`)

**Purpose**: Export test scenarios to simulation platforms

**Platforms**:
- **CARLA**: Python scripts, OpenScenario XML
- **SUMO**: XML configuration files

**Features**:
- Automated format conversion
- Parameter mapping
- Scenario validation

### 9. **Conversational AI** (`src/orchestrators/`)

**Purpose**: Natural language interaction with VTA

**Technology**: LangChain + Local LLM (HuggingFace)

**Features**:
- Multi-turn conversations
- Tool routing (recommendations, ROI, metrics)
- Context-aware responses
- Offline inference support

### 10. **Dashboard** (`src/dashboard/`)

**Purpose**: Interactive web interface

**Pages**:
1. **Dashboard**: Overview metrics and charts
2. **Recommendations**: Test recommendation interface
3. **ROI Analysis**: Financial impact analysis
4. **Metrics**: Coverage and quality tracking
5. **Governance**: KTP project status
6. **Simulation Export**: Scenario export interface
7. **Scenarios**: Browse and filter test scenarios

**Features**:
- Futuristic white theme
- Glass morphism effects
- Interactive Plotly charts
- Real-time API integration

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/v1/recommendations` | POST | Get test recommendations |
| `/api/v1/roi` | POST | Calculate ROI |
| `/api/v1/metrics` | POST | Calculate metrics |
| `/api/v1/governance/status` | GET | Get governance status |
| `/api/v1/governance/lmc-report` | POST | Generate LMC report |
| `/api/v1/simulation/export` | POST | Export to simulation |
| `/api/v1/scenarios` | GET | List scenarios |
| `/api/v1/scenarios/{id}` | GET | Get scenario details |

### Example Request

```python
POST /api/v1/recommendations
{
  "vehicle_model": "Ariya",
  "platform": "EV",
  "systems": ["Powertrain", "Battery"],
  "components": ["High_Voltage_Battery"],
  "top_k": 10
}
```

---

## 🗄️ Database Schema

### Neo4j Graph Model

**Node Types**:
- `Vehicle` - Vehicle models (Ariya, Leaf, etc.)
- `Component` - Vehicle components (Battery, Motor, etc.)
- `System` - Vehicle systems (Powertrain, Chassis, etc.)
- `Test` - Test scenarios
- `Standard` - Regulatory standards (ISO, UN, etc.)
- `Platform` - Platform types (EV, HEV, ICE)

**Relationship Types**:
- `HAS_COMPONENT` - Vehicle → Component
- `HAS_SYSTEM` - Vehicle → System
- `REQUIRES_TEST` - Component/System → Test
- `COMPLIES_WITH` - Test → Standard
- `APPLICABLE_TO` - Test → Platform

### PostgreSQL Schema

**Tables**:
- `test_scenarios` - Test scenario metadata
- `embeddings` - Vector embeddings (pgvector)
- `metrics` - Historical metrics

---

## 🚀 Deployment

### Docker Compose Services

1. **postgres** - PostgreSQL + pgvector (Port 5432)
2. **neo4j** - Neo4j Graph DB (Ports 7687, 7474)
3. **redis** - Redis Cache (Port 6379)
4. **api** - FastAPI Backend (Port 8000)
5. **dashboard** - Streamlit Frontend (Port 8501)
6. **init-data** - One-time data initialization

### Quick Start

```bash
# Docker Deployment
docker compose up -d

# Conda Local Development
conda env create -f environment.yml
conda activate vta
docker compose up -d postgres neo4j redis
uvicorn src.api.main:app --reload
streamlit run src/dashboard/app.py
```

---

## 📊 Data Flow

### Input Data
- Vehicle models and configurations
- Test scenario definitions
- Historical test data
- Regulatory requirements

### Processing
- AI-powered recommendation
- Graph-based reasoning
- Vector similarity search
- Business logic calculations

### Output
- Test recommendations
- ROI analysis
- Metrics dashboards
- Simulation exports
- Governance reports

---

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Graph Tests**: Neo4j operations
- **Business Logic Tests**: ROI, metrics calculations

### Run Tests
```bash
pytest                    # All tests
pytest tests/test_api.py  # API tests
pytest --cov=src          # With coverage
```

---

## 📈 Development Phases

The project was developed in **10 phases**:

1. **Phase 1**: Config + Data + Synthetic Generation
2. **Phase 2**: Neo4j Knowledge Graph
3. **Phase 3**: Semantic Web (RDF/OWL/SPARQL/SHACL)
4. **Phase 4**: pgvector + Embeddings + Search
5. **Phase 5**: AI Recommender + Deduplication
6. **Phase 6**: CARLA/SUMO Simulation Export
7. **Phase 7**: Business Impact + ROI + Governance
8. **Phase 8**: FastAPI + Streamlit Dashboard
9. **Phase 9**: LangChain + Local LLM Agent
10. **Phase 10**: Docker + CI/CD + Deployment

**Status**: ✅ **PRODUCTION READY**

---

## 🔐 Configuration

### Environment Variables

**Database**:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`

**Application**:
- `API_HOST`, `API_PORT`, `API_WORKERS`
- `LOG_LEVEL`
- `USE_MOCK_LLM`

**Business**:
- `HOURLY_RATE_GBP`
- `PHYSICAL_TEST_MULTIPLIER`
- `SIMULATION_COST_FACTOR`

---

## 📚 Key Documentation Files

- **README.md** - Main project documentation
- **QUICK_START.md** - Quick deployment guide
- **DEPLOYMENT.md** - Deployment instructions
- **DOCKER_DEPLOYMENT_GUIDE.md** - Docker setup
- **CONDA_SETUP_GUIDE.md** - Conda environment setup
- **FRONTEND_REDESIGN_PLAN.md** - Frontend architecture
- **REACT_MIGRATION_GUIDE.md** - React migration guide

---

## 🎯 Business Value

### Cost Reduction
- **30-50% reduction** in physical testing costs
- Intelligent duplicate detection
- Simulation-first approach

### Time Savings
- **40-60% faster** test planning
- Automated recommendations
- Streamlined workflows

### Compliance
- **95%+ coverage** of regulatory requirements
- Automated compliance checking
- Standard tracking

### ROI Tracking
- Real-time financial metrics
- Multi-year projections
- Governance reporting

---

## 🔮 Future Enhancements

### Potential Improvements
- React/Next.js frontend migration
- Advanced ML models
- Real-time collaboration
- Mobile app support
- Enhanced visualization

---

## 📞 Contact & Support

- **Developer**: Naga Sri Ram Nani
- **Email**: nagasriramnani@gmail.com
- **GitHub**: https://github.com/nagasriramnani
- **Organization**: Nissan NTCE × Cranfield University

---

**Built with ❤️ for the future of automotive testing**

