# Storj Exporter
---

Storj exporter for prometheus written in python.
This exporter pulls information from storj node api for `node`, `satellite` and `payout` metrics.

Can be used together with [Storj-Exporter-dashboard](https://github.com/anclrii/Storj-Exporter-dashboard) for Grafana to visualise metrics for multiple Storj storage nodes.

![combined dashboard](https://github.com/anclrii/Storj-Exporter-Dashboard/raw/master/combined%20dashboard.png)

Tested with storage node version `1.16.1`

## Support
<img src="https://avatars2.githubusercontent.com/u/40526988?s=120&v=4" alt="Markdown Monster icon" width=150 hight=150 align="right"/> 

Feel free to raise issues if you find any and also raise a PR if you'd like to contribute.

If you wish to support my work :coffee:, please find my eth wallet address below or scan the qr code:

### `0x187C8C43890fe4C91aFabbC62128D383A90548Dd`
<br clear="right"/>

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
   
### Linux Installation

#### Create storj-exporter user for service

    useradd --no-create-home --shell /bin/false storj_exporter

#### Install package dependencies

    Dependencies: python3 python3-pip
    pip3 install prometheus_client
    
#### Move storj_exporter to binary directory

    mv Storj-Exporter/storj-exporter.py /usr/local/bin/
    chown storj_exporter:storj_exporter /usr/local/bin/storj-exporter.py
    chmod +x /usr/local/bin/storj-exporter.py
   
#### Install systemd service and set to start on boot
    
    cp storj_exporter.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl restart storj_exporter
    systemctl enable storj_exporter

## Variables
Environment variables are available to manage storage node hostname and ports. Defaults are different for Docker/Standalone, mainly 127.0.0.1 is a default api host for standalone.

| Variable name | Docker default | Standalone default |
| --- | --- | --- |
| STORJ_HOST_ADDRESS | storagenode | 127.0.0.1 |
| STORJ_API_PORT | 14002 | 14002 |
| STORJ_EXPORTER_PORT | 9651 | 9651 |
