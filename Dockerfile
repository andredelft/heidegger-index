FROM python:3.9-alpine

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /

ENV PORT=8000

EXPOSE $PORT
CMD ./entrypoint.sh $PORT
