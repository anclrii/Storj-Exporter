  
FROM python:3.7-alpine

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir -p /app
COPY storj-exporter.py /app
WORKDIR /app
ENV STORJ_HOST_ADDRESS=storagenode STORJ_API_PORT=14002 STORJ_EXPORTER_PORT=9651
CMD [ "python", "./storj-exporter.py" ]
