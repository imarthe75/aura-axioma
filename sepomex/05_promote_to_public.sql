/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 05: PROMOTE TO PUBLIC - MERGE VALIDATED DATA TO PRODUCTION
================================================================================
Descripción:
  Migra datos validados del esquema sepomex hacia las tablas reales en public
  utilizando MERGE SCD2. Esto preserva el historial de cambios en producción.

Ventajas:
  - Validación previa en sepomex antes de afectar public
  - Traceabilidad completa: public.* también tiene SCD2
  - Sin TRUNCATE: solo inserta/actualiza registros nuevos o modificados
  - Aplica la MISMA lógica SCD2 que en staging

Orden de Procesamiento (respeta FKs):
  1. public.ctpaises
  2. public.cttiposzona
  3. public.cttipoasentamiento
  4. public.ctestados
  5. public.ctmunicipios
  6. public.ctcodigospostales
  7. public.ctasentamientos

PRECONDICIONES:
  - Se debe haber ejecutado exitosamente:
    01_create_sepomex_schema_and_tables.sql
    02_add_scd2.sql
    03_stage_load.sql
    04_merge_scd2.sql
  - Las tablas public.* deben tener estructura SCD2 idéntica a sepomex.*

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

-- ============================================================================
-- VERIFICACIÓN DE PRECONDICIONES
-- ============================================================================

\echo 'Verificando precondiciones...'

DO $$
BEGIN
    -- Verificar que sepomex tiene datos
    IF (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_vigente = TRUE) = 0 THEN
        RAISE EXCEPTION 'ERROR: sepomex.ctpaises no contiene datos vigentes. Ejecutar scripts 01-04 primero.';
    END IF;

    -- Verificar que public.* tiene estructura SCD2
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'ctpaises' 
        AND column_name = 'scd_vigente'
    ) THEN
        RAISE EXCEPTION 'ERROR: public.ctpaises no tiene estructura SCD2. Verificar tablas en public schema.';
    END IF;

    RAISE NOTICE 'Precondiciones verificadas exitosamente';
END $$;

-- ============================================================================
-- PASO 1: PROMOTE ctpaises
-- ============================================================================

\echo 'Paso 1: Promoviendo ctpaises hacia public...'

MERGE INTO public.ctpaises d
USING sepomex.ctpaises s
ON d.llpais = s.llpais
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (llpais, cvisoalpha3, dspais, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llpais, s.cvisoalpha3, s.dspais, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

-- Insertar nuevas versiones para registros modificados
INSERT INTO public.ctpaises (
    llpais, cvisoalpha3, dspais, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llpais, s.cvisoalpha3, s.dspais, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.ctpaises s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.ctpaises d
    WHERE d.llpais = s.llpais AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 2: PROMOTE cttiposzona
-- ============================================================================

\echo 'Paso 2: Promoviendo cttiposzona hacia public...'

MERGE INTO public.cttiposzona d
USING sepomex.cttiposzona s
ON d.lltipozona = s.lltipozona
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (lltipozona, cvtipozona, dstipozona, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.lltipozona, s.cvtipozona, s.dstipozona, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.cttiposzona (
    lltipozona, cvtipozona, dstipozona, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.lltipozona, s.cvtipozona, s.dstipozona, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.cttiposzona s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.cttiposzona d
    WHERE d.lltipozona = s.lltipozona AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 3: PROMOTE cttipoasentamiento
-- ============================================================================

\echo 'Paso 3: Promoviendo cttipoasentamiento hacia public...'

MERGE INTO public.cttipoasentamiento d
USING sepomex.cttipoasentamiento s
ON d.lltipoasentamiento = s.lltipoasentamiento
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (lltipoasentamiento, dstipoasentamiento, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.lltipoasentamiento, s.dstipoasentamiento, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.cttipoasentamiento (
    lltipoasentamiento, dstipoasentamiento, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.lltipoasentamiento, s.dstipoasentamiento, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.cttipoasentamiento s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.cttipoasentamiento d
    WHERE d.lltipoasentamiento = s.lltipoasentamiento AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 4: PROMOTE ctestados
-- ============================================================================

\echo 'Paso 4: Promoviendo ctestados hacia public...'

MERGE INTO public.ctestados d
USING sepomex.ctestados s
ON d.llestado = s.llestado
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (llestado, llpais, cvestado, dsestado, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llestado, s.llpais, s.cvestado, s.dsestado, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.ctestados (
    llestado, llpais, cvestado, dsestado, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llestado, s.llpais, s.cvestado, s.dsestado, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.ctestados s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.ctestados d
    WHERE d.llestado = s.llestado AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 5: PROMOTE ctmunicipios
-- ============================================================================

\echo 'Paso 5: Promoviendo ctmunicipios hacia public...'

MERGE INTO public.ctmunicipios d
USING sepomex.ctmunicipios s
ON d.llmunicipio = s.llmunicipio
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (llmunicipio, llestado, cvmunicipio, dsmunicipo, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llmunicipio, s.llestado, s.cvmunicipio, s.dsmunicipo, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.ctmunicipios (
    llmunicipio, llestado, cvmunicipio, dsmunicipo, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llmunicipio, s.llestado, s.cvmunicipio, s.dsmunicipo, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.ctmunicipios s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.ctmunicipios d
    WHERE d.llmunicipio = s.llmunicipio AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 6: PROMOTE ctcodigospostales
-- ============================================================================

\echo 'Paso 6: Promoviendo ctcodigospostales hacia public...'

MERGE INTO public.ctcodigospostales d
USING sepomex.ctcodigospostales s
ON d.llcodigopostal = s.llcodigopostal
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (llcodigopostal, cvcodigopostal, dscodigopostal, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llcodigopostal, s.cvcodigopostal, s.dscodigopostal, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.ctcodigospostales (
    llcodigopostal, cvcodigopostal, dscodigopostal, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llcodigopostal, s.cvcodigopostal, s.dscodigopostal, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.ctcodigospostales s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.ctcodigospostales d
    WHERE d.llcodigopostal = s.llcodigopostal AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PASO 7: PROMOTE ctasentamientos
-- ============================================================================

\echo 'Paso 7: Promoviendo ctasentamientos hacia public...'

MERGE INTO public.ctasentamientos d
USING sepomex.ctasentamientos s
ON d.llasentamiento = s.llasentamiento
WHEN MATCHED AND d.scd_vigente = TRUE AND d.scd_hash IS DISTINCT FROM s.scd_hash THEN
    UPDATE SET
        scd_vigente = FALSE,
        scd_fecha_fin = NOW(),
        fcmodificacion = NOW(),
        dsusuariomodifica = 'SEPOMEX_PROMOTE'
WHEN NOT MATCHED THEN
    INSERT (llasentamiento, llmunicipio, dsasentamiento, lltipoasentamiento,
            lltipozona, llcodigopostal, boactivo, scd_fecha_inicio,
            scd_vigente, scd_version, scd_hash, fcreacion, dsusuariocreacion)
    VALUES (s.llasentamiento, s.llmunicipio, s.dsasentamiento, s.lltipoasentamiento,
            s.lltipozona, s.llcodigopostal, s.boactivo, s.scd_fecha_inicio,
            s.scd_vigente, s.scd_version, s.scd_hash, NOW(), 'SEPOMEX_PROMOTE');

INSERT INTO public.ctasentamientos (
    llasentamiento, llmunicipio, dsasentamiento, lltipoasentamiento,
    lltipozona, llcodigopostal, boactivo,
    scd_fecha_inicio, scd_vigente, scd_version, scd_hash,
    fcreacion, dsusuariocreacion
)
SELECT
    s.llasentamiento, s.llmunicipio, s.dsasentamiento, s.lltipoasentamiento,
    s.lltipozona, s.llcodigopostal, s.boactivo,
    s.scd_fecha_inicio, s.scd_vigente, s.scd_version, s.scd_hash,
    NOW(), 'SEPOMEX_PROMOTE'
FROM sepomex.ctasentamientos s
WHERE s.scd_vigente = TRUE
AND NOT EXISTS (
    SELECT 1 FROM public.ctasentamientos d
    WHERE d.llasentamiento = s.llasentamiento AND d.scd_vigente = TRUE
)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICACIÓN POST-PROMOCIÓN
-- ============================================================================

\echo '✓ Promoción completada para todas las tablas'
\echo ''
\echo 'Resumen de registros vigentes en public.*:'

SELECT
    'ctpaises' AS tabla, COUNT(*) AS vigentes
FROM public.ctpaises WHERE scd_vigente = TRUE
UNION ALL
SELECT 'cttiposzona', COUNT(*) FROM public.cttiposzona WHERE scd_vigente = TRUE
UNION ALL
SELECT 'cttipoasentamiento', COUNT(*) FROM public.cttipoasentamiento WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctestados', COUNT(*) FROM public.ctestados WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctmunicipios', COUNT(*) FROM public.ctmunicipios WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctcodigospostales', COUNT(*) FROM public.ctcodigospostales WHERE scd_vigente = TRUE
UNION ALL
SELECT 'ctasentamientos', COUNT(*) FROM public.ctasentamientos WHERE scd_vigente = TRUE
ORDER BY tabla;

\echo ''
\echo 'Comparativa sepomex vs public (vigentes):'

WITH sepomex_counts AS (
    SELECT 'ctpaises' AS tabla, COUNT(*) AS cnt FROM sepomex.ctpaises WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctestados', COUNT(*) FROM sepomex.ctestados WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctmunicipios', COUNT(*) FROM sepomex.ctmunicipios WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctasentamientos', COUNT(*) FROM sepomex.ctasentamientos WHERE scd_vigente = TRUE
),
public_counts AS (
    SELECT 'ctpaises' AS tabla, COUNT(*) AS cnt FROM public.ctpaises WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctestados', COUNT(*) FROM public.ctestados WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctmunicipios', COUNT(*) FROM public.ctmunicipios WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctasentamientos', COUNT(*) FROM public.ctasentamientos WHERE scd_vigente = TRUE
)
SELECT
    s.tabla,
    s.cnt AS sepomex_vigentes,
    p.cnt AS public_vigentes,
    CASE WHEN s.cnt = p.cnt THEN '✓ OK' ELSE '✗ DIFERENCIA' END AS estado
FROM sepomex_counts s
JOIN public_counts p ON s.tabla = p.tabla
ORDER BY s.tabla;

\echo '✓ Script 05 completado exitosamente'

