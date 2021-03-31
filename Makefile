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

build: npm-build hugo  ## Build site


# ------------------------------------------------------------------------------
# Python (Notion)

env:  ## Create python env
	mamba env create


articles:  ## Make articles from Notion
	python python/articles.py


# ------------------------------------------------------------------------------
# JS

theme:  # Build theme from danielfrg.com
	cd $(CURDIR)/danielfrg.com/theme/js; npm run build


npm-build:  ## Build JS
	cd $(CURDIR)/js/; npm run build


npm-i: npm-install
npm-install:  ## Install JS dependencies
	cd $(CURDIR)/js/; npm install


npm-dev:  ## Build JS with watch
	cd $(CURDIR)/js/; npm run dev


clean-js:  ## Clean JS files
	rm -rf $(CURDIR)/js/dist
	rm -rf $(CURDIR)/static/dist/*


cleanall-js: clean-js  ## Clean JS files
	rm -rf $(CURDIR)/js/node_modules


# ------------------------------------------------------------------------------
# Hugo

hugo: ## Run hugo build
	hugo


serve:  ## Serve website
	hugo serve -F -D

# ------------------------------------------------------------------------------
# Other

clean:  ## Clean build files
	rm -rf public
	rm -rf content/articles/generated-notion


cleanall: clean cleanall-js   ## Clean everything


help:  ## Show this help menu
	@grep -E '^[0-9a-zA-Z_-]+:.*?##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"; OFS="\t\t"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, ($$2==""?"":$$2)}'
