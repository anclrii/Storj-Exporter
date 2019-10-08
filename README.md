# Storj Exporter
---

Storj exporter for prometheus written in python.

This exporter pulls information from storj storage node api for `dashboard` and `satellite` metrics.

Can be used together with [Storj-Exporter-dashboard](https://github.com/anclrii/Storj-Exporter-dashboard) for Grafana to visualise metrics for multiple Storj storage nodes.

![combined dashboard](https://github.com/anclrii/Storj-Exporter-Dashboard/raw/master/combined%20dashboard.png)

Tested with storj storage node version `v0.22.1`

## Usage
Exporter can be run as standalone script or docker container
### Standalone script

    python3 storj-exporter.py

### Docker
#### Build docker container

    docker build -t storj-exporter .

#### Run docker container

    docker run -d --link=storagenode --name=storjexporter -p 9651:9651 storj-exporterA

## Variables
Environment variables are available to manage storage node hostname and ports. Defaults are different for Docker/Standalone, mainly 127.0.0.1 is a default api host for standalone.

| Variable name | Docker default | Standalone default |
| --- | --- | --- |
| STORJ_HOST_ADDRESS | storagenode | 127.0.0.1 |
| STORJ_API_PORT | 14002 | 14002 |
| STORJ_EXPORTER_PORT | 9651 | 9651 |
