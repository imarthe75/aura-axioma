-- Aura Axioma - INEGI Specific Tables
-- Normalized Hierarchy

CREATE SCHEMA IF NOT EXISTS inegi;

CREATE TABLE IF NOT EXISTS inegi.localidades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID REFERENCES geo.municipios(id),
    clave_localidad CHAR(4) NOT NULL,
    nombre TEXT NOT NULL,
    latitud DECIMAL(9,6),
    longitud DECIMAL(9,6),
    altitud INTEGER,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    UNIQUE(municipality_id, clave_localidad, scd_is_current)
);
