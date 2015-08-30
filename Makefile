DATA_PATH ?= tests
DB_SQL ?= etc
DB_NAME ?= com.plexapp.plugins.library.db
PWD = $(shell pwd)

all: build

build: clean schema data movies dummy

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
	@rm -Rf $(DATA_PATH)/database $(DATA_PATH)/library $(DATA_PATH)/posters $(DATA_PATH)/dummy
	@mkdir $(DATA_PATH)/database $(DATA_PATH)/library $(DATA_PATH)/posters $(DATA_PATH)/dummy
	@echo "done"

movies:
	@echo
	@echo "Library in: $(PWD)/$(DATA_PATH)/library"
	@echo "Posters in: $(PWD)/$(DATA_PATH)/posters"
	@printf "Generating test media file: "
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT file FROM media_parts" | xargs -I {} basename "{}" | xargs -I {} touch $(DATA_PATH)/library/"{}"
	@echo "done"
	@printf "Update test data with new file location: "
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT id, file FROM media_parts" | \
	awk -F "|" '{printf $$1 " " $$2 "\n"}' | \
	while read ID FILE; do \
		env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "UPDATE media_parts SET file = '$(PWD)/$(DATA_PATH)/library/$$(basename "$$FILE")' WHERE id = $$ID"; \
	done
	@echo "done"
	@printf "Generating bad database: "
	@env echo 'bad_data' > $(DATA_PATH)/database/bad.db
	@env touch $(DATA_PATH)/database/empty.db
	@env touch $(DATA_PATH)/database/backup.db
	@echo "done"
	@printf "Generating test poster file: "
	@env sqlite3 $(DATA_PATH)/database/$(DB_NAME) "SELECT user_thumb_url FROM metadata_items" | cut -d "/" -f 3- | xargs -P 10 -I {} touch $(DATA_PATH)/"{}"
	@echo "done"

dummy:
	@printf "Generating dummy file: "
	@echo $$(ps aux | grep $$(whoami) | tr -s ' ' | cut -d ' ' -f 2 | head -n 1) > $(DATA_PATH)/dummy/ok.pid
	@echo 1 > $(DATA_PATH)/dummy/ok_no_perm.pid
	@echo '' > $(DATA_PATH)/dummy/empty.pid
	@echo '9879876987876879' > $(DATA_PATH)/dummy/bad.pid
	@echo '32768' > $(DATA_PATH)/dummy/max.pid
	@echo "done"