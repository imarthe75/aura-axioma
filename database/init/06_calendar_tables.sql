-- Aura Axioma - Calendar Tables
-- Operative holidays and business periods

CREATE TABLE IF NOT EXISTS calendars.holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL, -- Natural Key
    name TEXT NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'MX',
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

CREATE UNIQUE INDEX IF NOT EXISTS idx_calendars_holidays_current ON calendars.holidays(date, country_code) WHERE scd_is_current = TRUE;

COMMENT ON TABLE calendars.holidays IS 'Días festivos oficiales y bancarios';
