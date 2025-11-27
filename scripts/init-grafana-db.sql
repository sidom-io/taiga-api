-- Create separate database for Grafana
-- This runs automatically when PostgreSQL container starts

CREATE DATABASE grafana;
GRANT ALL PRIVILEGES ON DATABASE grafana TO taiga;
