-- Aura Axioma - Additional SAT Catalogs (c_Banco and c_Pais)

-- 1. Bancos del SAT (c_Banco)
CREATE TABLE IF NOT EXISTS fiscal.cat_bancos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(3) NOT NULL, -- Natural Key (e.g. 012, 002)
    nombre_corto TEXT NOT NULL,
    razon_social TEXT NOT NULL,
    rfc VARCHAR(15) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_bancos_current ON fiscal.cat_bancos(code) WHERE scd_is_current = TRUE;

-- 2. Países del SAT (c_Pais)
CREATE TABLE IF NOT EXISTS fiscal.cat_paises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(3) NOT NULL, -- Natural Key (e.g. MEX, USA)
    description TEXT NOT NULL,
    agrupacion TEXT,
    active BOOLEAN DEFAULT TRUE,
    
    -- SCD2
    scd_start_date TIMESTAMPTZ DEFAULT NOW(),
    scd_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    scd_is_current BOOLEAN DEFAULT TRUE,
    scd_version INTEGER DEFAULT 1,
    scd_checksum TEXT NOT NULL,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_paises_current ON fiscal.cat_paises(code) WHERE scd_is_current = TRUE;
