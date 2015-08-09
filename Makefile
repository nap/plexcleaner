DATA_PATH ?= test
DB_SQL ?= etc
DB_NAME ?= com.plexapp.plugins.library.db
PWD = $(shell pwd)

all: build

build: clean schema data files

metadata_items.ddl:
	@printf "Create schema metadata_items: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/metadata_items.ddl.sql
	@echo "done"
media_items.ddl:
	@printf "Create schema media_items: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_items.ddl.sql
	@echo "done"
media_part.ddl:
	@printf "Create schema media_part: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_parts.ddl.sql
	@echo "done"
media_items.data:
	@printf "Insert data media_items: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_items.data.sql
	@echo "done"
media_part.data:
	@printf "Insert data media_parts: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/media_parts.data.sql
	@echo "done"
metadata_items.data:
	@printf "Insert data metadata_items: "
	@sqlite3 $(DATA_PATH)/database/$(DB_NAME) < $(DB_SQL)/metadata_items.data.sql
	@echo "done"

schema: metadata_items.ddl media_items.ddl media_part.ddl

data: media_items.data media_part.data metadata_items.data

clean:
	@printf "Cleaning old test data: "
	@rm -f $(DATA_PATH)/{database,library}/*
	@mkdir -p $(DATA_PATH)/{database,library}
	@echo "done"

files:
	@echo
	@echo "Library in: $(PWD)/$(DATA_PATH)/library"
	@printf "Update test data with new file location: "
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT file FROM media_parts" | xargs -I {} basename "{}" | xargs -I {} touch $(DATA_PATH)/library/"{}"
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT id, file FROM media_parts" | \
	awk -F "|" '{printf $$1 " " $$2 "\n"}' | \
	while read ID FILE; do \
		env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "UPDATE media_parts SET file = '$(PWD)/$(DATA_PATH)/library/$$(basename "$$FILE")' WHERE id = $$ID"; \
	done
	@echo "done"