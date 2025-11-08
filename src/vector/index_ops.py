"""
Vector index operations for upserting and searching embeddings.
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from sqlalchemy import text
from pgvector.sqlalchemy import Vector

from src.vector.pg_client import get_pg_client, TestScenarioVector

logger = logging.getLogger(__name__)


class VectorIndexOps:
    """Operations for managing vector indexes and similarity search."""
    
    def __init__(self):
        """Initialize vector index operations."""
        self.client = get_pg_client()
    
    def upsert_vector(
        self,
        scenario_id: str,
        test_name: str,
        test_type: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
        structured_features: Optional[Dict[str, Any]] = None,
        graph_features: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Insert or update a single vector embedding.
        
        Args:
            scenario_id: Unique scenario identifier
            test_name: Test name
            test_type: Test type
            embedding: Embedding vector (numpy array)
            metadata: Additional metadata
            structured_features: Structured feature dict
            graph_features: Graph feature dict
        """
        with self.client.session() as session:
            # Check if exists
            existing = session.query(TestScenarioVector).filter_by(
                scenario_id=scenario_id
            ).first()
            
            if existing:
                # Update
                existing.test_name = test_name
                existing.test_type = test_type
                existing.embedding = embedding.tolist()
                existing.structured_features = structured_features or {}
                existing.graph_features = graph_features or {}
                
                if metadata:
                    existing.complexity_score = metadata.get('complexity_score')
                    existing.risk_level = metadata.get('risk_level')
                    existing.estimated_duration_hours = metadata.get('estimated_duration_hours')
                    existing.estimated_cost_gbp = metadata.get('estimated_cost_gbp')
            else:
                # Insert
                vector = TestScenarioVector(
                    scenario_id=scenario_id,
                    test_name=test_name,
                    test_type=test_type,
                    embedding=embedding.tolist(),
                    structured_features=structured_features or {},
                    graph_features=graph_features or {},
                    complexity_score=metadata.get('complexity_score') if metadata else None,
                    risk_level=metadata.get('risk_level') if metadata else None,
                    estimated_duration_hours=metadata.get('estimated_duration_hours') if metadata else None,
                    estimated_cost_gbp=metadata.get('estimated_cost_gbp') if metadata else None,
                )
                session.add(vector)
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Batch upsert multiple vectors.
        
        Args:
            vectors: List of vector dictionaries with keys:
                     scenario_id, test_name, test_type, embedding, metadata, etc.
            batch_size: Number of vectors to process per batch
            
        Returns:
            Number of vectors upserted
        """
        count = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            
            for vec in batch:
                self.upsert_vector(
                    scenario_id=vec['scenario_id'],
                    test_name=vec['test_name'],
                    test_type=vec['test_type'],
                    embedding=vec['embedding'],
                    metadata=vec.get('metadata'),
                    structured_features=vec.get('structured_features'),
                    graph_features=vec.get('graph_features')
                )
                count += 1
            
            if (i + batch_size) % 200 == 0:
                logger.info(f"  Upserted {min(i + batch_size, len(vectors))}/{len(vectors)} vectors...")
        
        logger.info(f"Upserted {count} vectors total")
        return count
    
    def ann_search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        test_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        min_complexity: Optional[int] = None,
        max_complexity: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Approximate Nearest Neighbor search using cosine similarity.
        
        Args:
            query_vector: Query embedding vector
            k: Number of nearest neighbors to return
            test_type: Filter by test type (optional)
            risk_level: Filter by risk level (optional)
            min_complexity: Minimum complexity score (optional)
            max_complexity: Maximum complexity score (optional)
            
        Returns:
            List of dictionaries with scenario info and similarity scores
        """
        with self.client.session() as session:
            # Build query
            query = session.query(
                TestScenarioVector,
                (1 - TestScenarioVector.embedding.cosine_distance(query_vector.tolist())).label('similarity')
            )
            
            # Apply filters
            if test_type:
                query = query.filter(TestScenarioVector.test_type == test_type)
            
            if risk_level:
                query = query.filter(TestScenarioVector.risk_level == risk_level)
            
            if min_complexity is not None:
                query = query.filter(TestScenarioVector.complexity_score >= min_complexity)
            
            if max_complexity is not None:
                query = query.filter(TestScenarioVector.complexity_score <= max_complexity)
            
            # Order by similarity and limit
            results = query.order_by(text('similarity DESC')).limit(k).all()
            
            # Format results
            output = []
            for vector, similarity in results:
                output.append({
                    'scenario_id': vector.scenario_id,
                    'test_name': vector.test_name,
                    'test_type': vector.test_type,
                    'complexity_score': vector.complexity_score,
                    'risk_level': vector.risk_level,
                    'estimated_duration_hours': vector.estimated_duration_hours,
                    'estimated_cost_gbp': vector.estimated_cost_gbp,
                    'similarity': float(similarity),
                    'structured_features': vector.structured_features,
                    'graph_features': vector.graph_features,
                })
            
            return output
    
    def get_vector_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a vector by scenario ID.
        
        Args:
            scenario_id: Scenario identifier
            
        Returns:
            Vector dictionary or None
        """
        with self.client.session() as session:
            vector = session.query(TestScenarioVector).filter_by(
                scenario_id=scenario_id
            ).first()
            
            if vector:
                return {
                    'scenario_id': vector.scenario_id,
                    'test_name': vector.test_name,
                    'test_type': vector.test_type,
                    'complexity_score': vector.complexity_score,
                    'risk_level': vector.risk_level,
                    'estimated_duration_hours': vector.estimated_duration_hours,
                    'estimated_cost_gbp': vector.estimated_cost_gbp,
                    'embedding': np.array(vector.embedding),
                    'structured_features': vector.structured_features,
                    'graph_features': vector.graph_features,
                }
            return None
    
    def find_similar_scenarios(
        self,
        scenario_id: str,
        k: int = 5,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find similar scenarios to a given scenario.
        
        Args:
            scenario_id: Reference scenario ID
            k: Number of similar scenarios to return
            exclude_self: Exclude the reference scenario from results
            
        Returns:
            List of similar scenarios with similarity scores
        """
        # Get the reference vector
        ref_vector = self.get_vector_by_id(scenario_id)
        
        if not ref_vector:
            return []
        
        # Search for similar vectors
        k_search = k + 1 if exclude_self else k
        similar = self.ann_search(ref_vector['embedding'], k=k_search)
        
        # Exclude self if requested
        if exclude_self:
            similar = [s for s in similar if s['scenario_id'] != scenario_id]
        
        return similar[:k]
    
    def batch_similarity_search(
        self,
        scenario_ids: List[str],
        k: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find similar scenarios for multiple scenarios at once.
        
        Args:
            scenario_ids: List of scenario IDs
            k: Number of similar scenarios per scenario
            
        Returns:
            Dictionary mapping scenario_id to list of similar scenarios
        """
        results = {}
        
        for scenario_id in scenario_ids:
            results[scenario_id] = self.find_similar_scenarios(scenario_id, k=k)
        
        return results
    
    def get_vector_count(self) -> int:
        """Get total number of vectors in the index."""
        with self.client.session() as session:
            return session.query(TestScenarioVector).count()
    
    def delete_vector(self, scenario_id: str) -> bool:
        """
        Delete a vector by scenario ID.
        
        Args:
            scenario_id: Scenario identifier
            
        Returns:
            True if deleted, False if not found
        """
        with self.client.session() as session:
            vector = session.query(TestScenarioVector).filter_by(
                scenario_id=scenario_id
            ).first()
            
            if vector:
                session.delete(vector)
                return True
            return False


def upsert_vectors(vectors: List[Dict[str, Any]]) -> int:
    """
    Convenience function for batch upserting vectors.
    
    Args:
        vectors: List of vector dictionaries
        
    Returns:
        Number of vectors upserted
    """
    ops = VectorIndexOps()
    return ops.upsert_vectors(vectors)


def ann_search(query_vector: np.ndarray, k: int = 10, **filters) -> List[Dict[str, Any]]:
    """
    Convenience function for ANN search.
    
    Args:
        query_vector: Query embedding
        k: Number of results
        **filters: Additional filters (test_type, risk_level, etc.)
        
    Returns:
        List of similar scenarios
    """
    ops = VectorIndexOps()
    return ops.ann_search(query_vector, k=k, **filters)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VECTOR INDEX OPERATIONS TEST")
    print("=" * 70)
    
    try:
        ops = VectorIndexOps()
        
        # Check connection
        print("\n[1/2] Checking vector index...")
        count = ops.get_vector_count()
        print(f"[OK] Current vector count: {count}")
        
        # Test upsert
        print("\n[2/2] Testing vector upsert...")
        test_vector = {
            'scenario_id': 'TEST-001',
            'test_name': 'Test Vector',
            'test_type': 'performance',
            'embedding': np.random.rand(828),
            'metadata': {
                'complexity_score': 5,
                'risk_level': 'medium',
                'estimated_duration_hours': 10.0,
                'estimated_cost_gbp': 5000.0
            }
        }
        
        ops.upsert_vector(**test_vector)
        print("[OK] Test vector upserted")
        
        # Verify
        retrieved = ops.get_vector_by_id('TEST-001')
        if retrieved:
            print(f"[OK] Retrieved test vector: {retrieved['test_name']}")
            
            # Clean up
            ops.delete_vector('TEST-001')
            print("[OK] Test vector deleted")
        
        print("\n[OK] Vector index operations test complete")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        print("Make sure PostgreSQL with pgvector is running.")

