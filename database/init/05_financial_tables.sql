-- Aura Axioma - Financial & Calendars Tables

-- 1. Bancos (SPEI) & Financieras (CASFIM)
CREATE TABLE IF NOT EXISTS financial.instituciones_bancarias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clave CHAR(3) NOT NULL, -- Natural Key (e.g. 012, 002)
    nombre TEXT NOT NULL,
    corto TEXT,
    tipo_entidad TEXT, -- (e.g. BANCA MULTIPLE, SOFIPO, IFPE)
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

-- 2. Divisas (ISO 4217)
CREATE TABLE IF NOT EXISTS financial.cat_divisas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(3) NOT NULL, -- Natural Key (e.g. MXN, USD)
    name TEXT NOT NULL,
    symbol VARCHAR(5),
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

-- 3. Festivos (México)
CREATE TABLE IF NOT EXISTS calendars.festivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    holiday_date DATE NOT NULL, -- Natural Key (within year)
    name TEXT NOT NULL,
    is_official BOOLEAN DEFAULT TRUE,
    
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

-- Partial unique indices
CREATE UNIQUE INDEX IF NOT EXISTS idx_financial_instituciones_current ON financial.instituciones_bancarias(clave) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_financial_divisas_current ON financial.cat_divisas(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_calendars_festivos_current ON calendars.festivos(holiday_date) WHERE scd_is_current = TRUE;
