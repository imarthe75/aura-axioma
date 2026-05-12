-- Aura Axioma - Geo Tables (Normalized Hierarchy)
-- Based on SEPOMEX & INEGI Standards

-- 1. Paises
CREATE TABLE IF NOT EXISTS geo.paises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    iso_alpha3 CHAR(3) NOT NULL UNIQUE,
    iso_alpha2 CHAR(2),
    numeric_code CHAR(3),
    name TEXT NOT NULL,
    name_en TEXT,
    name_fr TEXT,
    name_native TEXT,
    phone_code VARCHAR(10),
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2 & Audit
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Estados
CREATE TABLE IF NOT EXISTS geo.estados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID REFERENCES geo.paises(id),
    state_code VARCHAR(10) NOT NULL,
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(country_id, state_code, scd_is_current)
);

-- 3. Municipios
CREATE TABLE IF NOT EXISTS geo.municipios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_id UUID REFERENCES geo.estados(id),
    municipality_code VARCHAR(10) NOT NULL,
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(state_id, municipality_code, scd_is_current)
);

-- 4. Tipos (Catálogos Menores)
CREATE TABLE IF NOT EXISTS geo.asentamiento_tipos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS geo.zona_tipos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Codigos Postales
CREATE TABLE IF NOT EXISTS geo.codigos_postales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cp VARCHAR(10) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(cp, scd_is_current)
);

-- 6. Asentamientos
CREATE TABLE IF NOT EXISTS geo.asentamientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID REFERENCES geo.municipios(id),
    cp_id UUID REFERENCES geo.codigos_postales(id),
    asentamiento_tipo_id UUID REFERENCES geo.asentamiento_tipos(id),
    zona_tipo_id UUID REFERENCES geo.zona_tipos(id),
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(municipality_id, cp_id, name, scd_is_current)
);

-- 7. Ciudades
CREATE TABLE IF NOT EXISTS geo.ciudades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID REFERENCES geo.municipios(id),
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
