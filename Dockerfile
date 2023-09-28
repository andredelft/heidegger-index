FROM python:3.11
ADD . /
ENV PORT=8000
EXPOSE $PORT
RUN pip install --upgrade pip && pip install -r requirements/production.txt

# Ensure cache is always invalidated from here, for an updated download of the required packages
ARG CACHEBUST=1
RUN echo "$CACHEBUST"
RUN pip install -r requirements/no-cache.txt

CMD ./entrypoint.sh $PORT