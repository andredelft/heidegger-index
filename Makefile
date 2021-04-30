HOST_PORT=5003
IMAGE_TAG=heidegger-index
CONTAINER_NAME=HeideggerIndex
ENV_FILE=.env

build:
	docker build -t $(IMAGE_TAG) .

run:
	touch $(ENV_FILE)
	docker run --name $(CONTAINER_NAME) --env-file $(ENV_FILE) -p $(HOST_PORT):8000 --detach $(IMAGE_TAG)

update:
	make build
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
	make run
