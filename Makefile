DB_PATH = etc
DB_NAME = $(DB_PATH)/test.db

.PHONY: clean schema data build
.DEFAULT: build
build: clean schema data

metadata_items.ddl:
	sqlite3 $(DB_NAME) < $(DB_PATH)/metadata_items.ddl.sql
media_items.ddl:
	sqlite3 $(DB_NAME) < $(DB_PATH)/media_items.ddl.sql
media_part.ddl:
	sqlite3 $(DB_NAME) < $(DB_PATH)/media_parts.ddl.sql
media_items.data:
	sqlite3 $(DB_NAME) < $(DB_PATH)/media_items.data.sql
media_part.data:
	sqlite3 $(DB_NAME) < $(DB_PATH)/media_parts.data.sql
metadata_items.data:
	sqlite3 $(DB_NAME) < $(DB_PATH)/metadata_items.data.sql

schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

clean:
	rm -f $(DB_NAME)