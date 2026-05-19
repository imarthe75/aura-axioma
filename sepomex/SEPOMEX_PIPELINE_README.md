# SEPOMEX Pipeline - PostgreSQL 18 SCD2

## Descripción General

Este pipeline implementa un **proceso completo, determinista y reproducible** para cargar, validar e integrar el catálogo nacional de códigos postales mexicanos (**SEPOMEX**) en PostgreSQL 18.

Características principales:
- ✅ **SCD2 (Slowly Changing Dimension Type 2)**: Mantiene historial temporal completo de cambios
- ✅ **MERGE Nativo**: Utiliza `MERGE` de PostgreSQL 18 para upserts eficientes
- ✅ **Esquema de Staging**: Valida datos en `sepomex.*` antes de afectar `public.*`
- ✅ **Determinista**: Reglas de IDs hardcodeadas garantizan reproducibilidad
- ✅ **Sin TRUNCATE**: Preserva historial en producción mediante SCD2

---

## Estructura del Pipeline

```
01_create_sepomex_schema_and_tables.sql
    ↓ Crea esquemas y tablas vacías
02_add_scd2.sql
    ↓ Agrega columnas y componentes SCD2
03_stage_load.sql
    ↓ Carga CPdescarga.txt + transformaciones
04_merge_scd2.sql
    ↓ Aplica MERGE SCD2 al esquema sepomex
05_promote_to_public.sql
    ↓ Promueve datos validados a public (también SCD2)
tests_verificacion.sql
    ↓ Valida integridad y consistencia
```

---

## 1. FUENTE DE DATOS: CPdescarga.txt

### Origen Oficial
- **Proveedor**: Correos de México (SEPOMEX)
- **URL**: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx
- **Documentación**: 
  - https://github.com/eclipxe13/sepomexphp/blob/master/docs/DATABASE.md
  - https://deepwiki.com/aaron-dotnet/Mexico-Postal-Codes/8-data-reference

### Formato del Archivo

| **Columna**      | **SEPOMEX**      | **Descripción**              | **Tipo**      |
|------------------|------------------|------------------------------|---------------|
| 1                | d_codigo         | Código asignado              | VARCHAR(10)   |
| 2                | d_asenta         | Asentamiento                 | VARCHAR(100)  |
| 3                | d_tipo_asenta    | Tipo de asentamiento         | VARCHAR(50)   |
| 4                | d_mnpio          | Municipio                    | VARCHAR(100)  |
| 5                | d_estado         | Estado/Entidad               | VARCHAR(100)  |
| 6                | d_ciudad         | Ciudad                       | VARCHAR(100)  |
| 7                | d_cp             | Código Postal                | VARCHAR(10)   |
| 8                | c_estado         | Clave numérica estado        | NUMERIC(2,0)  |
| 9                | c_oficina        | Clave oficina                | NUMERIC(3,0)  |
| 10               | c_cp             | Clave numérica CP            | NUMERIC(5,0)  |
| 11               | c_tipo_asenta    | Clave tipo asentamiento      | NUMERIC(2,0)  |
| 12               | c_mnpio          | Clave municipio              | NUMERIC(3,0)  |
| 13               | id_asenta_cpcons | ID consulta SEPOMEX          | NUMERIC(6,0)  |
| 14               | d_zona           | Zona (U/R)                   | VARCHAR(20)   |
| 15               | c_cve_ciudad     | Clave ciudad                 | NUMERIC(4,0)  |

### Estructura del Archivo
```
[Línea 1] Nota legal de derechos de autor (ignorar)
[Línea 2] Encabezados: d_codigo|d_asenta|d_tipo_asenta|...
[Línea 3+] Datos reales (28107 registros aprox.)
```

**Propiedades**:
- Delimitador: `|` (pipe)
- Codificación: LATIN1 (ISO-8859-1)
- Sin BOM
- Line endings: LF

---

## 2. ESTRUCTURA DE DATOS: MATRICES DE RELACIÓN

```
┌─────────────────────────────────────────┐
│         JERARQUÍA DE CATÁLOGOS          │
└─────────────────────────────────────────┘

        ctpaises (1)
             ↓
        ctestados (32)
             ↓
        ctmunicipios (2,455)
         ↙  ↓  ↘
        ↙   ↓   ↘
   ctlocalidades  ctasentamientos ← ctcodigospostales
                 ↓
         ctciudades
```

### Catálogos

#### **ctpaises** (Países)
- **PK**: `llpais` = 484 (México, ISO 3166-1)
- **Clave Natural**: `cvisoalpha3` (MEX)
- **Atributos**: país ISO, descripción

#### **ctestados** (Estados)
- **PK**: `llestado` = 48400 + c_estado
- **Clave Natural**: (llpais, cvestado)
- **FK**: → ctpaises(llpais)
- **Datos**: 32 entidades federativas

#### **ctmunicipios** (Municipios)
- **PK**: `llmunicipio` = llestado * 1000 + c_mnpio
- **Clave Natural**: (llestado, cvmunicipio)
- **FK**: → ctestados(llestado)
- **Datos**: 2,455 municipios

#### **ctcodigospostales** (Códigos Postales)
- **PK**: `llcodigopostal` = CAST(d_cp AS BIGINT)
- **Clave Natural**: `cvcodigopostal` (el código tal cual)
- **Datos**: 28,107 códigos únicos

#### **ctasentamientos** (Asentamientos)
- **PK**: `llasentamiento` (generado con ROW_NUMBER)
- **Clave Natural**: (llmunicipio, dsasentamiento, lltipoasentamiento, lltipozona, llcodigopostal)
- **FKs**: → ctmunicipios, cttipoasentamiento, cttipozona, ctcodigospostales
- **Datos**: 28,107 registros

#### **cttipoasentamiento** (Tipos de Asentamiento)
- **PK**: `lltipoasentamiento` = c_tipo_asenta
- **Clave Natural**: `dstipoasentamiento`
- **Ejemplos**: Colonia, Fraccionamiento, Pueblo, Barrio, etc.

#### **cttiposzona** (Tipos de Zona)
- **PK**: `lltipozona`
- **Datos Fijos**:
  - 1 = Urbano (d_zona = 'U')
  - 2 = Rural  (d_zona = 'R')

#### **ctlocalidades** (Localidades)
- **PK**: `lllocalidad` (secuencial)
- **Clave Natural**: (llmunicipio, COALESCE(cvlocalidad, dslocalidad))
- **FK**: → ctmunicipios

#### **ctciudades** (Ciudades)
- **PK**: `llciudad` (secuencial)
- **Clave Natural**: (llasentamiento, dsciudad)
- **FK**: → ctasentamientos

---

## 3. SCD2: SLOWLY CHANGING DIMENSION TYPE 2

### Conceptos

**SCD2** mantiene un historial completo de cambios con validez temporal:

```sql
-- Registro Vigente
id=1, nombre="Ciudad de México", scd_vigente=TRUE,  scd_fecha_inicio='2026-01-01', scd_fecha_fin=NULL,          scd_version=1

-- Cambio detectado → se cierra versión anterior
id=1, nombre="Ciudad de México", scd_vigente=FALSE, scd_fecha_inicio='2026-01-01', scd_fecha_fin='2026-03-01', scd_version=1

-- Se inserta nueva versión
id=1, nombre="Nuevo Nombre",     scd_vigente=TRUE,  scd_fecha_inicio='2026-03-01', scd_fecha_fin=NULL,          scd_version=2
```

### Columnas SCD2

| **Columna**       | **Tipo**      | **Descripción**                              |
|-------------------|---------------|----------------------------------------------|
| `scd_fecha_inicio`| TIMESTAMPTZ   | Cuándo entra en vigencia                     |
| `scd_fecha_fin`   | TIMESTAMPTZ   | Cuándo termina (NULL = vigente actualmente)  |
| `scd_vigente`     | BOOLEAN       | TRUE si es la versión actual                 |
| `scd_version`     | INTEGER       | Número secuencial de versión                 |
| `scd_hash`        | TEXT (MD5)    | Hash de atributos clave (detección cambios)  |

### Índices SCD2

Para cada tabla se crean:

```sql
-- Índice único parcial en clave natural (solo vigentes)
CREATE UNIQUE INDEX idx_tabla_scd2_vigente
    ON tabla(clave_natural_columns)
    WHERE scd_vigente = TRUE;

-- Índice para búsquedas por vigencia
CREATE INDEX idx_tabla_scd_vigente
    ON tabla(scd_vigente);
```

### CHECK Constraint

```sql
ALTER TABLE tabla
ADD CONSTRAINT ck_tabla_scd_temporality
    CHECK (scd_fecha_fin IS NULL OR scd_fecha_fin > scd_fecha_inicio);
```

---

## 4. ARQUITECTURA: ESQUEMAS MULTI-NIVEL

```
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL Database                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  public                    sepomex              sepomex_stage
│  ───────                   ───────              ──────────────
│  ctpaises      ←────────── ctpaises             (vacío tras ejecución)
│  ctestados                 ctestados
│  ctmunicipios              ctmunicipios
│  ctasentamientos           ctasentamientos
│  ...                       ...
│                            (SCD2 vigentes)      sepomex_raw
│                                                 (datos crudos)
│
│  [PRODUCCIÓN]             [VALIDACIÓN]         [STAGING]
│                                                
└─────────────────────────────────────────────────────────┘
```

### Flujo de Datos

```
CPdescarga.txt (archivo SEPOMEX)
        ↓ (03_stage_load.sql)
sepomex_stage.sepomex_raw
        ↓ (transformaciones en 03)
sepomex_stage.ctpaises, ctestados, ..., ctasentamientos
        ↓ (04_merge_scd2.sql)
sepomex.ctpaises, ctestados, ..., ctasentamientos (versión validada)
        ↓ (05_promote_to_public.sql)
public.ctpaises, ctestados, ..., ctasentamientos (producción con historial)
```

---

## 5. EJECUCIÓN DEL PIPELINE

### Precondiciones

1. **PostgreSQL 18+** instalado y funcionando
2. **Archivo CPdescarga.txt** descargado en ruta accesible al servidor
3. **Permisos**: superuser o rol con CREATE SCHEMA, CREATE TABLE
4. **Espacio**: ~500 MB disponible (datos x 2 esquemas)

### Paso 1: Preparar Archivo

```bash
# En Docker (recomendado para aislar)
mkdir -p /var/lib/postgresql/sepomex
cp ~/Download/CPdescarga.txt /var/lib/postgresql/sepomex/

# En Local (Windows/MacOS)
# Guardar en ruta accesible (ej: C:\sepomex\CPdescarga.txt)
# Y actualizar ruta en 03_stage_load.sql línea ~50
```

### Paso 2: Ejecutar Scripts

```bash
# Terminal 1: Conectar a PostgreSQL
psql -U postgres -d mi_base_datos

# Terminal 2: Ejecutar scripts en orden

# Script 01: Crear esquemas y tablas
\i '01_create_sepomex_schema_and_tables.sql'

# Script 02: Agregar SCD2
\i '02_add_scd2.sql'

# Script 03: Cargar datos
\i '03_stage_load.sql'

# Script 04: MERGE SCD2 (sepomex)
\i '04_merge_scd2.sql'

# Script 05: PROMOTE to public (CUIDADO: Afecta tablas de producción)
\i '05_promote_to_public.sql'

# Script 06: Ejecutar tests
\i 'tests_verificacion.sql'
```

### Paso 3: Verificación Post-Carga

```sql
-- Ver resumen de registros cargados
SELECT 'ctpaises' AS tabla, COUNT(*) AS total, 
       SUM(CASE WHEN scd_vigente THEN 1 ELSE 0 END) AS vigentes
FROM sepomex.ctpaises
UNION ALL
SELECT 'ctestados', COUNT(*),
       SUM(CASE WHEN scd_vigente THEN 1 ELSE 0 END)
FROM sepomex.ctestados
-- ... repetir para otras tablas
ORDER BY tabla;

-- Ver historial de cambios (SCD2)
SELECT * FROM sepomex.ctestados
WHERE cvestado = '09'  -- CDMX
ORDER BY scd_fecha_inicio DESC;

-- Ver datos vigentes
SELECT * FROM sepomex.ctpaises WHERE scd_vigente = TRUE;
```

---

## 6. INTERPRETACIÓN DE LOGS Y RESULTADOS

### Durante Ejecución (psql)

```
✓ Esquemas creados: sepomex, sepomex_stage
✓ Tablas catálogo creadas en sepomex.*
✓ Carga RAW completada
✓ Transformación completada
✓ MERGE completado para todas las tablas
```

### Resultado de Tests

```sql
-- Éxito: Sin duplicados vigentes
(0 registros retornados)

-- Éxito: FK válidas
relacion                                      | huerfanos
──────────────────────────────────────────────┼──────────
ctmunicipios → ctestados                      |         0
ctasentamientos → ctmunicipios                |         0
ctasentamientos → ctcodigospostales           |         0

-- Resumen
Catálogo                    Vigentes | Histórico
─────────────────────────────────────┼──────────
ctpaises                            1 |         0
ctestados                          32 |         0
ctmunicipios                     2455 |         0
ctasentamientos              28107 |         0
```

---

## 7. COMPARACIÓN: sepomex.* vs public.*

Para verificar que la promoción fue exitosa:

```sql
-- Comparar registro por registro
SELECT 
    s.tabla,
    s.vigentes AS sepomex_vigentes,
    p.vigentes AS public_vigentes,
    CASE WHEN s.vigentes = p.vigentes THEN '✓' ELSE '✗ DIFF' END AS estado
FROM (
    SELECT 'ctpaises' AS tabla, COUNT(*) AS vigentes 
    FROM sepomex.ctpaises WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctestados', COUNT(*) FROM sepomex.ctestados WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctmunicipios', COUNT(*) FROM sepomex.ctmunicipios WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctasentamientos', COUNT(*) FROM sepomex.ctasentamientos WHERE scd_vigente = TRUE
) s
JOIN (
    SELECT 'ctpaises' AS tabla, COUNT(*) AS vigentes FROM public.ctpaises WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctestados', COUNT(*) FROM public.ctestados WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctmunicipios', COUNT(*) FROM public.ctmunicipios WHERE scd_vigente = TRUE
    UNION ALL
    SELECT 'ctasentamientos', COUNT(*) FROM public.ctasentamientos WHERE scd_vigente = TRUE
) p ON s.tabla = p.tabla
ORDER BY s.tabla;

-- ✓ Resultado esperado: Todas las filas muestran estado '✓'
```

---

## 8. OPERACIONES COMUNES POST-CARGA

### Buscar referencias de un código postal

```sql
SELECT 
    a.dsasentamiento AS asentamiento,
    m.dsmunicipo AS municipio,
    e.dsestado AS estado,
    cp.cvcodigopostal AS codigo_postal,
    tz.dstipozona AS zona
FROM sepomex.ctasentamientos a
JOIN sepomex.ctmunicipios m ON a.llmunicipio = m.llmunicipio
JOIN sepomex.ctestados e ON m.llestado = e.llestado
JOIN sepomex.ctcodigospostales cp ON a.llcodigopostal = cp.llcodigopostal
JOIN sepomex.cttiposzona tz ON a.lltipozona = tz.lltipozona
WHERE a.scd_vigente = TRUE
  AND cp.cvcodigopostal = '28001'  -- CDMX
ORDER BY a.dsasentamiento;
```

### Ver historial de cambios (SCD2)

```sql
-- Historial de un estado
SELECT 
    cvestado,
    dsestado,
    scd_version,
    scd_vigente,
    scd_fecha_inicio,
    scd_fecha_fin
FROM sepomex.ctestados
WHERE llestado = 48409  -- CDMX
ORDER BY scd_fecha_inicio DESC;
```

### Detectar cambios entre cargas

```sql
-- Nuevos asentamientos en última carga
SELECT * FROM sepomex.ctasentamientos
WHERE scd_version = 1 AND scd_vigente = TRUE
AND scd_fecha_inicio > NOW() - INTERVAL '1 hour';

-- Asentamientos que cambiaron nombre
SELECT * FROM sepomex.ctasentamientos
WHERE scd_vigente = FALSE AND scd_fecha_fin > NOW() - INTERVAL '1 hour';
```

### Limpiar (si es necesario)

```sql
-- CUIDADO: Esto borra TODO el esquema sepomex
DROP SCHEMA sepomex CASCADE;
DROP SCHEMA sepomex_stage CASCADE;

-- Reconstruir desde scripts 01-05
```

---

## 9. ADVERTENCIAS Y CONSIDERACIONES

### ⚠️ COPY FROM PROGRAM

El script 03 usa:
```sql
COPY sepomex_stage.sepomex_raw
FROM PROGRAM 'tail -n +3 /var/lib/postgresql/sepomex/CPdescarga.txt'
```

**Consideraciones**:
- Requiere que `pgsql_program_create_trigger_functions` esté habilitado
- El usuario PostgreSQL debe tener permisos de lectura en la ruta
- En Docker, usar volúmenes normales: `COPY FROM 'C:\ruta\archivo'` (en Windows)
- En Linux/Mac, usar ruta Unix: `/var/lib/postgresql/sepomex/CPdescarga.txt`

### ⚠️ LATIN1 Encoding

El archivo original está en **LATIN1 (ISO-8859-1)**, no UTF-8.
- Si la BD es UTF-8 (recomendado), la conversión es automática
- Si hay caracteres especiales que se rompen, verificar:
  ```sql
  SHOW client_encoding;
  SET client_encoding = 'UTF8';
  ```

### ⚠️ Promoción a public

El script 05 afecta las tablas en `public.*`:
- ✅ NO hace `TRUNCATE` (preserva historial)
- ✅ Solo inserta/actualiza cambios
- Pero ⚠️ Asegúrate de que `public.*` tiene estructura SCD2 idéntica

### ⚠️ FKs y Constraints

- Los scripts asumen que `public.*` ya existe con SCD2
- Si `public.*` **NO** tiene SCD2, el script 05 fallará
- Ejecutar primero los scripts 01-02 en `public.*` si es necesario

---

## 10. FUENTES Y REFERENCIAS OFICIALES

### SEPOMEX Files
- Archivo de muestra CPdescarga.txt
  - [OneDrive - CPdescarga_muestra.txt](https://casystems-my.sharepoint.com/personal/israelm_casmarts_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/CPdescarga_muestra.txt)
- Portal oficial Correos de México
  - https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/Descarga.aspx
  - https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx

### Documentación SEPOMEX
- GitHub: SEPOMEX PHP
  - https://github.com/eclipxe13/sepomexphp/blob/master/docs/DATABASE.md
- Deep Wiki
  - https://deepwiki.com/aaron-dotnet/Mexico-Postal-Codes/8-data-reference

### PostgreSQL 18
- MERGE Statement
  - https://www.postgresql.org/docs/current/sql-merge.html
- Release Notes
  - https://www.postgresql.org/docs/current/release-18.html
- SCD2 Patterns
  - https://www.postgresql.org/docs/current/functions-datetime.html

---

## 11. TROUBLESHOOTING

### Error: "FK constraint 'fk_...' violated"

**Causa**: Clave foránea no existe en tabla padre.

**Solución**:
1. Verificar que los scripts se ejecutaron en orden (01→02→03→04)
2. Ejecutar `tests_verificacion.sql` para diagnosticar
3. Revisar script 03 para cambios en reglas de IDs

### Error: "Permission denied" en COPY FROM PROGRAM

**Causa**: Permisos insuficientes o ruta inválida.

**Solución**:
```bash
# En Docker
docker exec -u postgres postgres_container \
    cp CPdescarga.txt /var/lib/postgresql/sepomex/
chmod 644 /var/lib/postgresql/sepomex/CPdescarga.txt

# En Local (Windows PowerShell)
$env:PGHOST = 'localhost'
$env:PGUSER = 'postgres'
psql -c "COPY sepomex_stage.sepomex_raw ..."
```

### Error: "Encoding conversion failed"

**Causa**: Inconsistencia LATIN1 ↔ UTF-8

**Solución**:
```sql
-- Verificar encoding actual
SHOW server_encoding;

-- Convertir archivo si es necesario
-- Linux/Mac:
iconv -f LATIN1 -t UTF-8 CPdescarga.txt > CPdescarga_utf8.txt

-- Windows PowerShell:
[System.IO.File]::WriteAllText(
    "CPdescarga_utf8.txt",
    [System.IO.File]::ReadAllText("CPdescarga.txt", [System.Text.Encoding]::GetEncoding("iso-8859-1")),
    [System.Text.Encoding]::UTF8
)
```

### Error: "Hash mismatch" en SCD2

**Causa**: Los hashes no coinciden entre staging y sepomex.

**Solución**:
1. Ejecutar stage_load nuevamente (limpia y recarga)
2. Verificar que no hay modificaciones manuales de datos
3. Recalcular hashes: `UPDATE sepomex.tabla SET scd_hash = MD5(...)`

---

## 12. MANTENIMIENTO Y ACTUALIZACIONES

### Ejecutar Nuevamente Mensualmente

```bash
# Descargar nuevo CPdescarga.txt desde Correos de México

# Ejecutar solo scripts 03-05 (preserva datos vigentes en public)
psql -d mi_base -f 03_stage_load.sql
psql -d mi_base -f 04_merge_scd2.sql
psql -d mi_base -f 05_promote_to_public.sql

# Verificar
psql -d mi_base -f tests_verificacion.sql
```

### Estadísticas de Cambios

```sql
-- Cuántas entradas fueron nuevas, modificadas, sin cambios
WITH cambios AS (
    SELECT 
        COUNT(*) FILTER (WHERE scd_version = 1) AS nuevas,
        COUNT(*) FILTER (WHERE scd_version > 1) AS modificadas,
        MAX(scd_fecha_inicio) AS ultima_actualizacion
    FROM sepomex.ctasentamientos
    WHERE scd_vigente = TRUE
)
SELECT * FROM cambios;
```

---

## 13. CÁLCULO DE TAMAÑO DE DATOS

**Estimado** (post-carga completa):

| Tabla           | Registros | Tamaño (SCD2) | Histórico |
|-----------------|-----------|---------------|-----------|
| ctpaises        | 1         | ~8 KB         | Mínimo    |
| ctestados       | 32        | ~256 KB       | Mínimo    |
| ctmunicipios    | 2,455     | ~20 MB        | Mínimo    |
| ctasentamientos | 28,107    | ~280 MB       | Variable  |
| **TOTAL**       | **30,595**| **~300 MB**   | **+20%**  |

**Requerimiento Total**: ~400 MB en DOS esquemas (700 MB bruto)

---

## 14. CONTACTO Y SOPORTE

Para reportar problemas o sugerencias:

1. Verificar que se siguieron los pasos en orden
2. Ejecutar `tests_verificacion.sql` para diagnosticar
3. Revisar logs de PostgreSQL: `pg_log/postgresql.log`
4. Consultar fuentes oficiales (ver sección 10)

---

**Última Actualización**: 2026-03-23  
**Versión**: 1.0  
**PostgreSQL**: 18.x  
**Estado**: ✅ Producción

