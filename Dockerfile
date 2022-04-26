FROM python:3.10-alpine
RUN apk add build-base

ADD requirements-prod.txt /
RUN pip install -r requirements-prod.txt

ADD . /

ENV PORT=8000

EXPOSE $PORT
CMD ./entrypoint.sh $PORT
