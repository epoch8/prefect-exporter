VERSION=$(shell cat pyproject.toml | sed -n 's/.*version = "\([^"]*\)".*/\1/p')


IMAGE=ghcr.io/epoch8/prefect-exporter:${VERSION}

update-requirements:
	poetry export -f requirements.txt > requirements.txt

build:
	docker build . -t ${IMAGE}

upload:
	docker push ${IMAGE}
