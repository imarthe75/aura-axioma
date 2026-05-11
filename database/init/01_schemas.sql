-- Aura Axioma - Database Initialization
-- Schema definitions for Master Catalog Service

-- Admin schema for system management and ingestion logs
CREATE SCHEMA IF NOT EXISTS admin;

-- Staging schema for bulk loads and SCD2 comparisons
CREATE SCHEMA IF NOT EXISTS staging;

-- Business schemas
CREATE SCHEMA IF NOT EXISTS geo;       -- SEPOMEX, INEGI
CREATE SCHEMA IF NOT EXISTS fiscal;    -- SAT (Anexo 20)
CREATE SCHEMA IF NOT EXISTS financial; -- SPEI, Divisas
CREATE SCHEMA IF NOT EXISTS calendars; -- Holidays, Business Periods

COMMENT ON SCHEMA admin IS 'Metadatos del sistema y logs de ingesta';
COMMENT ON SCHEMA staging IS 'Tablas temporales para carga masiva y lógica SCD2';
COMMENT ON SCHEMA geo IS 'Catálogos geográficos (SEPOMEX/INEGI)';
COMMENT ON SCHEMA fiscal IS 'Catálogos fiscales (SAT)';
COMMENT ON SCHEMA financial IS 'Catálogos bancarios y de divisas';
COMMENT ON SCHEMA calendars IS 'Calendarios operativos y días festivos';
