-- Aura Axioma SSoT - DDL Refactoring
-- Habilita PostGIS, pg_trgm, modela fusiones de CASFIM e implementa índices de búsqueda predictiva trigram.

-- 1. Extensiones requeridas
CREATE EXTENSION IF NOT EXISTS postgis SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pg_trgm SCHEMA public;

-- 2. Integración Geo-Espacial INEGI
-- Habilitar columna geométrica en inegi.localidades para soporte de polígonos/geometrías espaciales
ALTER TABLE inegi.localidades ADD COLUMN IF NOT EXISTS geom public.GEOMETRY(Geometry, 4326);
CREATE INDEX IF NOT EXISTS idx_localidades_geom ON inegi.localidades USING GIST(geom);

-- 3. Índices de Búsqueda Predictiva Trigram (Fuzzy Search)
-- Para búsquedas instantáneas en catálogos masivos
CREATE INDEX IF NOT EXISTS idx_geo_asentamientos_fuzzy ON geo.asentamientos USING gin (name public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_fiscal_productos_fuzzy ON fiscal.cat_prod_serv USING gin (description public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_fiscal_productos_code_trgm ON fiscal.cat_prod_serv USING gin (code public.gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_fiscal_unidades_fuzzy ON fiscal.cat_unidades USING gin (name public.gin_trgm_ops);

-- 4. Modificaciones del Módulo Financiero (CASFIM)
-- Regla de Negocio: Mapeo de fusiones y estatus operativo en instituciones bancarias
ALTER TABLE financial.instituciones_bancarias ADD COLUMN IF NOT EXISTS estatus VARCHAR(20) NOT NULL DEFAULT 'ACTIVA' CHECK (estatus IN ('ACTIVA', 'FUSIONADA', 'CANCELADA'));
ALTER TABLE financial.instituciones_bancarias ADD COLUMN IF NOT EXISTS sucesora_id UUID REFERENCES financial.instituciones_bancarias(id);

-- Índice parcial para instituciones actuales y estatus
CREATE INDEX IF NOT EXISTS idx_financial_instituciones_estatus ON financial.instituciones_bancarias(estatus) WHERE scd_is_current = TRUE;
