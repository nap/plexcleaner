PATH ?= test
DB_SQL ?= etc
DB_NAME ?= com.plexapp.plugins.library.db

all: build

build: clean schema data files

metadata_items.ddl:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/metadata_items.ddl.sql
media_items.ddl:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/media_items.ddl.sql
media_part.ddl:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/media_parts.ddl.sql
media_items.data:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/media_items.data.sql
media_part.data:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/media_parts.data.sql
metadata_items.data:
	sqlite3 $(PATH)/$(DB_NAME) < $(DB_SQL)/metadata_items.data.sql

schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

clean:
	rm -f $(PATH)/database/$(DB_NAME)
	mkdir -p $(PATH)

files:
	env sqlite3 $(PATH)/database/$(DB_NAME) "SELECT file FROM media_parts" |
	xargs -I {} basename "{}" | xargs -I {} touch $(PATH)/library/"{}"
	env sqlite3 $(PATH)/database/$(DB_NAME) "SELECT id, file FROM media_parts" |
	awk -F "|" '{printf $1 " " $2 "\n"}' |
	while read ID FILE; do
		sqlite3 $(PATH)/database/$(DB_NAME) "UPDATE media_parts SET file = '$(PATH)/library/$(basename "$FILE")' WHERE id = $ID";
	done