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
CREATE UNIQUE INDEX index_media_parts_on_size ON media_parts (size);
CREATE UNIQUE INDEX index_media_parts_on_deleted_at ON media_parts (deleted_at);
CREATE UNIQUE INDEX index_media_parts_on_file ON media_parts (file);
CREATE UNIQUE INDEX index_media_parts_on_hash ON media_parts (hash);
CREATE UNIQUE INDEX index_media_parts_on_media_item_id ON media_parts (media_item_id);
CREATE UNIQUE INDEX index_media_parts_on_directory_id ON media_parts (directory_id);
