# 🛠️ Documentación Técnica: Aura Axioma

## 1. Modelo de Datos SCD2 (Slowly Changing Dimensions Type 2)

Aura Axioma implementa SCD2 para garantizar que cualquier cambio en los catálogos maestros no destruya la integridad referencial de los registros históricos en otras aplicaciones.

### Columnas de Control
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `scd_start_date` | TIMESTAMPTZ | Fecha de inicio de vigencia de la versión. |
| `scd_end_date` | TIMESTAMPTZ | Fecha de fin de vigencia (Default: 9999-12-31). |
| `scd_is_current` | BOOLEAN | Indica si es la versión activa actual. |
| `scd_version` | INTEGER | Número correlativo de versión. |
| `scd_checksum` | TEXT | Hash MD5 de los datos del registro para detectar cambios. |

### Flujo de Integración (Merge Logic)
1. Los datos se cargan en el esquema `staging`.
2. Se calcula el `checksum` de la fila entrante.
3. Se compara contra el registro `is_current` en la tabla destino.
4. **Si hay cambios:** Se cierra la versión actual (`is_current = FALSE`) y se inserta una nueva.
5. **Si es nuevo:** Se inserta como Versión 1.

## 2. Automatización de Catálogos (Ingestión Dinámica)

### 2.1 CASFIM (Financiero)
La ingestión de entidades financieras se realiza automáticamente mediante el `CasfimProcessor`.
- **Fuente:** Portal oficial de SHCP (Catálogo del Sistema Financiero Mexicano).
- **Extracción:** Utiliza **Docling** para procesar PDFs complejos y convertirlos en datos relacionales.
- **Normalización:** Los nombres se limpian, las claves se normalizan a 3 dígitos y se mapea el estatus de operación.
- **Frecuencia:** Orquestado vía Celery para actualizaciones periódicas.

### 2.2 SAT (Fiscal)
Implementación completa del Anexo 20 para CFDI 4.0.
- **Catálogos:** Monedas, Regímenes Fiscales, Usos de CFDI, Formas de Pago, Métodos de Pago, Unidades de Medida.
- **Estructura:** Todos los catálogos residen en el esquema `fiscal` y utilizan el patrón SCD2.

## 3. API Endpoints (V1)

### Geografía (SEPOMEX/INEGI)
- `GET /geo/cp/{cp}`: Retorna asentamientos, municipio y estado asociados a un código postal.
- `GET /geo/estados`: Listado de estados con claves ISO.

### Fiscal (SAT)
- `GET /fiscal/sat/monedas`: Catálogo de monedas vigentes.
- `GET /fiscal/sat/regimenes`: Catálogo de regímenes fiscales.
- `GET /fiscal/sat/usos`: Catálogo de usos de CFDI.

### Financiero (CASFIM)
- `GET /financial/instituciones`: Listado de entidades financieras extraídas de SHCP.
- `GET /financial/tipos`: Tipos de entidades (Banca Múltiple, SOFIPO, etc.).

## 4. Integración con Clientes
Se recomienda que las aplicaciones cliente almacenen el **Natural Key** (ej. clave de banco 012) o el **ID (UUID)** y consulten a Axioma para obtener los metadatos vigentes. Axioma garantiza que la versión con `scd_is_current = TRUE` es la oficial en el momento de la consulta.
