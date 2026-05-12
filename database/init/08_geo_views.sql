CREATE OR REPLACE VIEW geo.vw_geografia_mexico AS
SELECT 
    cp.cp as codigo_postal,
    a.name as asentamiento,
    at.name as tipo_asentamiento,
    z.name as zona,
    m.name as municipio,
    e.name as estado,
    p.name as pais,
    p.phone_code as codigo_telefonico
FROM geo.asentamientos a
JOIN geo.codigos_postales cp ON a.cp_id = cp.id
JOIN geo.asentamiento_tipos at ON a.asentamiento_tipo_id = at.id
JOIN geo.zona_tipos z ON a.zona_tipo_id = z.id
JOIN geo.municipios m ON a.municipality_id = m.id
JOIN geo.estados e ON m.state_id = e.id
JOIN geo.paises p ON e.country_id = p.id
WHERE a.scd_is_current = TRUE
  AND cp.scd_is_current = TRUE
  AND m.scd_is_current = TRUE
  AND e.scd_is_current = TRUE
  AND p.scd_is_current = TRUE;
