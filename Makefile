CONTAINER_CMD=$(shell which podman 2>/dev/null || which docker)
TAG ?= latest

pre-commit:
	pre-commit run --all-files

test:
	tox

commit: pre-commit test

container-build:
	$(CONTAINER_CMD) build -f container/Dockerfile -t quay.io/redhatqe/qe-metrics:$(TAG) .

container-push:
	$(CONTAINER_CMD) push quay.io/redhatqe/qe-metrics:$(TAG)

container-test:
	$(CONTAINER_CMD) run -it --env-file development/env.list --entrypoint /bin/bash qe-metrics:$(TAG) /development/test.sh

container-run:
	$(CONTAINER_CMD) run -it --env-file development/env.list --entrypoint /bin/bash qe-metrics:$(TAG)

container-build-run: container-build container-run

container-build-test: container-build container-test
