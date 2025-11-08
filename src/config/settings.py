"""
Configuration management for VTA using Pydantic settings.
Reads from environment variables and .env file.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
import logging
import socket
import re

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation and environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Neo4j Configuration
    # Auto-detect: use 'neo4j' hostname in Docker, 'localhost' when running locally
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="please_change_me", description="Neo4j password")
    
    @model_validator(mode='after')
    def auto_detect_neo4j_uri(self):
        """Auto-detect Neo4j URI based on environment (Docker vs local)."""
        # If URI contains 'neo4j' hostname (Docker service name), check if it resolves
        if 'neo4j' in self.neo4j_uri and 'localhost' not in self.neo4j_uri:
            try:
                # Try to resolve 'neo4j' hostname (Docker service name)
                socket.gethostbyname('neo4j')
                # If successful, we're in Docker - keep the Docker hostname
                logger.debug("Detected Docker environment, using neo4j:7687")
            except (socket.gaierror, OSError):
                # Can't resolve 'neo4j', we're running locally - use localhost
                logger.info("Detected local environment, changing neo4j hostname to localhost")
                # Replace neo4j hostname with localhost, preserving port and protocol
                if 'neo4j:7687' in self.neo4j_uri:
                    self.neo4j_uri = self.neo4j_uri.replace('neo4j:7687', 'localhost:7687')
                elif 'neo4j:' in self.neo4j_uri:
                    # Handle custom ports
                    self.neo4j_uri = re.sub(r'neo4j:(\d+)', r'localhost:\1', self.neo4j_uri)
                else:
                    # Fallback: replace any occurrence of 'neo4j' with 'localhost'
                    self.neo4j_uri = self.neo4j_uri.replace('neo4j', 'localhost')
        return self
    
    # PostgreSQL + pgvector Configuration
    pg_conn: str = Field(
        default="postgresql+psycopg2://postgres:pass@localhost:5432/vta",
        description="PostgreSQL connection string"
    )
    
    # Business Configuration
    engineering_hourly_rate: float = Field(default=75.0, ge=0, description="Engineering hourly rate in GBP")
    campaigns_per_year: int = Field(default=8, ge=1, description="Number of test campaigns per year")
    
    # HuggingFace LLM Configuration (Local, Offline)
    use_mock_llm: bool = Field(default=True, description="Use mock LLM for testing (set to False for production)")
    hf_llm_model_id: str = Field(
        default="mock-llm",
        description="HuggingFace model ID for local inference (or 'mock-llm' for testing)"
    )
    hf_device: str = Field(default="auto", description="Device for model inference (auto/cuda/cpu)")
    hf_load_8bit: bool = Field(default=False, description="Enable 8-bit quantization if GPU available")
    hf_max_new_tokens: int = Field(default=512, ge=1, le=4096, description="Max tokens to generate")
    hf_temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature")
    
    # Embedding Model
    embedding_model_name: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="SentenceTransformer model for embeddings"
    )
    
    # Application Settings
    app_name: str = Field(default="Virtual Testing Assistant", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard Python logging levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper
    
    def log_config(self) -> None:
        """Log the resolved configuration (masking sensitive values)."""
        config_dict = self.model_dump()
        
        # Mask sensitive fields
        sensitive_fields = ["neo4j_password", "pg_conn"]
        for field in sensitive_fields:
            if field in config_dict and config_dict[field]:
                config_dict[field] = "***MASKED***"
        
        logger.info(f"Resolved Configuration for {self.app_name}:")
        for key, value in config_dict.items():
            logger.info(f"  {key}: {value}")
    
    def get_pg_host(self) -> str:
        """Extract PostgreSQL host from connection string."""
        try:
            # Extract host from connection string
            parts = self.pg_conn.split("@")
            if len(parts) > 1:
                host_port = parts[1].split("/")[0].split(":")[0]
                return host_port
            return "localhost"
        except Exception:
            return "localhost"
    
    def get_pg_database(self) -> str:
        """Extract PostgreSQL database name from connection string."""
        try:
            parts = self.pg_conn.split("/")
            return parts[-1]
        except Exception:
            return "vta"


# Global settings instance
settings = Settings()


def configure_logging() -> None:
    """Configure application logging based on settings."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


# Configure logging on import
configure_logging()


if __name__ == "__main__":
    # Test configuration loading and logging
    settings.log_config()
    print(f"\n[OK] Configuration loaded successfully!")
    print(f"   Neo4j URI: {settings.neo4j_uri}")
    print(f"   PostgreSQL Database: {settings.get_pg_database()}")
    print(f"   HF Model: {settings.hf_llm_model_id}")
    print(f"   Engineering Rate: GBP{settings.engineering_hourly_rate}/hour")

