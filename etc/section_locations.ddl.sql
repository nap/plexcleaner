CREATE TABLE section_locations
(
    id INTEGER PRIMARY KEY NOT NULL,
    library_section_id INTEGER,
    root_path TEXT,
    available INTEGER DEFAULT 't',
    scanned_at TEXT,
    created_at TEXT,
    updated_at TEXT
);
