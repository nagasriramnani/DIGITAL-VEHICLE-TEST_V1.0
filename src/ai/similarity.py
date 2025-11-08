"""
Similarity computation helpers for vector search and recommendations.
"""
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.spatial.distance import cosine as cosine_distance
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity

logger = logging.getLogger(__name__)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity (0 to 1, higher is more similar)
    """
    # Ensure vectors are 1D
    vec1 = vec1.flatten()
    vec2 = vec2.flatten()
    
    # Cosine similarity = 1 - cosine distance
    return 1.0 - cosine_distance(vec1, vec2)


def batch_cosine_similarity(
    query_vector: np.ndarray,
    vectors: np.ndarray
) -> np.ndarray:
    """
    Compute cosine similarity between a query vector and multiple vectors.
    
    Args:
        query_vector: Query vector (1D or 2D with shape (1, dim))
        vectors: Matrix of vectors (N x dim)
        
    Returns:
        Array of similarity scores (N,)
    """
    # Ensure query is 2D
    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)
    
    # Compute similarities
    similarities = sklearn_cosine_similarity(query_vector, vectors)[0]
    
    return similarities


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute Euclidean distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Euclidean distance (lower is more similar)
    """
    return np.linalg.norm(vec1 - vec2)


def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute Manhattan (L1) distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Manhattan distance (lower is more similar)
    """
    return np.sum(np.abs(vec1 - vec2))


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalize vector to unit length (L2 normalization).
    
    Args:
        vector: Input vector
        
    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def find_nearest_neighbors(
    query_vector: np.ndarray,
    vectors: np.ndarray,
    k: int = 10,
    metric: str = 'cosine'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find k nearest neighbors to a query vector.
    
    Args:
        query_vector: Query vector
        vectors: Matrix of vectors to search
        k: Number of neighbors to return
        metric: Distance metric ('cosine', 'euclidean', 'manhattan')
        
    Returns:
        Tuple of (indices, distances) of k nearest neighbors
    """
    if metric == 'cosine':
        # Compute cosine similarities
        similarities = batch_cosine_similarity(query_vector, vectors)
        # Get top k (argsort in descending order)
        top_k_indices = np.argsort(similarities)[::-1][:k]
        top_k_scores = similarities[top_k_indices]
        return top_k_indices, top_k_scores
        
    elif metric == 'euclidean':
        # Compute Euclidean distances
        distances = np.linalg.norm(vectors - query_vector, axis=1)
        # Get top k (argsort in ascending order)
        top_k_indices = np.argsort(distances)[:k]
        top_k_distances = distances[top_k_indices]
        return top_k_indices, top_k_distances
        
    elif metric == 'manhattan':
        # Compute Manhattan distances
        distances = np.sum(np.abs(vectors - query_vector), axis=1)
        # Get top k (argsort in ascending order)
        top_k_indices = np.argsort(distances)[:k]
        top_k_distances = distances[top_k_indices]
        return top_k_indices, top_k_distances
        
    else:
        raise ValueError(f"Unknown metric: {metric}")


def compute_similarity_matrix(vectors: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine similarity matrix for a set of vectors.
    
    Args:
        vectors: Matrix of vectors (N x dim)
        
    Returns:
        Similarity matrix (N x N)
    """
    return sklearn_cosine_similarity(vectors)


def rank_by_similarity(
    query_vector: np.ndarray,
    candidates: List[Dict[str, Any]],
    embedding_key: str = 'embedding'
) -> List[Tuple[Dict[str, Any], float]]:
    """
    Rank candidates by similarity to query vector.
    
    Args:
        query_vector: Query embedding
        candidates: List of candidate dictionaries with embeddings
        embedding_key: Key for embedding in candidate dict
        
    Returns:
        List of (candidate, similarity_score) tuples, sorted by similarity
    """
    results = []
    
    for candidate in candidates:
        embedding = candidate.get(embedding_key)
        if embedding is not None:
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            
            sim = cosine_similarity(query_vector, embedding)
            results.append((candidate, float(sim)))
    
    # Sort by similarity (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results


def weighted_similarity(
    vec1: np.ndarray,
    vec2: np.ndarray,
    weights: np.ndarray
) -> float:
    """
    Compute weighted cosine similarity.
    
    Args:
        vec1: First vector
        vec2: Second vector
        weights: Weight vector (same dimension as vec1/vec2)
        
    Returns:
        Weighted cosine similarity
    """
    # Apply weights
    vec1_weighted = vec1 * weights
    vec2_weighted = vec2 * weights
    
    return cosine_similarity(vec1_weighted, vec2_weighted)


def diversity_reranking(
    candidates: List[Tuple[Any, float]],
    embeddings: np.ndarray,
    lambda_param: float = 0.5,
    k: int = 10
) -> List[Tuple[Any, float]]:
    """
    Rerank candidates to balance relevance and diversity (MMR-like).
    
    Args:
        candidates: List of (item, relevance_score) tuples
        embeddings: Embeddings for all candidates
        lambda_param: Trade-off between relevance and diversity (0-1)
        k: Number of items to return
        
    Returns:
        Reranked list of (item, score) tuples
    """
    if len(candidates) <= k:
        return candidates[:k]
    
    selected = []
    selected_indices = []
    remaining = list(range(len(candidates)))
    
    # Select first (most relevant)
    selected.append(candidates[0])
    selected_indices.append(0)
    remaining.remove(0)
    
    # Iteratively select items
    while len(selected) < k and remaining:
        best_score = -float('inf')
        best_idx = None
        
        for idx in remaining:
            # Relevance score
            relevance = candidates[idx][1]
            
            # Diversity score (minimum similarity to selected items)
            diversities = []
            for sel_idx in selected_indices:
                sim = cosine_similarity(embeddings[idx], embeddings[sel_idx])
                diversities.append(sim)
            
            diversity = 1.0 - max(diversities) if diversities else 1.0
            
            # Combined score
            score = lambda_param * relevance + (1 - lambda_param) * diversity
            
            if score > best_score:
                best_score = score
                best_idx = idx
        
        if best_idx is not None:
            selected.append(candidates[best_idx])
            selected_indices.append(best_idx)
            remaining.remove(best_idx)
    
    return selected


class SimilaritySearcher:
    """Helper class for similarity-based search operations."""
    
    def __init__(self, metric: str = 'cosine'):
        """
        Initialize similarity searcher.
        
        Args:
            metric: Distance metric to use
        """
        self.metric = metric
    
    def search(
        self,
        query_vector: np.ndarray,
        vector_database: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k most similar vectors.
        
        Args:
            query_vector: Query vector
            vector_database: Database of vectors
            k: Number of results
            
        Returns:
            Tuple of (indices, scores)
        """
        return find_nearest_neighbors(
            query_vector,
            vector_database,
            k=k,
            metric=self.metric
        )
    
    def batch_search(
        self,
        query_vectors: np.ndarray,
        vector_database: np.ndarray,
        k: int = 10
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Search for multiple queries.
        
        Args:
            query_vectors: Matrix of query vectors (N x dim)
            vector_database: Database of vectors
            k: Number of results per query
            
        Returns:
            List of (indices, scores) tuples for each query
        """
        results = []
        
        for query in query_vectors:
            indices, scores = self.search(query, vector_database, k=k)
            results.append((indices, scores))
        
        return results


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SIMILARITY COMPUTATION TEST")
    print("=" * 70)
    
    # Create test vectors
    print("\n[1/4] Creating test vectors...")
    vec1 = np.random.rand(100)
    vec2 = np.random.rand(100)
    vec3 = vec1 + np.random.rand(100) * 0.1  # Similar to vec1
    
    print("[OK] Test vectors created")
    
    # Test cosine similarity
    print("\n[2/4] Testing cosine similarity...")
    sim_12 = cosine_similarity(vec1, vec2)
    sim_13 = cosine_similarity(vec1, vec3)
    print(f"[OK] Similarity(vec1, vec2): {sim_12:.4f}")
    print(f"     Similarity(vec1, vec3): {sim_13:.4f}")
    print(f"     vec3 is more similar to vec1: {sim_13 > sim_12}")
    
    # Test batch similarity
    print("\n[3/4] Testing batch similarity...")
    vectors = np.vstack([vec2, vec3, np.random.rand(100)])
    similarities = batch_cosine_similarity(vec1, vectors)
    print(f"[OK] Batch similarities: {similarities}")
    
    # Test nearest neighbors
    print("\n[4/4] Testing nearest neighbors...")
    database = np.random.rand(100, 100)
    database[0] = vec1  # Add vec1 to database
    
    indices, scores = find_nearest_neighbors(vec1, database, k=3)
    print(f"[OK] Top 3 neighbors: indices={indices}, scores={scores[:3]}")
    print(f"     First neighbor is vec1 itself: {indices[0] == 0}")
    
    print("\n[OK] Similarity computation test complete")

