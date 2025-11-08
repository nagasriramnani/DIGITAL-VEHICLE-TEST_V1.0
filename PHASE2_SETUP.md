# Phase 2: Neo4j Setup Guide

## Overview
Phase 2 implements the Knowledge Graph using Neo4j. To use the graph operations, you need to have Neo4j installed and running.

## Quick Start (Docker - Recommended)

The easiest way to run Neo4j is using Docker:

```bash
# Pull Neo4j image
docker pull neo4j:5.15-community

# Run Neo4j container
docker run -d \
  --name vta-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/please_change_me \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.15-community

# Wait ~30 seconds for Neo4j to start

# Check if running
docker ps | grep vta-neo4j
```

### Access Neo4j Browser
Open http://localhost:7474 in your browser:
- Username: `neo4j`
- Password: `please_change_me`

## Alternative: Install Locally

### Windows
1. Download Neo4j Desktop from https://neo4j.com/download/
2. Install and launch Neo4j Desktop
3. Create a new project and database
4. Set password to `please_change_me` (or update `.env`)
5. Start the database

### Linux/Mac
```bash
# Using Homebrew (Mac)
brew install neo4j
neo4j start

# Or download from https://neo4j.com/download-center/
```

## Configuration

Update your `.env` file:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=please_change_me
```

## Verify Installation

```bash
# Test connection
python -c "from src.graph.neo4j_connector import get_connector; print(get_connector().health_check())"
```

Expected output:
```python
{'status': 'healthy', 'node_count': 0, 'relationship_count': 0, ...}
```

## Running Phase 2 Operations

Once Neo4j is running:

### 1. Create Schema
```bash
python -c "from src.graph.graph_operations import create_schema; create_schema()"
```

### 2. Ingest Synthetic Data
```bash
python -c "from src.graph.graph_operations import ingest_synthetic; print(ingest_synthetic())"
```

### 3. Run Tests
```bash
# Run all Phase 2 tests
pytest tests/test_graph.py -v

# Run only tests that don't need Neo4j
pytest tests/test_graph.py::TestOntologyDesign -v
```

## Expected Results

After ingestion, you should have:
- ~8 vehicle models
- ~60 components
- ~500 test scenarios
- ~9 vehicle systems
- ~3 platforms
- ~6 test types
- ~Thousands of relationships

## Querying the Graph

### Cypher Examples

```cypher
// Count nodes by label
MATCH (n) RETURN labels(n)[0] as label, count(*) as count ORDER BY count DESC;

// Get tests for Ariya EV
MATCH (v:Vehicle {name: 'Ariya'})-[:REQUIRES_TEST]->(t:TestScenario)
RETURN t.test_name, t.test_type, t.estimated_duration_hours
LIMIT 10;

// Find critical components
MATCH (c:Component {criticality: 'critical'})
RETURN c.name, c.criticality
LIMIT 10;

// Get test complexity distribution
MATCH (t:TestScenario)
RETURN t.test_type, avg(t.complexity_score) as avg_complexity, count(*) as test_count
ORDER BY avg_complexity DESC;
```

## Troubleshooting

### "Connection refused"
- Neo4j is not running. Start Neo4j using Docker or Neo4j Desktop.
- Check if port 7687 is blocked by firewall.

### "Authentication failed"
- Verify password in `.env` matches Neo4j password.
- Default password is `please_change_me`.

### "Memory issues"
- Increase Neo4j heap size in `neo4j.conf`:
  ```
  dbms.memory.heap.initial_size=2G
  dbms.memory.heap.max_size=4G
  ```

## Next Steps

After completing Phase 2:
- ✅ Knowledge Graph created
- ✅ 500 test scenarios ingested
- ✅ Ready for Phase 3 (Semantic Web)

Run Phase 3 to add RDF/OWL/SPARQL capabilities!

