CREATE TABLE metadata_items
(
    id INTEGER PRIMARY KEY NOT NULL,
    library_section_id INTEGER,
    parent_id INTEGER,
    metadata_type INTEGER,
    guid TEXT,
    media_item_count INTEGER,
    title TEXT,
    title_sort TEXT,
    original_title TEXT,
    studio TEXT,
    rating REAL,
    rating_count INTEGER,
    tagline TEXT,
    summary TEXT,
    trivia TEXT,
    quotes TEXT,
    content_rating TEXT,
    content_rating_age INTEGER,
    "index" INTEGER,
    absolute_index INTEGER,
    duration INTEGER,
    user_thumb_url TEXT,
    user_art_url TEXT,
    user_banner_url TEXT,
    user_music_url TEXT,
    user_fields TEXT,
    tags_genre TEXT,
    tags_collection TEXT,
    tags_director TEXT,
    tags_writer TEXT,
    tags_star TEXT,
    originally_available_at TEXT,
    available_at TEXT,
    expires_at TEXT,
    refreshed_at TEXT,
    year INTEGER,
    added_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    deleted_at TEXT,
    tags_country TEXT,
    extra_data TEXT,
    hash TEXT,
    audience_rating REAL,
    changed_at INTEGER DEFAULT 0,
    resources_changed_at INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX index_metadata_items_on_resources_changed_at ON metadata_items (resources_changed_at);
CREATE UNIQUE INDEX index_metadata_items_on_changed_at ON metadata_items (changed_at);
CREATE UNIQUE INDEX index_metadata_items_on_originally_available_at ON metadata_items (originally_available_at);
CREATE UNIQUE INDEX index_metadata_items_on_added_at ON metadata_items (added_at);
CREATE UNIQUE INDEX index_metadata_items_on_hash ON metadata_items (hash);
CREATE UNIQUE INDEX index_metadata_items_on_library_section_id_and_metadata_type_and_added_at ON metadata_items (library_section_id, metadata_type, added_at);
CREATE UNIQUE INDEX index_metadata_items_on_deleted_at ON metadata_items (deleted_at);
CREATE UNIQUE INDEX index_metadata_items_on_metadata_type ON metadata_items (metadata_type);
CREATE UNIQUE INDEX index_metadata_items_on_guid ON metadata_items (guid);
CREATE UNIQUE INDEX index_metadata_items_on_title_sort ON metadata_items (title_sort);
CREATE UNIQUE INDEX index_metadata_items_on_title ON metadata_items (title);
CREATE UNIQUE INDEX index_metadata_items_on_index ON metadata_items ("index");
CREATE UNIQUE INDEX index_metadata_items_on_created_at ON metadata_items (created_at);
CREATE UNIQUE INDEX index_metadata_items_on_parent_id ON metadata_items (parent_id);
CREATE UNIQUE INDEX index_metadata_items_on_library_section_id ON metadata_items (library_section_id);
