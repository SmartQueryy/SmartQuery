-- Migration: 002_create_projects_table.sql
-- Description: Create projects table with foreign key relationship to users table
-- Date: January 2025

-- Create project status enum type
CREATE TYPE project_status AS ENUM ('uploading', 'processing', 'ready', 'error');

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    csv_filename VARCHAR(255) NOT NULL,
    csv_path TEXT NOT NULL,
    row_count INTEGER NOT NULL DEFAULT 0,
    column_count INTEGER NOT NULL DEFAULT 0,
    columns_metadata JSONB,
    status project_status NOT NULL DEFAULT 'uploading',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at);
CREATE INDEX IF NOT EXISTS idx_projects_user_status ON projects(user_id, status);
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at DESC);

-- Apply trigger to projects table for automatic updated_at updates
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add constraints
ALTER TABLE projects ADD CONSTRAINT projects_name_check 
    CHECK (LENGTH(TRIM(name)) > 0 AND LENGTH(TRIM(name)) <= 255);

ALTER TABLE projects ADD CONSTRAINT projects_csv_filename_check 
    CHECK (LENGTH(TRIM(csv_filename)) > 0);

ALTER TABLE projects ADD CONSTRAINT projects_csv_path_check 
    CHECK (LENGTH(TRIM(csv_path)) > 0);

ALTER TABLE projects ADD CONSTRAINT projects_row_count_check 
    CHECK (row_count >= 0);

ALTER TABLE projects ADD CONSTRAINT projects_column_count_check 
    CHECK (column_count >= 0);

ALTER TABLE projects ADD CONSTRAINT projects_description_check 
    CHECK (description IS NULL OR LENGTH(TRIM(description)) <= 1000);

-- Add comments for documentation
COMMENT ON TABLE projects IS 'User projects containing CSV data for analysis';
COMMENT ON COLUMN projects.id IS 'Primary key, UUID';
COMMENT ON COLUMN projects.user_id IS 'Foreign key to users table';
COMMENT ON COLUMN projects.name IS 'Project name, user-defined';
COMMENT ON COLUMN projects.description IS 'Optional project description';
COMMENT ON COLUMN projects.csv_filename IS 'Original CSV filename';
COMMENT ON COLUMN projects.csv_path IS 'Storage path for CSV file';
COMMENT ON COLUMN projects.row_count IS 'Number of rows in CSV';
COMMENT ON COLUMN projects.column_count IS 'Number of columns in CSV';
COMMENT ON COLUMN projects.columns_metadata IS 'JSON metadata about CSV columns';
COMMENT ON COLUMN projects.status IS 'Current processing status of the project';
COMMENT ON COLUMN projects.created_at IS 'Project creation timestamp';
COMMENT ON COLUMN projects.updated_at IS 'Last update timestamp';

-- Add comment on enum type
COMMENT ON TYPE project_status IS 'Project processing status: uploading, processing, ready, error'; 