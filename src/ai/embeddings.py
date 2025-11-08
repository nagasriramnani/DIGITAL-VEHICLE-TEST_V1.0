"""
Unified embedding pipeline combining text, structured, and graph features.
Uses SentenceTransformers for text encoding and custom feature engineering.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from pathlib import Path

from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """
    Unified embedding pipeline that combines:
    1. Text embeddings (from test name and description)
    2. Structured features (normalized numeric and one-hot categorical)
    3. Graph features (from Neo4j - neighbor counts, centrality)
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        device: Optional[str] = None
    ):
        """
        Initialize embedding pipeline.
        
        Args:
            model_name: SentenceTransformer model name
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = 'mps'  # Apple Silicon
            else:
                device = 'cpu'
        
        self.device = device
        
        logger.info(f"Loading embedding model: {model_name} on {device}")
        self.model = SentenceTransformer(model_name, device=device)
        self.text_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Text embedding dimension: {self.text_dim}")
        
        # Feature dimensions
        self.structured_dim = 50  # Numeric + one-hot features
        self.graph_dim = 10       # Graph features
        self.total_dim = self.text_dim + self.structured_dim + self.graph_dim
        
        logger.info(f"Total embedding dimension: {self.total_dim}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text using SentenceTransformer.
        
        Args:
            text: Input text
            
        Returns:
            Text embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def encode_text_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts in batch.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            
        Returns:
            Array of text embeddings (N x text_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True
        )
        return embeddings
    
    def extract_structured_features(self, scenario: Dict[str, Any]) -> np.ndarray:
        """
        Extract and normalize structured features from scenario.
        
        Features include:
        - Normalized duration (log scale)
        - Normalized cost (log scale)
        - Complexity score (0-1)
        - Temperature (normalized to -1 to 1)
        - Humidity (0-1)
        - Load percent (0-1)
        - Speed profile (one-hot)
        - Test type (one-hot)
        - Risk level (one-hot)
        - Road surface (one-hot)
        - Weather (one-hot)
        
        Args:
            scenario: Scenario dictionary
            
        Returns:
            Structured feature vector (50-dim)
        """
        features = []
        
        # Numeric features (normalized)
        duration = scenario.get('estimated_duration_hours', 10.0)
        features.append(np.log1p(duration) / 10.0)  # Log normalized
        
        cost = scenario.get('estimated_cost_gbp', 5000.0)
        features.append(np.log1p(cost) / 15.0)  # Log normalized
        
        complexity = scenario.get('complexity_score', 5)
        features.append(complexity / 10.0)  # 0-1 scale
        
        # Environmental conditions
        env = scenario.get('environmental_conditions', {})
        temp = env.get('temperature_celsius', 20.0)
        features.append((temp + 40) / 80.0)  # -40 to 40 -> 0 to 1
        
        humidity = env.get('humidity_percent', 50.0)
        features.append(humidity / 100.0)  # 0-1
        
        # Load profile
        load = scenario.get('load_profile', {})
        load_percent = load.get('load_percent', 50.0)
        features.append(load_percent / 100.0)  # 0-1
        
        distance = load.get('distance_km', 50.0)
        features.append(np.log1p(distance) / 10.0)  # Log normalized
        
        # One-hot: Speed profile (5 categories)
        speed_profile = load.get('speed_profile', 'mixed')
        speed_profiles = ['urban', 'highway', 'mixed', 'sport', 'eco']
        speed_one_hot = [1.0 if speed_profile == sp else 0.0 for sp in speed_profiles]
        features.extend(speed_one_hot)
        
        # One-hot: Test type (6 categories)
        test_type = scenario.get('test_type', 'performance')
        test_types = ['performance', 'durability', 'safety', 'regulatory', 'adas', 'emissions']
        type_one_hot = [1.0 if test_type == tt else 0.0 for tt in test_types]
        features.extend(type_one_hot)
        
        # One-hot: Risk level (4 categories)
        risk_level = scenario.get('risk_level', 'medium')
        risk_levels = ['low', 'medium', 'high', 'critical']
        risk_one_hot = [1.0 if risk_level == rl else 0.0 for rl in risk_levels]
        features.extend(risk_one_hot)
        
        # One-hot: Road surface (5 categories)
        road_surface = env.get('road_surface', 'dry')
        road_surfaces = ['dry', 'wet', 'snow', 'ice', 'gravel']
        road_one_hot = [1.0 if road_surface == rs else 0.0 for rs in road_surfaces]
        features.extend(road_one_hot)
        
        # One-hot: Weather (4 categories)
        weather = env.get('weather', 'clear')
        weathers = ['clear', 'rain', 'snow', 'fog']
        weather_one_hot = [1.0 if weather == w else 0.0 for w in weathers]
        features.extend(weather_one_hot)
        
        # Binary flags
        features.append(1.0 if scenario.get('certification_required', False) else 0.0)
        
        # Pad or truncate to exactly 50 dimensions
        features = features[:50]
        while len(features) < 50:
            features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    def extract_graph_features(
        self,
        scenario: Dict[str, Any],
        graph_context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Extract graph-based features from Neo4j relationships.
        
        Features include:
        - Number of target components
        - Number of target systems
        - Number of regulatory standards
        - Component criticality average
        - Historical test count
        - Historical pass rate
        - Degree centrality (placeholder)
        - Betweenness centrality (placeholder)
        - Platform coverage score
        - Execution frequency score
        
        Args:
            scenario: Scenario dictionary
            graph_context: Optional pre-computed graph features
            
        Returns:
            Graph feature vector (10-dim)
        """
        features = []
        
        if graph_context:
            # Use pre-computed graph features
            features.append(graph_context.get('component_count', 0) / 10.0)
            features.append(graph_context.get('system_count', 0) / 5.0)
            features.append(graph_context.get('standard_count', 0) / 5.0)
            features.append(graph_context.get('avg_criticality', 0.5))
            features.append(graph_context.get('degree_centrality', 0.0))
            features.append(graph_context.get('betweenness_centrality', 0.0))
        else:
            # Extract from scenario data
            components = scenario.get('target_components', [])
            features.append(len(components) / 10.0)  # Normalized
            
            systems = scenario.get('target_systems', [])
            features.append(len(systems) / 5.0)  # Normalized
            
            standards = scenario.get('regulatory_standards', [])
            features.append(len(standards) / 5.0)  # Normalized
            
            # Placeholder features (would come from graph queries)
            features.extend([0.5, 0.0, 0.0])  # avg_criticality, degree, betweenness
        
        # Historical context
        historical = scenario.get('historical_results', [])
        features.append(len(historical) / 10.0)  # Normalized execution count
        
        if historical:
            pass_count = sum(1 for h in historical if h.get('passed', False))
            pass_rate = pass_count / len(historical)
            features.append(pass_rate)
        else:
            features.append(0.5)  # Default pass rate
        
        # Platform and model coverage
        platforms = scenario.get('applicable_platforms', [])
        features.append(len(platforms) / 3.0)  # Max 3 platforms
        
        models = scenario.get('applicable_models', [])
        features.append(len(models) / 8.0)  # Max 8 models
        
        # Pad or truncate to exactly 10 dimensions
        features = features[:10]
        while len(features) < 10:
            features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    def create_unified_embedding(
        self,
        scenario: Dict[str, Any],
        graph_context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """
        Create unified embedding combining text, structured, and graph features.
        
        Args:
            scenario: Scenario dictionary
            graph_context: Optional pre-computed graph features
            
        Returns:
            Unified embedding vector (text_dim + 50 + 10)
        """
        # Text embedding
        text = f"{scenario.get('test_name', '')} {scenario.get('description', '')}"
        text_emb = self.encode_text(text)
        
        # Structured features
        struct_emb = self.extract_structured_features(scenario)
        
        # Graph features
        graph_emb = self.extract_graph_features(scenario, graph_context)
        
        # Concatenate
        unified = np.concatenate([text_emb, struct_emb, graph_emb])
        
        return unified
    
    def batch_encode_scenarios(
        self,
        scenarios: List[Dict[str, Any]],
        graph_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[np.ndarray]:
        """
        Batch encode multiple scenarios.
        
        Args:
            scenarios: List of scenario dictionaries
            graph_contexts: Optional dict mapping scenario_id to graph features
            
        Returns:
            List of unified embeddings
        """
        logger.info(f"Encoding {len(scenarios)} scenarios...")
        
        # Batch encode text
        texts = [
            f"{s.get('test_name', '')} {s.get('description', '')}"
            for s in scenarios
        ]
        text_embeddings = self.encode_text_batch(texts)
        
        # Extract structured and graph features
        embeddings = []
        for i, scenario in enumerate(scenarios):
            scenario_id = scenario.get('scenario_id')
            graph_context = graph_contexts.get(scenario_id) if graph_contexts else None
            
            struct_emb = self.extract_structured_features(scenario)
            graph_emb = self.extract_graph_features(scenario, graph_context)
            
            # Concatenate
            unified = np.concatenate([text_embeddings[i], struct_emb, graph_emb])
            embeddings.append(unified)
            
            if (i + 1) % 100 == 0:
                logger.info(f"  Processed {i + 1}/{len(scenarios)} scenarios...")
        
        logger.info(f"Encoded {len(embeddings)} scenarios")
        return embeddings


def create_embedding_pipeline(model_name: Optional[str] = None) -> EmbeddingPipeline:
    """
    Create embedding pipeline with default or custom model.
    
    Args:
        model_name: Optional custom model name
        
    Returns:
        EmbeddingPipeline instance
    """
    from src.config.settings import settings
    
    model = model_name or settings.embedding_model_name
    return EmbeddingPipeline(model_name=model)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EMBEDDING PIPELINE TEST")
    print("=" * 70)
    
    # Create pipeline
    print("\n[1/3] Loading embedding model...")
    pipeline = EmbeddingPipeline()
    print(f"[OK] Model loaded: {pipeline.model_name}")
    print(f"     Device: {pipeline.device}")
    print(f"     Text dim: {pipeline.text_dim}")
    print(f"     Total dim: {pipeline.total_dim}")
    
    # Test text encoding
    print("\n[2/3] Testing text encoding...")
    text = "Battery thermal management test for EV platform"
    text_emb = pipeline.encode_text(text)
    print(f"[OK] Text embedding shape: {text_emb.shape}")
    
    # Test unified embedding
    print("\n[3/3] Testing unified embedding...")
    test_scenario = {
        'scenario_id': 'TEST-001',
        'test_name': 'Battery Thermal Test',
        'description': 'Validate battery thermal management under extreme conditions',
        'test_type': 'performance',
        'complexity_score': 7,
        'risk_level': 'high',
        'estimated_duration_hours': 48.5,
        'estimated_cost_gbp': 12000.0,
        'certification_required': True,
        'environmental_conditions': {
            'temperature_celsius': 40.0,
            'humidity_percent': 80.0,
            'road_surface': 'dry',
            'weather': 'clear'
        },
        'load_profile': {
            'load_percent': 85.0,
            'speed_profile': 'highway',
            'distance_km': 200.0
        },
        'target_components': ['High_Voltage_Battery', 'Battery_Management_System'],
        'target_systems': ['Battery', 'Thermal'],
        'regulatory_standards': ['UNECE_R100', 'ISO_6469'],
        'historical_results': [{'passed': True}, {'passed': True}],
        'applicable_platforms': ['EV'],
        'applicable_models': ['Ariya', 'Leaf']
    }
    
    unified_emb = pipeline.create_unified_embedding(test_scenario)
    print(f"[OK] Unified embedding shape: {unified_emb.shape}")
    print(f"     Text portion: {pipeline.text_dim}")
    print(f"     Structured portion: {pipeline.structured_dim}")
    print(f"     Graph portion: {pipeline.graph_dim}")
    
    print("\n[OK] Embedding pipeline test complete")

