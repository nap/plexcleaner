CREATE TABLE media_parts
(
    id INTEGER PRIMARY KEY NOT NULL,
    media_item_id INTEGER,
    directory_id INTEGER,
    hash TEXT,
    open_subtitle_hash TEXT,
    file TEXT,
    "index" INTEGER,
    size INTEGER,
    duration INTEGER,
    created_at TEXT,
    updated_at TEXT,
    deleted_at TEXT,
    extra_data TEXT
);
