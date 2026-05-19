/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 01: CREATE SCHEMA AND REPLICA TABLES
================================================================================
Descripción:
  Crea esquemas de trabajo (sepomex, sepomex_stage) y réplicas de las tablas
  del catálogo de códigos postales mexicanos.
  
  Las tablas se crean VACÍAS, sin datos iniciales.
  Los datos se cargarán mediante MERGE desde el archivo CPdescarga.txt.

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

-- Crear esquemas
CREATE SCHEMA IF NOT EXISTS sepomex;
COMMENT ON SCHEMA sepomex IS 'Repositorio validado del catálogo SEPOMEX con SCD2';

CREATE SCHEMA IF NOT EXISTS sepomex_stage;
COMMENT ON SCHEMA sepomex_stage IS 'Zona de staging para carga incremental de SEPOMEX';

-- ============================================================================
-- TABLA: sepomex.ctpaises
-- Clave Natural: cvisoalpha3
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctpaises (
    llpais BIGINT PRIMARY KEY,
    cvisoalpha3 VARCHAR(3) NOT NULL UNIQUE,
    dspais VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100)
);
COMMENT ON TABLE sepomex.ctpaises IS 'Catálogo de países (SCD2)';

-- ============================================================================
-- TABLA: sepomex.cttiposzona
-- Clave Natural: cvtipozona
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.cttiposzona (
    lltipozona BIGINT PRIMARY KEY,
    cvtipozona VARCHAR(10) NOT NULL UNIQUE,
    dstipozona VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100)
);
COMMENT ON TABLE sepomex.cttiposzona IS 'Catálogo de tipos de zona (SCD2)';

-- ============================================================================
-- TABLA: sepomex.cttipoasentamiento
-- Clave Natural: dstipoasentamiento
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.cttipoasentamiento (
    lltipoasentamiento BIGINT PRIMARY KEY,
    dstipoasentamiento VARCHAR(100) NOT NULL UNIQUE,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100)
);
COMMENT ON TABLE sepomex.cttipoasentamiento IS 'Catálogo de tipos de asentamiento (SCD2)';

-- ============================================================================
-- TABLA: sepomex.ctestados
-- Clave Natural: (llpais, cvestado)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctestados (
    llestado BIGINT PRIMARY KEY,
    llpais BIGINT NOT NULL,
    cvestado VARCHAR(10) NOT NULL,
    dsestado VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100),
    CONSTRAINT fk_ctestados_ctpaises FOREIGN KEY (llpais) 
        REFERENCES sepomex.ctpaises(llpais)
);
COMMENT ON TABLE sepomex.ctestados IS 'Catálogo de estados (SCD2)';
CREATE UNIQUE INDEX idx_ctestados_natural_key 
    ON sepomex.ctestados(llpais, UPPER(TRIM(cvestado)));

-- ============================================================================
-- TABLA: sepomex.ctmunicipios
-- Clave Natural: (llestado, cvmunicipio)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctmunicipios (
    llmunicipio BIGINT PRIMARY KEY,
    llestado BIGINT NOT NULL,
    cvmunicipio VARCHAR(10) NOT NULL,
    dsmunicipo VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100),
    CONSTRAINT fk_ctmunicipios_ctestados FOREIGN KEY (llestado) 
        REFERENCES sepomex.ctestados(llestado)
);
COMMENT ON TABLE sepomex.ctmunicipios IS 'Catálogo de municipios (SCD2)';
CREATE UNIQUE INDEX idx_ctmunicipios_natural_key 
    ON sepomex.ctmunicipios(llestado, UPPER(TRIM(cvmunicipio)));

-- ============================================================================
-- TABLA: sepomex.ctcodigospostales
-- Clave Natural: cvcodigopostal
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctcodigospostales (
    llcodigopostal BIGINT PRIMARY KEY,
    cvcodigopostal VARCHAR(10) NOT NULL UNIQUE,
    dscodigopostal VARCHAR(200),
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100)
);
COMMENT ON TABLE sepomex.ctcodigospostales IS 'Catálogo de códigos postales (SCD2)';

-- ============================================================================
-- TABLA: sepomex.ctlocalidades
-- Clave Natural: (llmunicipio, cvlocalidad || dslocalidad)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctlocalidades (
    lllocalidad BIGINT PRIMARY KEY,
    llmunicipio BIGINT NOT NULL,
    cvlocalidad VARCHAR(10),
    dslocalidad VARCHAR(100),
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100),
    CONSTRAINT fk_ctlocalidades_ctmunicipios FOREIGN KEY (llmunicipio) 
        REFERENCES sepomex.ctmunicipios(llmunicipio)
);
COMMENT ON TABLE sepomex.ctlocalidades IS 'Catálogo de localidades (SCD2)';
CREATE UNIQUE INDEX idx_ctlocalidades_natural_key 
    ON sepomex.ctlocalidades(llmunicipio, UPPER(TRIM(COALESCE(cvlocalidad, dslocalidad))));

-- ============================================================================
-- TABLA: sepomex.ctasentamientos
-- Clave Natural: (llmunicipio, dsasentamiento, lltipoasentamiento, lltipozona, llcodigopostal)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctasentamientos (
    llasentamiento BIGINT PRIMARY KEY,
    llmunicipio BIGINT NOT NULL,
    dsasentamiento VARCHAR(100) NOT NULL,
    lltipoasentamiento BIGINT,
    lltipozona BIGINT,
    llcodigopostal BIGINT NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100),
    CONSTRAINT fk_ctasentamientos_ctmunicipios FOREIGN KEY (llmunicipio) 
        REFERENCES sepomex.ctmunicipios(llmunicipio),
    CONSTRAINT fk_ctasentamientos_cttipoasentamiento FOREIGN KEY (lltipoasentamiento) 
        REFERENCES sepomex.cttipoasentamiento(lltipoasentamiento),
    CONSTRAINT fk_ctasentamientos_cttipozona FOREIGN KEY (lltipozona) 
        REFERENCES sepomex.cttiposzona(lltipozona),
    CONSTRAINT fk_ctasentamientos_ctcodigospostales FOREIGN KEY (llcodigopostal) 
        REFERENCES sepomex.ctcodigospostales(llcodigopostal)
);
COMMENT ON TABLE sepomex.ctasentamientos IS 'Catálogo de asentamientos (SCD2)';
CREATE UNIQUE INDEX idx_ctasentamientos_natural_key 
    ON sepomex.ctasentamientos(
        llmunicipio, 
        UPPER(TRIM(dsasentamiento)), 
        COALESCE(lltipoasentamiento, -1), 
        COALESCE(lltipozona, -1), 
        llcodigopostal
    );

-- ============================================================================
-- TABLA: sepomex.ctciudades
-- Clave Natural: (llasentamiento, dsciudad)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sepomex.ctciudades (
    llciudad BIGINT PRIMARY KEY,
    llasentamiento BIGINT NOT NULL,
    dsciudad VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE,
    fcreacion TIMESTAMPTZ DEFAULT NOW(),
    fcmodificacion TIMESTAMPTZ DEFAULT NOW(),
    dsusuariocreacion VARCHAR(100),
    dsusuariomodifica VARCHAR(100),
    CONSTRAINT fk_ctciudades_ctasentamientos FOREIGN KEY (llasentamiento) 
        REFERENCES sepomex.ctasentamientos(llasentamiento)
);
COMMENT ON TABLE sepomex.ctciudades IS 'Catálogo de ciudades (SCD2)';
CREATE UNIQUE INDEX idx_ctciudades_natural_key 
    ON sepomex.ctciudades(llasentamiento, UPPER(TRIM(dsciudad)));

-- ============================================================================
-- TABLAS STAGING: Réplicas para MERGE SCD2
-- ============================================================================

CREATE TABLE IF NOT EXISTS sepomex_stage.ctpaises (
    llpais BIGINT PRIMARY KEY,
    cvisoalpha3 VARCHAR(3) NOT NULL,
    dspais VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.cttiposzona (
    lltipozona BIGINT PRIMARY KEY,
    cvtipozona VARCHAR(10) NOT NULL,
    dstipozona VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.cttipoasentamiento (
    lltipoasentamiento BIGINT PRIMARY KEY,
    dstipoasentamiento VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctestados (
    llestado BIGINT PRIMARY KEY,
    llpais BIGINT NOT NULL,
    cvestado VARCHAR(10) NOT NULL,
    dsestado VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctmunicipios (
    llmunicipio BIGINT PRIMARY KEY,
    llestado BIGINT NOT NULL,
    cvmunicipio VARCHAR(10) NOT NULL,
    dsmunicipo VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctcodigospostales (
    llcodigopostal BIGINT PRIMARY KEY,
    cvcodigopostal VARCHAR(10) NOT NULL,
    dscodigopostal VARCHAR(200),
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctlocalidades (
    lllocalidad BIGINT PRIMARY KEY,
    llmunicipio BIGINT NOT NULL,
    cvlocalidad VARCHAR(10),
    dslocalidad VARCHAR(100),
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctasentamientos (
    llasentamiento BIGINT PRIMARY KEY,
    llmunicipio BIGINT NOT NULL,
    dsasentamiento VARCHAR(100) NOT NULL,
    lltipoasentamiento BIGINT,
    lltipozona BIGINT,
    llcodigopostal BIGINT NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS sepomex_stage.ctciudades (
    llciudad BIGINT PRIMARY KEY,
    llasentamiento BIGINT NOT NULL,
    dsciudad VARCHAR(100) NOT NULL,
    boactivo BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- TABLA RAW (CARGA DIRECTA DEL ARCHIVO)
-- ============================================================================

CREATE TABLE IF NOT EXISTS sepomex_stage.sepomex_raw (
    d_codigo VARCHAR(10),
    d_asenta VARCHAR(100),
    d_tipo_asenta VARCHAR(50),
    d_mnpio VARCHAR(100),
    d_estado VARCHAR(100),
    d_ciudad VARCHAR(100),
    d_cp VARCHAR(10),
    c_estado NUMERIC(2,0),
    c_oficina NUMERIC(3,0),
    c_cp NUMERIC(5,0),
    c_tipo_asenta NUMERIC(2,0),
    c_mnpio NUMERIC(3,0),
    id_asenta_cpcons NUMERIC(6,0),
    d_zona VARCHAR(20),
    c_cve_ciudad NUMERIC(4,0)
);
COMMENT ON TABLE sepomex_stage.sepomex_raw IS 'Tabla RAW: carga directa de CPdescarga.txt';

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

\echo '✓ Esquemas creados: sepomex, sepomex_stage'
\echo '✓ Tablas catálogo creadas en sepomex.*'
\echo '✓ Tablas staging creadas en sepomex_stage.*'
\echo '✓ Script 01 completado exitosamente'

