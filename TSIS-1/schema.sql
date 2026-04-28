-- Drop existing objects (if needed for fresh start)
DROP TABLE IF EXISTS phones CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS groups CASCADE;

-- Create groups table
CREATE TABLE groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create contacts table with extended fields
CREATE TABLE contacts (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(100),
    birthday  DATE,
    group_id  INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create phones table for 1-to-many relationship
CREATE TABLE phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) NOT NULL CHECK (type IN ('home', 'work', 'mobile')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default groups
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other');

-- Create indexes for faster queries
CREATE INDEX idx_contacts_name ON contacts(name);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_group_id ON contacts(group_id);
CREATE INDEX idx_phones_contact_id ON phones(contact_id);
CREATE INDEX idx_phones_phone ON phones(phone);
