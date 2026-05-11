# 📘 Guía de Usuario: Aura Axioma

## 1. Consulta de Datos
Acceda al **Explorador** en la interfaz web. Puede buscar por cualquier campo clave (Código Postal, Clave SAT, etc.). Por defecto, el sistema solo mostrará registros vigentes.

## 2. Actualización de Catálogos (Admin)

### Pasos para Carga Masiva:
1. Diríjase a la pestaña **Administración**.
2. Prepare su archivo CSV o Excel. Asegúrese de que las columnas coincidan con el esquema esperado (consulte los *templates* en `/api/templates`).
3. Arrastre el archivo al área de carga.
4. El sistema procesará el archivo y aplicará la lógica SCD2 automáticamente.
5. Verifique el resultado en la tabla de **Historial de Ingestas**.

### Sincronización Automática
Aura Axioma cuenta con "Job Runners" que se pueden disparar desde la API para:
- Actualizar festivos nacionales (`GET /admin/sync/holidays`).
- Sincronizar tipos de cambio.

## 3. Mejores Prácticas
- No modifique los datos directamente en la base de datos; use siempre el flujo de ingesta para mantener la trazabilidad.
- Revise periódicamente el log de errores en la consola de administración si una ingesta falla.
