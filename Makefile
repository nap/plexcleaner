DATA_PATH ?= test
DB_SQL ?= etc
DB_NAME ?= com.plexapp.plugins.library.db

all: build

build: clean schema data files

metadata_items.ddl:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/metadata_items.ddl.sql
media_items.ddl:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_items.ddl.sql
media_part.ddl:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_parts.ddl.sql
media_items.data:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_items.data.sql
media_part.data:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_parts.data.sql
metadata_items.data:
	sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/metadata_items.data.sql

schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

clean:
	@echo "Cleaning old test data"
	rm -f $(DATA_PATH)/{database,library}/*
	mkdir -p $(DATA_PATH)/{database,library}
	@echo "Done."

files:
	@echo "Update test data with new file location..."
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT file FROM media_parts" | xargs -I {} basename "{}" | xargs -I {} touch $(DATA_PATH)/library/"{}"
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT id, file FROM media_parts" | \
	awk -F "|" '{printf $$1 " " $$2 "\n"}' | \
	while read ID FILE; do \
		sqlite3 $(DATA_PATH)/database/$(DB_NAME) "UPDATE media_parts SET file = '$(DATA_PATH)/library/$$(basename "$$FILE")' WHERE id = $$ID"; \
	done
	@echo "Done."