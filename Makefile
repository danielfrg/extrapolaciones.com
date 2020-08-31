SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PWD := $(shell pwd)

YES ?= 0
LOG ?= info


first: help

# ------------------------------------------------------------------------------
# Hugo


.PHONY: build
build: npm-build hugo  ## Build site


.PHONY: hugo
hugo: ## Run hugo build
	hugo


.PHONY: notebooks
notebooks:  ## Convert notebooks
	python nbconvert/convert.py


.PHONY: serve
serve:  ## Serve website
	hugo serve -F -D


# ------------------------------------------------------------------------------
# JS

npm-build:  ## Build JS
	cd $(CURDIR)/js/; npm run build


npm-install:  ## Install JS dependencies
	cd $(CURDIR)/js/; npm install


npm-dev:  ## Build JS with watch
	cd $(CURDIR)/js/; npm run dev


# ------------------------------------------------------------------------------
# Other


.PHONY: clean
clean:  ## Clean build files
	@rm -rf public


.PHONY: help
help:  ## Show this help menu
	@grep -E '^[0-9a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"; OFS="\t\t"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, ($$2==""?"":$$2)}'
