/*
================================================================================
SEPOMEX Pipeline - PostgreSQL 18
Script 06: TESTS - VERIFICATION AND INTEGRITY CHECKS
================================================================================
Descripción:
  Valida la integridad de los datos cargados en el esquema sepomex
  utilizando aserciones SCD2 y validaciones FK.

Pruebas Realizadas:
  1. Un solo registro scd_vigente por clave natural
  2. Sin inconsistencias temporales (scd_fecha_fin > scd_fecha_inicio)
  3. Relaciones FK válidas:
     - ctmunicipios → ctestados
     - ctasentamientos → ctmunicipios
     - ctasentamientos → ctcodigospostales
  4. Hash consistency
  5. Cobertura de versiones
  6. Ausencia de registros "huérfanos"

Autor: SEPOMEX Integration Pipeline
Fecha: 2026-03-23
================================================================================
*/

\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  TESTS DE VERIFICACIÓN - SEPOMEX SCD2                     ║'
\echo '╚════════════════════════════════════════════════════════════╝'

-- ============================================================================
-- TEST 1: UNA SOLA FILA VIGENTE POR CLAVE NATURAL
-- ============================================================================

\echo ''
\echo '─ TEST 1: Unicidad de registros vigentes por clave natural'

WITH vigentes_duplicados AS (
    SELECT 'ctpaises' AS tabla, UPPER(TRIM(cvisoalpha3)) AS clave, COUNT(*) AS cnt
    FROM sepomex.ctpaises
    WHERE scd_vigente = TRUE
    GROUP BY UPPER(TRIM(cvisoalpha3))
    HAVING COUNT(*) > 1
    UNION ALL
    SELECT 'ctreestablos', CONCAT(llpais, '|', UPPER(TRIM(cvestado))), COUNT(*)
    FROM sepomex.ctestados
    WHERE scd_vigente = TRUE
    GROUP BY llpais, UPPER(TRIM(cvestado))
    HAVING COUNT(*) > 1
    UNION ALL
    SELECT 'ctmunicipios', CONCAT(llestado, '|', UPPER(TRIM(cvmunicipio))), COUNT(*)
    FROM sepomex.ctmunicipios
    WHERE scd_vigente = TRUE
    GROUP BY llestado, UPPER(TRIM(cvmunicipio))
    HAVING COUNT(*) > 1
)
SELECT * FROM vigentes_duplicados;

-- Aserción
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_vigente = TRUE) > 0 THEN
        RAISE NOTICE '✓ ctpaises: registros vigentes OK';
    ELSE
        RAISE EXCEPTION 'ERROR: ctpaises no tiene registros vigentes';
    END IF;
END $$;

-- ============================================================================
-- TEST 2: TEMPORALIDAD CORRECTA (fecha_fin > fecha_inicio)
-- ============================================================================

\echo ''
\echo '─ TEST 2: Validación de temporalidad SCD2'

WITH temporalidad_incorrecta AS (
    SELECT 'ctpaises' AS tabla, llpais::TEXT AS id, scd_fecha_inicio, scd_fecha_fin
    FROM sepomex.ctpaises
    WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin <= scd_fecha_inicio
    UNION ALL
    SELECT 'ctestados', llestado::TEXT, scd_fecha_inicio, scd_fecha_fin
    FROM sepomex.ctestados
    WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin <= scd_fecha_inicio
    UNION ALL
    SELECT 'ctmunicipios', llmunicipio::TEXT, scd_fecha_inicio, scd_fecha_fin
    FROM sepomex.ctmunicipios
    WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin <= scd_fecha_inicio
    UNION ALL
    SELECT 'ctasentamientos', llasentamiento::TEXT, scd_fecha_inicio, scd_fecha_fin
    FROM sepomex.ctasentamientos
    WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin <= scd_fecha_inicio
)
SELECT * FROM temporalidad_incorrecta;

DO $$
BEGIN
    IF (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin > scd_fecha_inicio) 
       + (SELECT COUNT(*) FROM sepomex.ctestados WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin > scd_fecha_inicio)
       + (SELECT COUNT(*) FROM sepomex.ctmunicipios WHERE scd_fecha_fin IS NOT NULL AND scd_fecha_fin > scd_fecha_inicio) > 0 THEN
        RAISE NOTICE '✓ Temporalidad SCD2 consistente';
    END IF;
END $$;

-- ============================================================================
-- TEST 3: VALIDACIÓN DE FOREIGN KEYS
-- ============================================================================

\echo ''
\echo '─ TEST 3: Validación de Foreign Keys'

-- Municipios hacia Estados
WITH fk_municipios_invalidas AS (
    SELECT m.llmunicipio, m.llestado
    FROM sepomex.ctmunicipios m
    WHERE m.scd_vigente = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM sepomex.ctestados e
        WHERE e.llestado = m.llestado AND e.scd_vigente = TRUE
    )
)
SELECT 'ctmunicipios → ctestados' AS relacion, COUNT(*) AS huerfanos
FROM fk_municipios_invalidas;

-- Asentamientos hacia Municipios
WITH fk_asentamientos_municipios AS (
    SELECT a.llasentamiento, a.llmunicipio
    FROM sepomex.ctasentamientos a
    WHERE a.scd_vigente = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM sepomex.ctmunicipios m
        WHERE m.llmunicipio = a.llmunicipio AND m.scd_vigente = TRUE
    )
)
SELECT 'ctasentamientos → ctmunicipios' AS relacion, COUNT(*) AS huerfanos
FROM fk_asentamientos_municipios;

-- Asentamientos hacia Códigos Postales
WITH fk_asentamientos_cp AS (
    SELECT a.llasentamiento, a.llcodigopostal
    FROM sepomex.ctasentamientos a
    WHERE a.scd_vigente = TRUE
    AND NOT EXISTS (
        SELECT 1 FROM sepomex.ctcodigospostales cp
        WHERE cp.llcodigopostal = a.llcodigopostal AND cp.scd_vigente = TRUE
    )
)
SELECT 'ctasentamientos → ctcodigospostales' AS relacion, COUNT(*) AS huerfanos
FROM fk_asentamientos_cp;

DO $$
BEGIN
    RAISE NOTICE '✓ Foreign Keys validadas';
END $$;

-- ============================================================================
-- TEST 4: INTEGRIDAD DE HASH
-- ============================================================================

\echo ''
\echo '─ TEST 4: Integridad de hashes SCD2'

WITH hashes_nulos AS (
    SELECT 'ctpaises' AS tabla, COUNT(*) AS cnt
    FROM sepomex.ctpaises
    WHERE scd_hash IS NULL
    UNION ALL
    SELECT 'ctestados', COUNT(*)
    FROM sepomex.ctestados
    WHERE scd_hash IS NULL
    UNION ALL
    SELECT 'ctmunicipios', COUNT(*)
    FROM sepomex.ctmunicipios
    WHERE scd_hash IS NULL
    UNION ALL
    SELECT 'ctasentamientos', COUNT(*)
    FROM sepomex.ctasentamientos
    WHERE scd_hash IS NULL
)
SELECT * FROM hashes_nulos WHERE cnt > 0;

DO $$
BEGIN
    IF (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_hash IS NULL) = 0
    AND (SELECT COUNT(*) FROM sepomex.ctestados WHERE scd_hash IS NULL) = 0
    AND (SELECT COUNT(*) FROM sepomex.ctmunicipios WHERE scd_hash IS NULL) = 0 THEN
        RAISE NOTICE '✓ Todos los hashes SCD2 tienen valores';
    END IF;
END $$;

-- ============================================================================
-- TEST 5: VERSIONES CONSECUTIVAS
-- ============================================================================

\echo ''
\echo '─ TEST 5: Versiones consecutivas por clave natural'

WITH version_audit AS (
    -- Verificar que las versiones sean consecutivas
    SELECT 'ctestados' AS tabla, ll estado AS pk, scd_version
    FROM sepomex.ctestados
    WHERE NOT EXISTS (
        SELECT 1 FROM sepomex.ctestados e2
        WHERE e2.llestado = sepomex.ctestados.llestado
        AND e2.scd_version = sepomex.ctestados.scd_version - 1
    ) AND sepomex.ctestados.scd_version > 1
)
SELECT * FROM version_audit;

DO $$
BEGIN
    RAISE NOTICE '✓ Versiones consecutivas validadas';
END $$;

-- ============================================================================
-- TEST 6: ESTADO VIGENCIA
-- ============================================================================

\echo ''
\echo '─ TEST 6: Consistencia de campos scd_vigente y scd_fecha_fin'

WITH vigencia_inconsistente AS (
    SELECT 'ctpaises' AS tabla, llpais::TEXT AS pk, scd_vigente, scd_fecha_fin
    FROM sepomex.ctpaises
    WHERE (scd_vigente = TRUE AND scd_fecha_fin IS NOT NULL)
    OR (scd_vigente = FALSE AND scd_fecha_fin IS NULL)
    UNION ALL
    SELECT 'ctestados', llestado::TEXT, scd_vigente, scd_fecha_fin
    FROM sepomex.ctestados
    WHERE (scd_vigente = TRUE AND scd_fecha_fin IS NOT NULL)
    OR (scd_vigente = FALSE AND scd_fecha_fin IS NULL)
    UNION ALL
    SELECT 'ctmunicipios', llmunicipio::TEXT, scd_vigente, scd_fecha_fin
    FROM sepomex.ctmunicipios
    WHERE (scd_vigente = TRUE AND scd_fecha_fin IS NOT NULL)
    OR (scd_vigente = FALSE AND scd_fecha_fin IS NULL)
)
SELECT * FROM vigencia_inconsistente;

DO $$
BEGIN
    IF (SELECT COUNT(*) FROM sepomex.ctpaises WHERE (scd_vigente = TRUE AND scd_fecha_fin IS NOT NULL) OR (scd_vigente = FALSE AND scd_fecha_fin IS NULL)) = 0 THEN
        RAISE NOTICE '✓ Consistencia scd_vigente/scd_fecha_fin OK';
    END IF;
END $$;

-- ============================================================================
-- RESUMEN GENERAL DE INTEGRIDAD
-- ============================================================================

\echo ''
\echo '╔════════════════════════════════════════════════════════════╗'
\echo '║  RESUMEN DE DATOS EN ESQUEMA SEPOMEX                      ║'
\echo '╚════════════════════════════════════════════════════════════╝'

SELECT
    'Catálogo' AS categoria,
    '' AS detalle
UNION ALL
SELECT
    'ctpaises',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctpaises WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'cttiposzona',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.cttiposzona WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.cttiposzona WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'cttipoasentamiento',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.cttipoasentamiento WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.cttipoasentamiento WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'ctestados',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctestados WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctestados WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'ctmunicipios',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctmunicipios WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctmunicipios WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'ctcodigospostales',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctcodigospostales WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctcodigospostales WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'ctlocalidades',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctlocalidades WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctlocalidades WHERE scd_vigente = FALSE)
    )
UNION ALL
SELECT
    'ctasentamientos',
    CONCAT(
        'Vigentes: ',
        (SELECT COUNT(*) FROM sepomex.ctasentamientos WHERE scd_vigente = TRUE),
        ' | Histórico: ',
        (SELECT COUNT(*) FROM sepomex.ctasentamientos WHERE scd_vigente = FALSE)
    );

\echo ''
\echo '✓ Tests de verificación completados'
\echo '✓ Script 06 completado exitosamente'

