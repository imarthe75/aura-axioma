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

## 2. API Endpoints

- `GET /geo/cp/{cp}`: Retorna datos geográficos vigentes.
- `GET /fiscal/sat/productos`: Lista claves SAT.
- `POST /ingestion/upload`: Endpoint para carga masiva de archivos.

## 3. Integración con Clientes
Se recomienda que las aplicaciones cliente almacenen el **UUID** o el **Natural Key** del catálogo, pero siempre consulten a Axioma para obtener la descripción vigente.
