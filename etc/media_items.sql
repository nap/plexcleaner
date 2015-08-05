CREATE TABLE media_items
(
    id INTEGER PRIMARY KEY NOT NULL,
    library_section_id INTEGER,
    section_location_id INTEGER,
    metadata_item_id INTEGER,
    type_id INTEGER,
    width INTEGER,
    height INTEGER,
    size INTEGER,
    duration INTEGER,
    bitrate INTEGER,
    container TEXT,
    video_codec TEXT,
    audio_codec TEXT,
    display_aspect_ratio REAL,
    frames_per_second REAL,
    audio_channels INTEGER,
    interlaced INTEGER,
    source TEXT,
    hints TEXT,
    display_offset INTEGER,
    settings TEXT,
    created_at TEXT,
    updated_at TEXT,
    optimized_for_streaming INTEGER,
    deleted_at TEXT,
    media_analysis_version INTEGER DEFAULT 0,
    sample_aspect_ratio REAL,
    extra_data TEXT
);
CREATE UNIQUE INDEX index_media_items_on_media_analysis_version ON media_items (media_analysis_version);
CREATE UNIQUE INDEX index_media_items_on_deleted_at ON media_items (deleted_at);
CREATE UNIQUE INDEX index_media_items_on_metadata_item_id ON media_items (metadata_item_id);
CREATE UNIQUE INDEX index_media_items_on_library_section_id ON media_items (library_section_id);
