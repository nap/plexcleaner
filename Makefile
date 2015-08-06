DB_PATH? = etc
DB_SQL? = $(DB_PATH)
DB_NAME? = test.db
DB? = $(DB_PATH)/$(DB_NAME)

all: build

.PHONY: clean schema data build
.DEFAULT: build
build: clean schema data

metadata_items.ddl:
	sqlite3 $(DB_NAME) < $(DB_SQL)/metadata_items.ddl.sql
media_items.ddl:
	sqlite3 $(DB_NAME) < $(DB_SQL)/media_items.ddl.sql
media_part.ddl:
	sqlite3 $(DB_NAME) < $(DB_SQL)/media_parts.ddl.sql
media_items.data:
	sqlite3 $(DB_NAME) < $(DB_SQL)/media_items.data.sql
media_part.data:
	sqlite3 $(DB_NAME) < $(DB_SQL)/media_parts.data.sql
metadata_items.data:
	sqlite3 $(DB_NAME) < $(DB_SQL)/metadata_items.data.sql

schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

clean:
	rm -f $(DB_NAME)