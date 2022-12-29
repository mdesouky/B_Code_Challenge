#!/usr/bin/env make
include Makehelp

SHELL := /bin/bash  -o pipefail


# Install Python Requirements for CDK
define install_requirements
	[[ -d ".venv" ]] && \
	echo "Python Environment already exists" || \
	echo "Creating Python Environment" && \
	python3 -m venv .venv && \
	echo "Activating Python virtual environment" && \
	source .venv/bin/activate && \
	echo "Installing Python Requirements" && \
	python3 -m pip install --upgrade pip && \
	pip install -q -r requirements.txt -r requirements-dev.txt && $1
endef


.ONESHELL:
## Run Unit tests on CDK code
test:
	@$(call install_requirements,pytest -v)
.PHONY: test

.ONESHELL:
## Synthesize Cloudformation Stacks from CDK Code for the target account/environment
synth:
	@$(call install_requirements,cdk synth)
.PHONY: synth

.ONESHELL:
## Show CDK diff on the target account/environment
diff:
	@$(call install_requirements,cdk diff)
.PHONY: diff

.ONESHELL:
## Fetch CDK context from the target account
context:
	@$(call install_requirements,cdk context)
.PHONY: context

.ONESHELL:
## Deploy All CDK Stacks into the target account
deploy:
	@$(call install_requirements,cdk deploy --all)
.PHONY: deploy

.ONESHELL:
## Destroy All CDK Stacks in the target account
destroy:
	@$(call install_requirements,cdk destroy --all)
.PHONY: destroy

.ONESHELL:
## Install Bootstrap CDK into the target account
bootstrap:
	@$(call install_requirements, cdk bootstrap)
.PHONY: bootstrap

.ONESHELL:
## Install Pre-Commit Hooks
install-pre-commit:
	pre-commit install --install-hooks
.PHONY: install-pre-commit
