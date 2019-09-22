FROM python:3.7-alpine

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir -p /app
COPY storj-exporter.py /app
WORKDIR /app
CMD [ "python", "./storj-exporter.py" ]
