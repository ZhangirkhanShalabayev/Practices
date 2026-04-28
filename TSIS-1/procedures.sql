-- Drop existing functions/procedures
DROP FUNCTION IF EXISTS get_contacts_paginated(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS search_contacts(TEXT) CASCADE;
DROP PROCEDURE IF EXISTS move_to_group(VARCHAR, VARCHAR) CASCADE;
DROP PROCEDURE IF EXISTS add_phone(VARCHAR, VARCHAR, VARCHAR) CASCADE;

-- Procedure to add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- Find the contact by name
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name LIMIT 1;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name % not found', p_contact_name;
    END IF;
    
    -- Validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type. Must be: home, work, or mobile';
    END IF;
    
    -- Insert the phone number
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
    
    RAISE NOTICE 'Phone number % (%) added to contact %', p_phone, p_type, p_contact_name;
END;
$$;

-- Procedure to move a contact to a group (creates group if not exists)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id INTEGER;
BEGIN
    -- Find the contact by name
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name LIMIT 1;
    
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact with name % not found', p_contact_name;
    END IF;
    
    -- Check if group exists, if not create it
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'New group % created', p_group_name;
    END IF;
    
    -- Update contact with new group
    UPDATE contacts SET group_id = v_group_id, updated_at = CURRENT_TIMESTAMP
    WHERE id = v_contact_id;
    
    RAISE NOTICE 'Contact % moved to group %', p_contact_name, p_group_name;
END;
$$;

-- Function to search contacts by multiple fields (name, email, phone)
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone_number VARCHAR,
    phone_type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name,
        p.phone,
        p.type
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE 
        c.name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%'
    ORDER BY c.name, p.type;
END;
$$ LANGUAGE plpgsql;

-- Function for paginated query - FIXED
CREATE OR REPLACE FUNCTION get_contacts_paginated(
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    contact_id INTEGER,
    contact_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phone_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name,
        COUNT(ph.id)::INTEGER
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones ph ON c.id = ph.contact_id
    GROUP BY c.id, g.name
    ORDER BY c.name
    OFFSET p_offset
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
