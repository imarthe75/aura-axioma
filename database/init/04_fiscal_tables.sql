-- Aura Axioma - Fiscal Tables (SAT)

-- 1. Claves de Productos y Servicios
CREATE TABLE IF NOT EXISTS fiscal.cat_prod_serv (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(10) NOT NULL, -- Natural Key (e.g. 01010101)
    description TEXT NOT NULL,
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

-- 2. Unidades de Medida
CREATE TABLE IF NOT EXISTS fiscal.cat_unidades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(5) NOT NULL, -- Natural Key (e.g. H87, E48)
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

-- 3. Regímenes Fiscales
CREATE TABLE IF NOT EXISTS fiscal.cat_regimen_fiscal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(5) NOT NULL, -- Natural Key (e.g. 601)
    description TEXT NOT NULL,
    persona_fisica BOOLEAN,
    persona_moral BOOLEAN,
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

-- 4. Uso de CFDI
CREATE TABLE IF NOT EXISTS fiscal.cat_uso_cfdi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(5) NOT NULL, -- Natural Key (e.g. G01)
    description TEXT NOT NULL,
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

-- 5. Monedas (SAT)
CREATE TABLE IF NOT EXISTS fiscal.cat_monedas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(3) NOT NULL, -- Natural Key (e.g. MXN)
    description TEXT NOT NULL,
    decimals INTEGER DEFAULT 2,
    variation_pct DECIMAL(10,4),
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

-- 6. Formas de Pago
CREATE TABLE IF NOT EXISTS fiscal.cat_forma_pago (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(2) NOT NULL, -- Natural Key (e.g. 01, 03)
    description TEXT NOT NULL,
    bancarizado BOOLEAN,
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

-- 7. Métodos de Pago
CREATE TABLE IF NOT EXISTS fiscal.cat_metodo_pago (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(3) NOT NULL, -- Natural Key (e.g. PUE, PPD)
    description TEXT NOT NULL,
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

-- 8. Exportación
CREATE TABLE IF NOT EXISTS fiscal.cat_exportacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(2) NOT NULL, -- Natural Key (e.g. 01, 02)
    description TEXT NOT NULL,
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

-- 9. Objeto Impuesto
CREATE TABLE IF NOT EXISTS fiscal.cat_objeto_imp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code CHAR(2) NOT NULL, -- Natural Key (e.g. 01, 02)
    description TEXT NOT NULL,
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

-- Partial unique indices
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_prod_serv_current ON fiscal.cat_prod_serv(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_unidades_current ON fiscal.cat_unidades(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_regimen_current ON fiscal.cat_regimen_fiscal(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_uso_cfdi_current ON fiscal.cat_uso_cfdi(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_monedas_current ON fiscal.cat_monedas(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_forma_pago_current ON fiscal.cat_forma_pago(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_metodo_pago_current ON fiscal.cat_metodo_pago(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_exportacion_current ON fiscal.cat_exportacion(code) WHERE scd_is_current = TRUE;
CREATE UNIQUE INDEX IF NOT EXISTS idx_fiscal_objeto_imp_current ON fiscal.cat_objeto_imp(code) WHERE scd_is_current = TRUE;
