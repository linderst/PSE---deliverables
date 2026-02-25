-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the table for ICD-10 data from classification registry file
CREATE TABLE icd_class (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    kind VARCHAR(50),              -- chapter, category, etc.
    title TEXT NOT NULL,
    definition TEXT,
    parent_code VARCHAR(10),       -- for hierarchy
    is_leaf BOOLEAN,
    para295 CHAR(1),
    para301 CHAR(1),
    sex_code CHAR(1),
    age_low VARCHAR(10),
    age_high VARCHAR(10),
    infectious BOOLEAN,
    content BOOLEAN
);

-- Create synonym table from alphabetical registry file
CREATE TABLE icd_synonym (
    id SERIAL PRIMARY KEY,
    icd_code VARCHAR(10) REFERENCES icd_class(code),
    term TEXT NOT NULL,
    coding_type INT,
    is_printed BOOLEAN
);

-- Create table with embedded vectors
CREATE TABLE icd_embedding (
    id SERIAL PRIMARY KEY,
    icd_code VARCHAR(10) REFERENCES icd_class(code),
    source_type VARCHAR(20),  -- 'title', 'synonym', 'definition'
    source_id INT,            -- reference id
    embedding vector(768)     -- depends on model, CHECK VECTOR SIZE!
);