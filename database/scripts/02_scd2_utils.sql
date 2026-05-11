-- Aura Axioma - SCD2 Utilities
-- Generic functions and logic for temporal tracking

-- Function to generate checksum for a record (excludes metadata and SCD columns)
CREATE OR REPLACE FUNCTION admin.calculate_checksum(row_data JSONB, exclude_keys TEXT[] DEFAULT '{id, scd_start_date, scd_end_date, scd_is_current, scd_version, scd_checksum, created_at, updated_at, metadata}') 
RETURNS TEXT AS $$
DECLARE
    clean_data JSONB;
BEGIN
    -- Remove excluded keys
    clean_data := row_data;
    FOR i IN 1 .. array_upper(exclude_keys, 1) LOOP
        clean_data := clean_data - exclude_keys[i];
    END LOOP;
    
    RETURN md5(clean_data::TEXT);
END;
$$ LANGUAGE plpgsql;

-- Trigger function to update timestamps
CREATE OR REPLACE FUNCTION admin.trg_update_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function to handle checksum on insert/update
CREATE OR REPLACE FUNCTION admin.trg_calculate_checksum()
RETURNS TRIGGER AS $$
BEGIN
    NEW.scd_checksum = admin.calculate_checksum(to_jsonb(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- View helper to get current records
CREATE OR REPLACE VIEW admin.vw_current_catalogs AS
SELECT * FROM (
    SELECT 'geo.paises' as table_name, * FROM geo.paises WHERE scd_is_current = TRUE
    -- This will be expanded as tables are added
) AS t;
