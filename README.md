# Storj Exporter
---

Storj exporter for prometheus written in python.

This exporter pulls information from storj storage node api for `dashboard` and `satellite` metrics.

Tested with storj storage node version `0.21.1`

## Build docker container

    docker build -t storj-exporter .

## Run docker container

    docker run -d --link=storagenode --name=storjexporter -p 9651:9651 storj-exporter
