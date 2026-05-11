-- Aura Axioma - Geo Tables (SEPOMEX & INEGI)

-- 1. Paises
CREATE TABLE IF NOT EXISTS geo.paises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iso_alpha3 CHAR(3) NOT NULL, -- Natural Key
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2 Columns
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 2. Estados (México)
CREATE TABLE IF NOT EXISTS geo.estados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID REFERENCES geo.paises(id),
    state_code VARCHAR(5) NOT NULL, -- Natural Key (e.g. 01, 09)
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 3. Municipios
CREATE TABLE IF NOT EXISTS geo.municipios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_id UUID REFERENCES geo.estados(id),
    municipality_code VARCHAR(5) NOT NULL, -- Natural Key (within state)
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 4. Codigos Postales
CREATE TABLE IF NOT EXISTS geo.codigos_postales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cp CHAR(5) NOT NULL, -- Natural Key
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 5. Asentamientos (Colonias)
CREATE TABLE IF NOT EXISTS geo.asentamientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID REFERENCES geo.municipios(id),
    cp_id UUID REFERENCES geo.codigos_postales(id),
    name TEXT NOT NULL,
    settlement_type TEXT, -- (Colonia, Barrio, Fraccionamiento, etc)
    zone_type TEXT,       -- (Urbano, Rural)
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Partial unique indices for SCD2 (only one current version per natural key)
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_paises_current ON geo.paises(iso_alpha3) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_estados_current ON geo.estados(country_id, state_code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_municipios_current ON geo.municipios(state_id, municipality_code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_cp_current ON geo.codigos_postales(cp) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_geo_asentamientos_current ON geo.asentamientos(municipality_id, cp_id, name) WHERE scd_is_current = TRUE;
