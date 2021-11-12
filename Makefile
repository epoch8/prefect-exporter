VERSION=$(shell cat pyproject.toml | sed -n 's/.*version = "\([^"]*\)".*/\1/p')


IMAGE=ghcr.io/epoch8/prefect-exporter:${VERSION}


build:
	docker build . -t ${IMAGE}

upload:
	docker push ${IMAGE}
