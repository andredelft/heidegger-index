FROM python:3.10-alpine
RUN apk add build-base gettext

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /

ENV PORT=8000

EXPOSE $PORT
CMD ./entrypoint.sh $PORT
