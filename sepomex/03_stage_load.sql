/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 03: STAGE LOAD - LOAD AND TRANSFORM CPdescarga.txt
================================================================================
Descripción:
  Carga el archivo CPdescarga.txt desde la ruta especificada en la tabla
  sepomex_stage.sepomex_raw y genera derivadas transformadas listas para MERGE.

Fuente:
  Archivo oficial de Correos de México (SEPOMEX)
  URL: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
  
Formato de entrada:
  - Delimitador: |
  - Codificación: LATIN1
  - Primeras 2 líneas: nota legal + encabezados (excluidas con tail -n +3)

Reglas Deterministas Aplicadas:
  - llpais = 484 (México, ISO 3166-1)
  - llestado = 48400 + c_estado
  - llmunicipio = llestado * 1000 + c_mnpio
  - llcodigopostal = CAST(d_cp AS BIGINT)
  - lltipozona = 1 (Urbano) / 2 (Rural, por d_zona)
  - lltipoasentamiento = c_tipo_asenta

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

-- ============================================================================
-- PASO 1: VACIAR TABLAS DE STAGING (Idempotencia)
-- ============================================================================

\echo 'Paso 1: Limpiando tablas de staging...'

TRUNCATE TABLE sepomex_stage.sepomex_raw CASCADE;
TRUNCATE TABLE sepomex_stage.ctpaises CASCADE;
TRUNCATE TABLE sepomex_stage.cttiposzona CASCADE;
TRUNCATE TABLE sepomex_stage.cttipoasentamiento CASCADE;
TRUNCATE TABLE sepomex_stage.ctestados CASCADE;
TRUNCATE TABLE sepomex_stage.ctmunicipios CASCADE;
TRUNCATE TABLE sepomex_stage.ctcodigospostales CASCADE;
TRUNCATE TABLE sepomex_stage.ctlocalidades CASCADE;
TRUNCATE TABLE sepomex_stage.ctasentamientos CASCADE;
TRUNCATE TABLE sepomex_stage.ctciudades CASCADE;

-- ============================================================================
-- PASO 2: CARGAR ARCHIVO RAW
-- ============================================================================

\echo 'Paso 2: Cargando CPdescarga.txt en sepomex_stage.sepomex_raw...'

-- RUTA DEL ARCHIVO EN SERVIDOR LINUX
-- Ubicación: /home/casmartdb/db/sepomex/CPdescarga.txt

COPY sepomex_stage.sepomex_raw (
    d_codigo, d_asenta, d_tipo_asenta, d_mnpio, d_estado,
    d_ciudad, d_cp, c_estado, c_oficina, c_cp,
    c_tipo_asenta, c_mnpio, id_asenta_cpcons, d_zona, c_cve_ciudad
)
FROM PROGRAM 'tail -n +3 /home/casmartdb/db/sepomex/CPdescarga.txt'
WITH (
    FORMAT csv,
    DELIMITER '|',
    HEADER FALSE,
    ENCODING 'LATIN1',
    NULL ''
);

\echo '✓ Carga RAW completada'

-- ============================================================================
-- PASO 3: CARGAR ctpaises (HARDCODEADO PARA MÉXICO)
-- ============================================================================

\echo 'Paso 3: Transformando ctpaises...'

INSERT INTO sepomex_stage.ctpaises (
    llpais, cvisoalpha3, dspais, boactivo
)
VALUES (
    484,
    'MEX',
    'MÉXICO',
    TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 4: CARGAR cttiposzona
-- ============================================================================

\echo 'Paso 4: Transformando cttiposzona...'

INSERT INTO sepomex_stage.cttiposzona (
    lltipozona, cvtipozona, dstipozona, boactivo
)
VALUES
    (1, 'U', 'URBANO', TRUE),
    (2, 'R', 'RURAL', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 5: CARGAR cttipoasentamiento
-- ============================================================================

\echo 'Paso 5: Transformando cttipoasentamiento...'

INSERT INTO sepomex_stage.cttipoasentamiento (
    lltipoasentamiento, dstipoasentamiento, boactivo
)
SELECT DISTINCT
    CAST(raw.c_tipo_asenta AS BIGINT) AS lltipoasentamiento,
    COALESCE(raw.d_tipo_asenta, CONCAT('TIPO_', CAST(raw.c_tipo_asenta AS TEXT))) AS dstipoasentamiento,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.c_tipo_asenta IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 6: CARGAR ctestados
-- ============================================================================

\echo 'Paso 6: Transformando ctestados...'

INSERT INTO sepomex_stage.ctestados (
    llestado, llpais, cvestado, dsestado, boactivo
)
SELECT DISTINCT
    (48400 + CAST(raw.c_estado AS BIGINT)) AS llestado,
    484 AS llpais,
    LPAD(CAST(raw.c_estado AS TEXT), 2, '0') AS cvestado,
    COALESCE(raw.d_estado, CONCAT('ESTADO_', CAST(raw.c_estado AS TEXT))) AS dsestado,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.c_estado IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 7: CARGAR ctmunicipios
-- ============================================================================

\echo 'Paso 7: Transformando ctmunicipios...'

INSERT INTO sepomex_stage.ctmunicipios (
    llmunicipio, llestado, cvmunicipio, dsmunicipo, boactivo
)
SELECT DISTINCT
    ((48400 + CAST(raw.c_estado AS BIGINT)) * 1000 + CAST(raw.c_mnpio AS BIGINT)) AS llmunicipio,
    (48400 + CAST(raw.c_estado AS BIGINT)) AS llestado,
    LPAD(CAST(raw.c_mnpio AS TEXT), 3, '0') AS cvmunicipio,
    COALESCE(raw.d_mnpio, CONCAT('MUNICIPIO_', CAST(raw.c_mnpio AS TEXT))) AS dsmunicipo,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.c_estado IS NOT NULL AND raw.c_mnpio IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 8: CARGAR ctcodigospostales
-- ============================================================================

\echo 'Paso 8: Transformando ctcodigospostales...'

INSERT INTO sepomex_stage.ctcodigospostales (
    llcodigopostal, cvcodigopostal, dscodigopostal, boactivo
)
SELECT DISTINCT
    CAST(raw.d_cp AS BIGINT) AS llcodigopostal,
    CAST(raw.d_cp AS VARCHAR(10)) AS cvcodigopostal,
    CONCAT(raw.d_estado, ' - ', raw.d_mnpio, ' - CP: ', raw.d_cp) AS dscodigopostal,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.d_cp IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 9: CARGAR ctlocalidades
-- ============================================================================

\echo 'Paso 9: Transformando ctlocalidades...'

INSERT INTO sepomex_stage.ctlocalidades (
    lllocalidad, llmunicipio, cvlocalidad, dslocalidad, boactivo
)
SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY raw.c_estado, raw.c_mnpio, raw.id_asenta_cpcons) 
        + (SELECT COALESCE(MAX(lllocalidad), 0) FROM sepomex_stage.ctlocalidades) AS lllocalidad,
    ((48400 + CAST(raw.c_estado AS BIGINT)) * 1000 + CAST(raw.c_mnpio AS BIGINT)) AS llmunicipio,
    LPAD(CAST(raw.id_asenta_cpcons AS TEXT), 6, '0') AS cvlocalidad,
    COALESCE(raw.d_asenta, CONCAT('LOCALIDAD_', CAST(raw.id_asenta_cpcons AS TEXT))) AS dslocalidad,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.c_estado IS NOT NULL AND raw.c_mnpio IS NOT NULL AND raw.id_asenta_cpcons IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 10: CARGAR ctasentamientos
-- ============================================================================

\echo 'Paso 10: Transformando ctasentamientos...'

INSERT INTO sepomex_stage.ctasentamientos (
    llasentamiento, llmunicipio, dsasentamiento, lltipoasentamiento, 
    lltipozona, llcodigopostal, boactivo
)
SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY raw.c_estado, raw.c_mnpio, raw.d_asenta) 
        + (SELECT COALESCE(MAX(llasentamiento), 0) FROM sepomex_stage.ctasentamientos) AS llasentamiento,
    ((48400 + CAST(raw.c_estado AS BIGINT)) * 1000 + CAST(raw.c_mnpio AS BIGINT)) AS llmunicipio,
    COALESCE(raw.d_asenta, 'SIN_ESPECIFICAR') AS dsasentamiento,
    CAST(raw.c_tipo_asenta AS BIGINT) AS lltipoasentamiento,
    CASE WHEN UPPER(raw.d_zona) = 'R' THEN 2 ELSE 1 END AS lltipozona,
    CAST(raw.d_cp AS BIGINT) AS llcodigopostal,
    TRUE AS boactivo
FROM sepomex_stage.sepomex_raw raw
WHERE raw.c_estado IS NOT NULL 
  AND raw.c_mnpio IS NOT NULL 
  AND raw.d_cp IS NOT NULL
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 11: GENERAR HASHES SCD2 PARA TODAS LAS TABLAS DE STAGING
-- ============================================================================

\echo 'Paso 11: Generando hashes SCD2...'

-- ctpaises
UPDATE sepomex_stage.ctpaises
SET scd_hash = MD5(CONCAT_WS('|', cvisoalpha3, dspais))
WHERE scd_hash IS NULL;

-- cttiposzona
UPDATE sepomex_stage.cttiposzona
SET scd_hash = MD5(CONCAT_WS('|', cvtipozona, dstipozona))
WHERE scd_hash IS NULL;

-- cttipoasentamiento
UPDATE sepomex_stage.cttipoasentamiento
SET scd_hash = MD5(CONCAT_WS('|', dstipoasentamiento))
WHERE scd_hash IS NULL;

-- ctestados
UPDATE sepomex_stage.ctestados
SET scd_hash = MD5(CONCAT_WS('|', llpais, cvestado, dsestado))
WHERE scd_hash IS NULL;

-- ctmunicipios
UPDATE sepomex_stage.ctmunicipios
SET scd_hash = MD5(CONCAT_WS('|', llestado, cvmunicipio, dsmunicipo))
WHERE scd_hash IS NULL;

-- ctcodigospostales
UPDATE sepomex_stage.ctcodigospostales
SET scd_hash = MD5(CONCAT_WS('|', cvcodigopostal, dscodigopostal))
WHERE scd_hash IS NULL;

-- ctlocalidades
UPDATE sepomex_stage.ctlocalidades
SET scd_hash = MD5(CONCAT_WS('|', llmunicipio, cvlocalidad, dslocalidad))
WHERE scd_hash IS NULL;

-- ctasentamientos
UPDATE sepomex_stage.ctasentamientos
SET scd_hash = MD5(CONCAT_WS('|', llmunicipio, dsasentamiento, lltipoasentamiento, lltipozona, llcodigopostal))
WHERE scd_hash IS NULL;

-- ============================================================================
-- VERIFICACIÓN DE CARGA
-- ============================================================================

\echo '✓ Carga y transformación completadas'
\echo ''
\echo 'Resumen de registros cargados:'

SELECT 
    'ctpaises' AS tabla, COUNT(*) AS registros 
FROM sepomex_stage.ctpaises
UNION ALL
SELECT 'cttiposzona', COUNT(*) FROM sepomex_stage.cttiposzona
UNION ALL
SELECT 'cttipoasentamiento', COUNT(*) FROM sepomex_stage.cttipoasentamiento
UNION ALL
SELECT 'ctestados', COUNT(*) FROM sepomex_stage.ctestados
UNION ALL
SELECT 'ctmunicipios', COUNT(*) FROM sepomex_stage.ctmunicipios
UNION ALL
SELECT 'ctcodigospostales', COUNT(*) FROM sepomex_stage.ctcodigospostales
UNION ALL
SELECT 'ctlocalidades', COUNT(*) FROM sepomex_stage.ctlocalidades
UNION ALL
SELECT 'ctasentamientos', COUNT(*) FROM sepomex_stage.ctasentamientos
ORDER BY tabla;

\echo '✓ Script 03 completado exitosamente'

