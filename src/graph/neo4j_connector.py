"""
Neo4j connector with connection pooling, retry logic, and health checks.
"""
import logging
import time
from typing import Optional, Any, Dict, List
from contextlib import contextmanager

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from src.config.settings import settings

logger = logging.getLogger(__name__)


class Neo4jConnector:
    """
    Neo4j database connector with retry logic and connection management.
    Implements singleton pattern for efficient resource usage.
    """
    
    _instance: Optional['Neo4jConnector'] = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one connector instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connector (only once due to singleton)."""
        if self._driver is None:
            self._connect()
    
    def _connect(self, max_retries: int = 3, retry_delay: float = 2.0) -> None:
        """
        Establish connection to Neo4j with retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retries in seconds
        """
        for attempt in range(max_retries):
            try:
                self._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    max_connection_lifetime=3600,  # 1 hour
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60.0,
                )
                
                # Verify connectivity
                self._driver.verify_connectivity()
                logger.info(f"Successfully connected to Neo4j at {settings.neo4j_uri}")
                return
                
            except ServiceUnavailable as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Neo4j connection attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {retry_delay}s... Error: {e}"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {e}")
                raise
    
    @contextmanager
    def session(self, database: str = "neo4j") -> Session:
        """
        Context manager for Neo4j sessions.
        
        Args:
            database: Database name (default: "neo4j")
            
        Yields:
            Neo4j session
            
        Example:
            with connector.session() as session:
                result = session.run("MATCH (n) RETURN count(n)")
        """
        if self._driver is None:
            self._connect()
        
        session = self._driver.session(database=database)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j"
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name
            
        Returns:
            List of result records as dictionaries
        """
        with self.session(database=database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j"
    ) -> Any:
        """
        Execute a write query within a transaction.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name
            
        Returns:
            Query result summary
        """
        with self.session(database=database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return summary
    
    def execute_transaction(
        self,
        queries: List[tuple],
        database: str = "neo4j"
    ) -> None:
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries: List of (query, parameters) tuples
            database: Database name
        """
        with self.session(database=database) as session:
            with session.begin_transaction() as tx:
                for query, parameters in queries:
                    tx.run(query, parameters or {})
                tx.commit()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Neo4j connection.
        
        Returns:
            Dictionary with health status information
        """
        try:
            with self.session() as session:
                # Get Neo4j version
                result = session.run("CALL dbms.components() YIELD name, versions")
                components = [dict(record) for record in result]
                
                # Get database info
                result = session.run(
                    "CALL db.info() YIELD name, creationDate"
                )
                db_info = [dict(record) for record in result]
                
                # Get node count
                result = session.run("MATCH (n) RETURN count(n) as node_count")
                node_count = result.single()["node_count"]
                
                # Get relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
                rel_count = result.single()["rel_count"]
                
                return {
                    "status": "healthy",
                    "uri": settings.neo4j_uri,
                    "components": components,
                    "database_info": db_info,
                    "node_count": node_count,
                    "relationship_count": rel_count,
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "uri": settings.neo4j_uri,
                "error": str(e),
            }
    
    def clear_database(self, database: str = "neo4j") -> None:
        """
        Clear all nodes and relationships from the database.
        USE WITH CAUTION - This deletes all data!
        
        Args:
            database: Database name
        """
        logger.warning("Clearing entire Neo4j database!")
        
        with self.session(database=database) as session:
            # Delete in batches to avoid memory issues
            while True:
                result = session.run(
                    "MATCH (n) WITH n LIMIT 10000 DETACH DELETE n RETURN count(n) as deleted"
                )
                deleted = result.single()["deleted"]
                if deleted == 0:
                    break
                logger.info(f"Deleted {deleted} nodes")
        
        logger.info("Database cleared successfully")
    
    def get_database_stats(self, database: str = "neo4j") -> Dict[str, Any]:
        """
        Get database statistics.
        
        Args:
            database: Database name
            
        Returns:
            Dictionary with database statistics
        """
        with self.session(database=database) as session:
            # Node counts by label
            result = session.run(
                """
                CALL db.labels() YIELD label
                CALL apoc.cypher.run(
                    'MATCH (n:`' + label + '`) RETURN count(n) as count',
                    {}
                ) YIELD value
                RETURN label, value.count as count
                """
            )
            # Fallback if APOC not available
            try:
                node_counts = {record["label"]: record["count"] for record in result}
            except:
                result = session.run("CALL db.labels() YIELD label RETURN label")
                labels = [record["label"] for record in result]
                node_counts = {}
                for label in labels:
                    result = session.run(f"MATCH (n:`{label}`) RETURN count(n) as count")
                    node_counts[label] = result.single()["count"]
            
            # Relationship counts by type
            result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
            rel_types = [record["relationshipType"] for record in result]
            rel_counts = {}
            for rel_type in rel_types:
                result = session.run(f"MATCH ()-[r:`{rel_type}`]->() RETURN count(r) as count")
                rel_counts[rel_type] = result.single()["count"]
            
            # Total counts
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = result.single()["total_nodes"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as total_rels")
            total_rels = result.single()["total_rels"]
            
            return {
                "total_nodes": total_nodes,
                "total_relationships": total_rels,
                "nodes_by_label": node_counts,
                "relationships_by_type": rel_counts,
            }
    
    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Global connector instance
_connector: Optional[Neo4jConnector] = None


def get_connector() -> Neo4jConnector:
    """
    Get or create the global Neo4j connector instance.
    
    Returns:
        Neo4jConnector instance
    """
    global _connector
    if _connector is None:
        _connector = Neo4jConnector()
    return _connector


if __name__ == "__main__":
    # Test the connector
    connector = get_connector()
    
    print("\n" + "=" * 60)
    print("NEO4J CONNECTOR TEST")
    print("=" * 60)
    
    # Health check
    health = connector.health_check()
    print(f"\nHealth Status: {health['status']}")
    
    if health['status'] == 'healthy':
        print(f"Node Count: {health['node_count']}")
        print(f"Relationship Count: {health['relationship_count']}")
        
        # Get stats
        stats = connector.get_database_stats()
        print(f"\nDatabase Statistics:")
        print(f"  Total Nodes: {stats['total_nodes']}")
        print(f"  Total Relationships: {stats['total_relationships']}")
        
        if stats['nodes_by_label']:
            print(f"\n  Nodes by Label:")
            for label, count in stats['nodes_by_label'].items():
                print(f"    {label}: {count}")
    else:
        print(f"Error: {health.get('error', 'Unknown error')}")
    
    print("\n[OK] Connector test complete")

