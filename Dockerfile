FROM python:3.9-alpine

WORKDIR /heidegger-index
ADD . /heidegger-index/

ENV PORT=8000

RUN pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE $PORT
CMD ./entrypoint.sh $PORT
