HOST_PORT=5003
IMAGE_TAG=heidegger-index
CONTAINER_NAME=HeideggerIndex
SECRET_KEY=$(SECRET_KEY)

build:
	docker build -t $(IMAGE_TAG) .

run:
	touch $(ENV_FILE)
	docker run --name $(CONTAINER_NAME) --env DEBUG=0 -e SECRET_KEY=$(SECRET_KEY) -p $(HOST_PORT):8000 --detach $(IMAGE_TAG)

update:
	make build
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
	make run
