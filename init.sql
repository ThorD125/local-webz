-- Table creation
CREATE TABLE url (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    css_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    js_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'hourly', 'weekly'))
);

-- Insert default test URLs
INSERT INTO url (address, css_enabled, js_enabled, frequency) VALUES
    ('https://example.com', TRUE, TRUE, 'daily'),
    ('https://testsite.dev', TRUE, FALSE, 'hourly'),
    ('https://nocss.example.org', FALSE, TRUE, 'weekly'),
    ('https://minimal.net', FALSE, FALSE, 'daily'),
    ('https://jsheavy.com', TRUE, TRUE, 'hourly');
