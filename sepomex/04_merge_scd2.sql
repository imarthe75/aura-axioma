/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 04: MERGE SCD2 - UPDATE SEPOMEX WITH STAGING DATA
================================================================================
Descripción:
  Ejecuta operaciones MERGE SCD2 para cada catálogo, integrando datos de
  sepomex_stage hacia sepomex con gestión completa de temporalidad.

Lógica SCD2:
  - Si la clave natural NO existe: INSERT nuevo registro (versión 1, vigente)
  - Si la clave existe y scd_hash cambió: 
    * Cerrar versión anterior (scd_vigente=FALSE, scd_fecha_fin=NOW())
    * Insertar nueva versión (scd_version=MAX+1, scd_vigente=TRUE)
  - Si la clave existe y scd_hash es igual: SIN CAMBIOS

Orden de Procesamiento (respeta FKs):
  1. ctpaises (sin dependencias)
  2. cttiposzona (sin dependencias)
  3. cttipoasentamiento (sin dependencias)
  4. ctestados (→ ctpaises)
  5. ctmunicipios (→ ctestados)
  6. ctcodigospostales (sin dependencias)
  7. ctasentamientos (→ ctmunicipios, cttipoasentamiento, cttipozona, ctcodigospostales)

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

-- ============================================================================
-- PASO 1: MERGE ctpaises
-- ============================================================================

\echo 'Paso 1: MERGE en sepomex.ctpaises...'

MERGE INTO sepomex.ctpaises d
USING sepomex_stage.ctpaises s
ON d.llpais = s.llpais
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (llpais, cvisoalpha3, dspais, boactivo, scd_fecha_inicio, 
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llpais, s.cvisoalpha3, s.dspais, s.boactivo, NOW(), 
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

-- Insertar nuevas versiones para registros modificados
INSERT INTO sepomex.ctpaises (
    llpais, cvisoalpha3, dspais, boactivo, 
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash, 
    fcreacion, dsusuariocreacion
)
SELECT 
    s.llpais, s.cvisoalpha3, s.dspais, s.boactivo,
    NOW(), TRUE, 
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.ctpaises WHERE llpais = s.llpais),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.ctpaises s
WHERE EXISTS (
    SELECT 1 FROM sepomex.ctpaises d 
    WHERE d.llpais = s.llpais AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 2: MERGE cttiposzona
-- ============================================================================

\echo 'Paso 2: MERGE en sepomex.cttiposzona...'

MERGE INTO sepomex.cttiposzona d
USING sepomex_stage.cttiposzona s
ON d.lltipozona = s.lltipozona
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (lltipozona, cvtipozona, dstipozona, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.lltipozona, s.cvtipozona, s.dstipozona, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.cttiposzona (
    lltipozona, cvtipozona, dstipozona, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.lltipozona, s.cvtipozona, s.dstipozona, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.cttiposzona WHERE lltipozona = s.lltipozona),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.cttiposzona s
WHERE EXISTS (
    SELECT 1 FROM sepomex.cttiposzona d
    WHERE d.lltipozona = s.lltipozona AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 3: MERGE cttipoasentamiento
-- ============================================================================

\echo 'Paso 3: MERGE en sepomex.cttipoasentamiento...'

MERGE INTO sepomex.cttipoasentamiento d
USING sepomex_stage.cttipoasentamiento s
ON d.lltipoasentamiento = s.lltipoasentamiento
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (lltipoasentamiento, dstipoasentamiento, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.lltipoasentamiento, s.dstipoasentamiento, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.cttipoasentamiento (
    lltipoasentamiento, dstipoasentamiento, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.lltipoasentamiento, s.dstipoasentamiento, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.cttipoasentamiento WHERE lltipoasentamiento = s.lltipoasentamiento),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.cttipoasentamiento s
WHERE EXISTS (
    SELECT 1 FROM sepomex.cttipoasentamiento d
    WHERE d.lltipoasentamiento = s.lltipoasentamiento AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 4: MERGE ctestados
-- ============================================================================

\echo 'Paso 4: MERGE en sepomex.ctestados...'

MERGE INTO sepomex.ctestados d
USING sepomex_stage.ctestados s
ON d.llestado = s.llestado
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (llestado, llpais, cvestado, dsestado, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llestado, s.llpais, s.cvestado, s.dsestado, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.ctestados (
    llestado, llpais, cvestado, dsestado, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llestado, s.llpais, s.cvestado, s.dsestado, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.ctestados WHERE llestado = s.llestado),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.ctestados s
WHERE EXISTS (
    SELECT 1 FROM sepomex.ctestados d
    WHERE d.llestado = s.llestado AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 5: MERGE ctmunicipios
-- ============================================================================

\echo 'Paso 5: MERGE en sepomex.ctmunicipios...'

MERGE INTO sepomex.ctmunicipios d
USING sepomex_stage.ctmunicipios s
ON d.llmunicipio = s.llmunicipio
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (llmunicipio, llestado, cvmunicipio, dsmunicipo, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llmunicipio, s.llestado, s.cvmunicipio, s.dsmunicipo, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.ctmunicipios (
    llmunicipio, llestado, cvmunicipio, dsmunicipo, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llmunicipio, s.llestado, s.cvmunicipio, s.dsmunicipo, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.ctmunicipios WHERE llmunicipio = s.llmunicipio),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.ctmunicipios s
WHERE EXISTS (
    SELECT 1 FROM sepomex.ctmunicipios d
    WHERE d.llmunicipio = s.llmunicipio AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 6: MERGE ctcodigospostales
-- ============================================================================

\echo 'Paso 6: MERGE en sepomex.ctcodigospostales...'

MERGE INTO sepomex.ctcodigospostales d
USING sepomex_stage.ctcodigospostales s
ON d.llcodigopostal = s.llcodigopostal
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (llcodigopostal, cvcodigopostal, dscodigopostal, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llcodigopostal, s.cvcodigopostal, s.dscodigopostal, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.ctcodigospostales (
    llcodigopostal, cvcodigopostal, dscodigopostal, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llcodigopostal, s.cvcodigopostal, s.dscodigopostal, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.ctcodigospostales WHERE llcodigopostal = s.llcodigopostal),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.ctcodigospostales s
WHERE EXISTS (
    SELECT 1 FROM sepomex.ctcodigospostales d
    WHERE d.llcodigopostal = s.llcodigopostal AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 7: MERGE ctasentamientos (ÚLTIMA DEPENDENCIA)
-- ============================================================================

\echo 'Paso 7: MERGE en sepomex.ctasentamientos...'

MERGE INTO sepomex.ctasentamientos d
USING sepomex_stage.ctasentamientos s
ON d.llasentamiento = s.llasentamiento
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_MERGE'
WHEN NOT MATCHED THEN
    INSERT (llasentamiento, llmunicipio, dsasentamiento, lltipoasentamiento, 
            lltipozona, llcodigopostal, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llasentamiento, s.llmunicipio, s.dsasentamiento, s.lltipoasentamiento,
            s.lltipozona, s.llcodigopostal, s.boactivo, NOW(),
            TRUE, 1, s.scd_hash, NOW(), 'SEPOMEX_MERGE');

INSERT INTO sepomex.ctasentamientos (
    llasentamiento, llmunicipio, dsasentamiento, lltipoasentamiento,
    lltipozona, llcodigopostal, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llasentamiento, s.llmunicipio, s.dsasentamiento, s.lltipoasentamiento,
    s.lltipozona, s.llcodigopostal, s.boactivo,
    NOW(), TRUE,
    (SELECT COALESCE(MAX(scd_version), 0) + 1 FROM sepomex.ctasentamientos WHERE llasentamiento = s.llasentamiento),
    s.scd_hash,
    NOW(), 'SEPOMEX_MERGE'
FROM sepomex_stage.ctasentamientos s
WHERE EXISTS (
    SELECT 1 FROM sepomex.ctasentamientos d
    WHERE d.llasentamiento = s.llasentamiento AND d.scd_vigente = FALSE AND d.scd_hash IS DISTINCT FROM s.scd_hash
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

\echo '✓ MERGE completado para todas las tablas'
\echo ''
\echo 'Resumen de registros vigentes en sepomex.*:'

SELECT
    'ctpaises' AS tabla, COUNT(*) AS vigentes
FROM sepomex.ctpaises WHERE scd_vigente = TRUE
UNION ALL
SELECT 'cttiposzona', COUNT(*) FROM sepomex.cttiposzona WHERE scd_vigente = TRUE
UNION ALL
SELECT 'cttipoasentamiento', COUNT(*) FROM sepomex.cttipoasentamiento WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctestados', COUNT(*) FROM sepomex.ctestados WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctmunicipios', COUNT(*) FROM sepomex.ctmunicipios WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctcodigospostales', COUNT(*) FROM sepomex.ctcodigospostales WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctlocalidades', COUNT(*) FROM sepomex.ctlocalidades WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctasentamientos', COUNT(*) FROM sepomex.ctasentamientos WHERE scd_vigente = TRUE
ORDER BY tabla;

\echo '✓ Script 04 completado exitosamente'

