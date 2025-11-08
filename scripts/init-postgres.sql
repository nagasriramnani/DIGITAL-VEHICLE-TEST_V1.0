-- Virtual Testing Assistant - PostgreSQL Initialization Script
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for VTA
CREATE SCHEMA IF NOT EXISTS vta;

-- Grant permissions
GRANT ALL ON SCHEMA vta TO vta_user;
GRANT ALL ON ALL TABLES IN SCHEMA vta TO vta_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA vta TO vta_user;

-- Create test_scenario_vectors table (if not exists)
CREATE TABLE IF NOT EXISTS vta.test_scenario_vectors (
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(255) UNIQUE NOT NULL,
    text_content TEXT,
    struct_features JSONB,
    graph_features JSONB,
    embedding vector(828),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_scenario_id ON vta.test_scenario_vectors(scenario_id);
CREATE INDEX IF NOT EXISTS idx_embedding_ivfflat ON vta.test_scenario_vectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION vta.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_test_scenario_vectors_updated_at BEFORE UPDATE ON vta.test_scenario_vectors
FOR EACH ROW EXECUTE FUNCTION vta.update_updated_at_column();

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'VTA PostgreSQL initialization complete!';
END $$;

