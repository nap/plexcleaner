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
