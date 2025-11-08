"""
PostgreSQL client with pgvector extension for vector similarity search.
"""
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text, Column, String, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pgvector.sqlalchemy import Vector

from src.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class TestScenarioVector(Base):
    """
    Test scenario vector embedding table.
    Stores unified embeddings combining text, structured, and graph features.
    """
    __tablename__ = 'test_scenario_vectors'
    
    scenario_id = Column(String, primary_key=True)
    test_name = Column(String)
    test_type = Column(String)
    
    # Metadata
    complexity_score = Column(Integer)
    risk_level = Column(String)
    estimated_duration_hours = Column(Float)
    estimated_cost_gbp = Column(Float)
    
    # Structured features (JSON)
    structured_features = Column(JSON)
    
    # Graph features (JSON)
    graph_features = Column(JSON)
    
    # Unified embedding vector (768 dimensions by default for all-mpnet-base-v2)
    # Text: 768, Structured: ~50, Graph: ~10 = ~828 total
    embedding = Column(Vector(828))
    
    def __repr__(self):
        return f"<TestScenarioVector(scenario_id='{self.scenario_id}', test_name='{self.test_name}')>"


class PGVectorClient:
    """
    PostgreSQL client with pgvector extension support.
    Manages connection, schema, and vector operations.
    """
    
    _instance: Optional['PGVectorClient'] = None
    _engine = None
    _session_maker = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize PostgreSQL connection with pgvector."""
        if self._engine is None:
            self._connect()
    
    def _connect(self) -> None:
        """Establish connection to PostgreSQL."""
        try:
            logger.info(f"Connecting to PostgreSQL...")
            
            # Create engine
            self._engine = create_engine(
                settings.pg_conn,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=settings.debug
            )
            
            # Create session maker
            self._session_maker = sessionmaker(bind=self._engine)
            
            # Test connection
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    @contextmanager
    def session(self) -> Session:
        """
        Context manager for database sessions.
        
        Yields:
            SQLAlchemy session
            
        Example:
            with client.session() as session:
                results = session.query(TestScenarioVector).all()
        """
        session = self._session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_extension(self) -> None:
        """Create pgvector extension if it doesn't exist."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("pgvector extension created/verified")
        except Exception as e:
            logger.error(f"Failed to create pgvector extension: {e}")
            raise
    
    def create_tables(self) -> None:
        """Create database tables."""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_index(self, index_type: str = "ivfflat", lists: int = 100) -> None:
        """
        Create vector index for fast similarity search.
        
        Args:
            index_type: Type of index ('ivfflat' or 'hnsw')
            lists: Number of lists for IVFFlat index
        """
        try:
            with self._engine.connect() as conn:
                # Drop existing index if any
                conn.execute(text(
                    "DROP INDEX IF EXISTS test_scenario_vectors_embedding_idx;"
                ))
                
                if index_type == "ivfflat":
                    # IVFFlat index (good for medium datasets)
                    conn.execute(text(f"""
                        CREATE INDEX test_scenario_vectors_embedding_idx
                        ON test_scenario_vectors
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = {lists});
                    """))
                    logger.info(f"Created IVFFlat index with {lists} lists")
                    
                elif index_type == "hnsw":
                    # HNSW index (better for larger datasets, more memory)
                    conn.execute(text("""
                        CREATE INDEX test_scenario_vectors_embedding_idx
                        ON test_scenario_vectors
                        USING hnsw (embedding vector_cosine_ops);
                    """))
                    logger.info("Created HNSW index")
                else:
                    raise ValueError(f"Unknown index type: {index_type}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on PostgreSQL connection.
        
        Returns:
            Dictionary with health status information
        """
        try:
            with self.session() as session:
                # Check vector extension
                result = session.execute(text(
                    "SELECT * FROM pg_extension WHERE extname = 'vector';"
                ))
                vector_ext = result.fetchone()
                
                # Count vectors
                count = session.query(TestScenarioVector).count()
                
                # Get sample
                sample = session.query(TestScenarioVector).first()
                
                return {
                    "status": "healthy",
                    "connection": settings.pg_conn.split("@")[1] if "@" in settings.pg_conn else "unknown",
                    "vector_extension": "installed" if vector_ext else "missing",
                    "vector_count": count,
                    "has_data": sample is not None,
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }
    
    def clear_vectors(self) -> int:
        """
        Clear all vectors from the database.
        
        Returns:
            Number of vectors deleted
        """
        with self.session() as session:
            count = session.query(TestScenarioVector).count()
            session.query(TestScenarioVector).delete()
            logger.info(f"Cleared {count} vectors")
            return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.session() as session:
            total = session.query(TestScenarioVector).count()
            
            # Count by test type
            result = session.execute(text("""
                SELECT test_type, COUNT(*) as count
                FROM test_scenario_vectors
                GROUP BY test_type
                ORDER BY count DESC;
            """))
            by_type = {row[0]: row[1] for row in result}
            
            # Count by risk level
            result = session.execute(text("""
                SELECT risk_level, COUNT(*) as count
                FROM test_scenario_vectors
                GROUP BY risk_level
                ORDER BY count DESC;
            """))
            by_risk = {row[0]: row[1] for row in result}
            
            # Average complexity
            result = session.execute(text("""
                SELECT AVG(complexity_score) as avg_complexity
                FROM test_scenario_vectors;
            """))
            avg_complexity = result.fetchone()[0] or 0
            
            return {
                "total_vectors": total,
                "by_test_type": by_type,
                "by_risk_level": by_risk,
                "average_complexity": float(avg_complexity),
            }
    
    def close(self) -> None:
        """Close database connection."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("PostgreSQL connection closed")


# Global client instance
_client: Optional[PGVectorClient] = None


def get_pg_client() -> PGVectorClient:
    """
    Get or create the global PostgreSQL client instance.
    
    Returns:
        PGVectorClient instance
    """
    global _client
    if _client is None:
        _client = PGVectorClient()
    return _client


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PGVECTOR CLIENT TEST")
    print("=" * 70)
    
    try:
        client = get_pg_client()
        
        # Create extension
        print("\n[1/3] Creating pgvector extension...")
        client.create_extension()
        print("[OK] pgvector extension ready")
        
        # Create tables
        print("\n[2/3] Creating tables...")
        client.create_tables()
        print("[OK] Tables created")
        
        # Health check
        print("\n[3/3] Health check...")
        health = client.health_check()
        print(f"[OK] Status: {health['status']}")
        print(f"     Vector count: {health['vector_count']}")
        print(f"     Extension: {health.get('vector_extension', 'unknown')}")
        
        print("\n[OK] PGVector client test complete")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("Make sure PostgreSQL is running and accessible.")

