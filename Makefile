HOST_PORT=5005
IMAGE_TAG=heidegger-index
ENV_FILE=.env
CONTAINER_NAME=HeideggerIndex

build:
	docker build -t $(IMAGE_TAG) .

run:
	touch $(ENV_FILE)
	docker run --name $(CONTAINER_NAME) --env DEBUG=0 --env-file $(ENV_FILE) -p $(HOST_PORT):8000 --detach $(IMAGE_TAG)

update:
	make build
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
	make run
