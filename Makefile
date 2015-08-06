DB_NAME = etc/test.db

metadata_items.ddl:
	sqlite3 $(DB_NAME) < etc/metadata_items.ddl.sql
media_items.ddl:
	sqlite3 $(DB_NAME) < etc/media_items.ddl.sql
media_part.ddl:
	sqlite3 $(DB_NAME) < etc/media_parts.ddl.sql
media_items.data:
	sqlite3 $(DB_NAME) < etc/media_items.data.sql
media_part.data:
	sqlite3 $(DB_NAME) < etc/media_parts.data.sql
metadata_items.data:
	sqlite3 $(DB_NAME) < etc/metadata_items.data.sql

.PHONY: schema data build clean
schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

build: clean schema data

clean:
	rm -f etc/test.db