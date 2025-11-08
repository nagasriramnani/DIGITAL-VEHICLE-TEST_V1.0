#!/usr/bin/env python
"""
Script to run Phase 2 knowledge graph ingestion.
Run this after Neo4j is set up and running.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.neo4j_connector import get_connector
from src.graph.graph_operations import GraphOperations


def main():
    """Run Phase 2 ingestion workflow."""
    print("\n" + "=" * 70)
    print("PHASE 2: NEO4J KNOWLEDGE GRAPH INGESTION")
    print("=" * 70)
    
    # Check Neo4j connectivity
    print("\n[1/4] Checking Neo4j connection...")
    try:
        connector = get_connector()
        health = connector.health_check()
        
        if health["status"] != "healthy":
            print("[ERROR] Neo4j is not healthy!")
            print("Please ensure Neo4j is running. See PHASE2_SETUP.md for instructions.")
            return 1
        
        print(f"[OK] Connected to Neo4j at {health['uri']}")
        print(f"     Current nodes: {health['node_count']}")
        print(f"     Current relationships: {health['relationship_count']}")
    except Exception as e:
        print(f"[ERROR] Cannot connect to Neo4j: {e}")
        print("\nPlease start Neo4j first. See PHASE2_SETUP.md for setup instructions.")
        return 1
    
    # Confirm before clearing
    if health['node_count'] > 0:
        print(f"\n[WARNING] Database has {health['node_count']} nodes.")
        response = input("Clear database and re-import? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return 0
        
        print("\n[2/4] Clearing database...")
        connector.clear_database()
        print("[OK] Database cleared")
    else:
        print("\n[2/4] Database is empty, skipping clear")
    
    # Create schema
    print("\n[3/4] Creating schema...")
    ops = GraphOperations()
    ops.create_schema()
    print("[OK] Schema created (constraints + indexes)")
    
    # Ingest synthetic data
    print("\n[4/4] Ingesting synthetic test scenarios...")
    print("      This may take 2-5 minutes for 500 scenarios...")
    
    stats = ops.ingest_synthetic_data()
    
    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    
    print("\nNodes Created:")
    print(f"  Vehicles:             {stats['vehicles']:6,d}")
    print(f"  Platforms:            {stats['platforms']:6,d}")
    print(f"  Components:           {stats['components']:6,d}")
    print(f"  Systems:              {stats['systems']:6,d}")
    print(f"  Test Scenarios:       {stats['test_scenarios']:6,d}")
    print(f"  Test Types:           {stats['test_types']:6,d}")
    print(f"  Regulatory Standards: {stats['regulatory_standards']:6,d}")
    print(f"  Historical Tests:     {stats['historical_tests']:6,d}")
    print(f"  Facilities:           {stats['facilities']:6,d}")
    
    print(f"\nRelationships:          {stats['relationships']:6,d}")
    
    # Verify with database stats
    db_stats = connector.get_database_stats()
    print("\n" + "=" * 70)
    print("DATABASE STATISTICS")
    print("=" * 70)
    print(f"\nTotal Nodes:            {db_stats['total_nodes']:6,d}")
    print(f"Total Relationships:    {db_stats['total_relationships']:6,d}")
    
    print("\nNodes by Label:")
    for label, count in sorted(db_stats['nodes_by_label'].items(), key=lambda x: -x[1]):
        print(f"  {label:25s}: {count:6,d}")
    
    print("\nRelationships by Type:")
    for rel_type, count in sorted(db_stats['relationships_by_type'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {rel_type:25s}: {count:6,d}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Phase 2 ingestion complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Access Neo4j Browser: http://localhost:7474")
    print("  2. Run queries to explore the graph")
    print("  3. Run tests: pytest tests/test_graph.py -v")
    print("  4. Proceed to Phase 3 (Semantic Web)")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

