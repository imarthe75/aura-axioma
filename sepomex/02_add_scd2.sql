/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 02: ADD SCD2 COLUMNS AND INDICES
================================================================================
Descripción:
  Agrega columnas de Slowly Changing Dimension Type 2 (SCD2) a todas las
  tablas del esquema sepomex para mantener historial de cambios con
  validez temporal.

Columnas agregadas:
  - scd_fecha_inicio: Timestamp de inicio de vigencia
  - scd_fecha_fin: Timestamp de fin de vigencia (NULL = vigente)
  - scd_vigente: Bandera booleana de vigencia actual
  - scd_version: Número de versión incremental
  - scd_hash: Hash MD5 de valores clave para detectar cambios

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

-- ============================================================================
-- TABLA: sepomex.ctpaises
-- Clave Natural: upper(trim(cvisoalpha3))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctpaises...'

ALTER TABLE sepomex.ctpaises
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

-- CHECK de temporalidad
ALTER TABLE sepomex.ctpaises
ADD CONSTRAINT ck_ctpaises_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

-- Índice único parcial por clave natural (solo vigentes)
CREATE UNIQUE INDEX IF NOT EXISTS idx_ctpaises_scd2_vigente
    ON sepomex.ctpaises(UPPER(TRIM(cvisoalpha3)))
    WHERE scd_vigente = TRUE;

-- Índice para búsquedas por vigencia
CREATE INDEX IF NOT EXISTS idx_ctpaises_scd_vigente
    ON sepomex.ctpaises(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.cttiposzona
-- Clave Natural: upper(trim(cvtipozona))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.cttiposzona...'

ALTER TABLE sepomex.cttiposzona
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.cttiposzona
ADD CONSTRAINT ck_cttiposzona_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cttiposzona_scd2_vigente
    ON sepomex.cttiposzona(UPPER(TRIM(cvtipozona)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_cttiposzona_scd_vigente
    ON sepomex.cttiposzona(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.cttipoasentamiento
-- Clave Natural: upper(trim(dstipoasentamiento))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.cttipoasentamiento...'

ALTER TABLE sepomex.cttipoasentamiento
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.cttipoasentamiento
ADD CONSTRAINT ck_cttipoasentamiento_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cttipoasentamiento_scd2_vigente
    ON sepomex.cttipoasentamiento(UPPER(TRIM(dstipoasentamiento)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_cttipoasentamiento_scd_vigente
    ON sepomex.cttipoasentamiento(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctestados
-- Clave Natural: (llpais, upper(trim(cvestado)))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctestados...'

ALTER TABLE sepomex.ctestados
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctestados
ADD CONSTRAINT ck_ctestados_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctestados_scd2_vigente
    ON sepomex.ctestados(llpais, UPPER(TRIM(cvestado)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctestados_scd_vigente
    ON sepomex.ctestados(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctmunicipios
-- Clave Natural: (llestado, upper(trim(cvmunicipio)))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctmunicipios...'

ALTER TABLE sepomex.ctmunicipios
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctmunicipios
ADD CONSTRAINT ck_ctmunicipios_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctmunicipios_scd2_vigente
    ON sepomex.ctmunicipios(llestado, UPPER(TRIM(cvmunicipio)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctmunicipios_scd_vigente
    ON sepomex.ctmunicipios(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctcodigospostales
-- Clave Natural: upper(trim(cvcodigopostal))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctcodigospostales...'

ALTER TABLE sepomex.ctcodigospostales
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctcodigospostales
ADD CONSTRAINT ck_ctcodigospostales_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctcodigospostales_scd2_vigente
    ON sepomex.ctcodigospostales(UPPER(TRIM(cvcodigopostal)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctcodigospostales_scd_vigente
    ON sepomex.ctcodigospostales(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctlocalidades
-- Clave Natural: (llmunicipio, upper(trim(COALESCE(cvlocalidad, dslocalidad))))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctlocalidades...'

ALTER TABLE sepomex.ctlocalidades
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctlocalidades
ADD CONSTRAINT ck_ctlocalidades_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctlocalidades_scd2_vigente
    ON sepomex.ctlocalidades(llmunicipio, UPPER(TRIM(COALESCE(cvlocalidad, dslocalidad))))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctlocalidades_scd_vigente
    ON sepomex.ctlocalidades(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctasentamientos
-- Clave Natural: (llmunicipio, upper(trim(dsasentamiento)), COALESCE(lltipoasentamiento, -1), COALESCE(lltipozona, -1), llcodigopostal)
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctasentamientos...'

ALTER TABLE sepomex.ctasentamientos
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctasentamientos
ADD CONSTRAINT ck_ctasentamientos_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctasentamientos_scd2_vigente
    ON sepomex.ctasentamientos(
        llmunicipio, 
        UPPER(TRIM(dsasentamiento)), 
        COALESCE(lltipoasentamiento, -1), 
        COALESCE(lltipozona, -1), 
        llcodigopostal
    )
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctasentamientos_scd_vigente
    ON sepomex.ctasentamientos(scd_vigente);

-- ============================================================================
-- TABLA: sepomex.ctciudades
-- Clave Natural: (llasentamiento, upper(trim(dsciudad)))
-- ============================================================================

\echo 'Agregando SCD2 a sepomex.ctciudades...'

ALTER TABLE sepomex.ctciudades
ADD COLUMN IF NOT EXISTS scd_fecha_inicio TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS scd_fecha_fin TIMESTAMPTZ DEFAULT NULL,
ADD COLUMN IF NOT EXISTS scd_vigente BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scd_version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS scd_hash TEXT;

ALTER TABLE sepomex.ctciudades
ADD CONSTRAINT ck_ctciudades_scd_temporality 
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ctciudades_scd2_vigente
    ON sepomex.ctciudades(llasentamiento, UPPER(TRIM(dsciudad)))
    WHERE scd_vigente = TRUE;

CREATE INDEX IF NOT EXISTS idx_ctciudades_scd_vigente
    ON sepomex.ctciudades(scd_vigente);

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

\echo '✓ Columnas SCD2 agregadas a todas las tablas'
\echo '✓ Índices únicos parciales (vigencia) creados'
\echo '✓ Índices de búsqueda por vigencia creados'
\echo '✓ Constraints de temporalidad implementados'
\echo '✓ Script 02 completado exitosamente'

