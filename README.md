# Storj Exporter
---

Storj exporter for prometheus written in python.
This exporter pulls information from storj storage node api for `dashboard` and `satellite` metrics.

Can be used together with [Storj-Exporter-dashboard](https://github.com/anclrii/Storj-Exporter-dashboard) for Grafana to visualise metrics for multiple Storj storage nodes.

![combined dashboard](https://github.com/anclrii/Storj-Exporter-Dashboard/raw/master/combined%20dashboard.png)

Tested with storj storage node version `v0.22.1`

## Usage

* Exporter can be run as standalone script or docker container
* Make sure you have `-p 127.0.0.1:14002:14002` in storagenode container docker run command
* `--link=storagenode` is the name of the storage node container used to link exporter to it's network dynamically

### Docker
#### Run latest from DockerHub (easiest option, works out of the box provided above is set)

    docker run -d --link=storagenode --name=storj-exporter -p 9651:9651 anclrii/storj-exporter:latest
    
#### OR build your own
Clone this repo and cd, then

    docker build -t storj-exporter .
    docker run -d --link=storagenode --name=storj-exporter -p 9651:9651 storj-exporter

### Standalone script

    python3 storj-exporter.py

## Variables
Environment variables are available to manage storage node hostname and ports. Defaults are different for Docker/Standalone, mainly 127.0.0.1 is a default api host for standalone.

| Variable name | Docker default | Standalone default |
| --- | --- | --- |
| STORJ_HOST_ADDRESS | storagenode | 127.0.0.1 |
| STORJ_API_PORT | 14002 | 14002 |
| STORJ_EXPORTER_PORT | 9651 | 9651 |

## Support
Feel free to raise issues if you find any (currently needs more work) and also raise PR if you'd like to contribute.

You can also buy me a coffee with some Ether/Storj if you find this useful:

### `0x187C8C43890fe4C91aFabbC62128D383A90548Dd`
