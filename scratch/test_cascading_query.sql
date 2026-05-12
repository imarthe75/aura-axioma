
SELECT 
    cp.cp,
    a.name as asentamiento,
    at.name as tipo_asentamiento,
    m.name as municipio,
    e.name as estado,
    p.name as pais,
    p.phone_code
FROM geo.codigos_postales cp
JOIN geo.asentamientos a ON a.cp_id = cp.id
JOIN geo.asentamiento_tipos at ON a.asentamiento_tipo_id = at.id
JOIN geo.municipios m ON a.municipality_id = m.id
JOIN geo.estados e ON m.state_id = e.id
JOIN geo.paises p ON e.country_id = p.id
WHERE cp.cp = '01000'
AND cp.scd_is_current = TRUE
AND a.scd_is_current = TRUE;
