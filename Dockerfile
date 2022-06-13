FROM python:3.8.5-alpine3.12

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir -p /app
ADD storj_exporter /app
WORKDIR /app
ENV STORJ_HOST_ADDRESS=storagenode STORJ_API_PORT=14002 STORJ_EXPORTER_PORT=9651
CMD [ "python", "./" ]
