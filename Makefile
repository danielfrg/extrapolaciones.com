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
# Python

env:  ## Create python env
	mamba env create

articles:  ## Make articles from Notion
	python python/articles.py

# ------------------------------------------------------------------------------
# JS

npm-build:  ## Build JS
	cd $(CURDIR)/js/; npm run build


npm-install:  ## Install JS dependencies
	cd $(CURDIR)/js/; npm install


npm-dev:  ## Build JS with watch
	cd $(CURDIR)/js/; npm run dev

# ------------------------------------------------------------------------------
# Hugo

build: npm-build hugo  ## Build site


hugo: ## Run hugo build
	hugo

serve:  ## Serve website
	hugo serve

serve-all:  ## Serve website: includes drafts and future
	hugo serve -F -D

# ------------------------------------------------------------------------------
# Other

clean:  ## Clean build files
	rm -rf public
	rm -rf content/articles/generated


help:  ## Show this help menu
	@grep -E '^[0-9a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"; OFS="\t\t"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, ($$2==""?"":$$2)}'
