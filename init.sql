-- Table creation
CREATE TABLE url (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE,
    css_enabled BOOLEAN NOT NULL DEFAULT 1,
    js_enabled BOOLEAN NOT NULL DEFAULT 1,
    frequency TEXT NOT NULL CHECK (frequency IN ('daily', 'hourly', 'weekly'))
);

-- Insert default test URLs
INSERT INTO url (address, css_enabled, js_enabled, frequency) VALUES
    ('https://example.com', 1, 1, 'daily'),
    ('https://testsite.dev', 1, 0, 'hourly'),
    ('https://nocss.example.org', 0, 1, 'weekly'),
    ('https://minimal.net', 0, 0, 'daily'),
    ('https://jsheavy.com', 1, 1, 'hourly');
