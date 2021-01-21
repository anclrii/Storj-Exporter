# Storj Exporter

Storj exporter for prometheus written in python. It pulls information from storj node api for `node`, `satellite` and `payout` metrics.

Also check out [Storj-Exporter-dashboard](https://github.com/anclrii/Storj-Exporter-dashboard) for Grafana to visualise metrics for multiple storj nodes.

Tested with storj node version `1.16.1`

<img src="https://github.com/anclrii/Storj-Exporter-dashboard/raw/master/storj-exporter-boom-table.png" alt="0x187C8C43890fe4C91aFabbC62128D383A90548Dd" hight=490 width=490 align="right"/> 

## Support
Feel free to raise issues if you find them and also raise a PR if you'd like to contribute.

<img src="qr.png" alt="0x187C8C43890fe4C91aFabbC62128D383A90548Dd" hight=100 width=100 align="right"/> 

If you wish to support my work :coffee:, please find my eth wallet address below or scan the qr code:


`0x187C8C43890fe4C91aFabbC62128D383A90548Dd`

## Usage

* Exporter can be installed as a docker container or a systemd service or a standalone script
* Make sure you have `-p 127.0.0.1:14002:14002` in storagenode container docker run command to allow local connections to storj node api
* `--link=storagenode` is the name of the storage node container used to link exporter to it's network dynamically, use your storj node container name if it differs

### Installation
#### Docker installation
##### Run latest build from DockerHub (easiest option, works out of the box provided above is set)

    docker run -d --link=storagenode --name=storj-exporter -p 9651:9651 anclrii/storj-exporter:latest

Docker image supports `linux/386,linux/amd64,linux/arm/v6,linux/arm/v7,linux/arm64` platforms.

##### OR build your own
Clone this repo and cd, then

    docker build -t storj-exporter .
    docker run -d --link=storagenode --name=storj-exporter -p 9651:9651 storj-exporter

---

#### Systemd service installation

##### Create storj-exporter user for service

    useradd --no-create-home --shell /bin/false storj_exporter

##### Install package dependencies

    Dependencies: python3 python3-pip
    pip3 install prometheus_client
    
##### Move storj_exporter to binary directory

    mv Storj-Exporter/storj-exporter.py /usr/local/bin/
    chown storj_exporter:storj_exporter /usr/local/bin/storj-exporter.py
    chmod +x /usr/local/bin/storj-exporter.py
   
##### Install systemd service and set to start on boot
    
    cp storj_exporter.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl restart storj_exporter
    systemctl enable storj_exporter

##### Standalone script

    python3 storj-exporter.py

---

##### Installing full monitoring stack (Prometheus + Grafana + Dashboard)

You can find some installation notes and guides in [dashboard README](https://github.com/anclrii/Storj-Exporter-dashboard#installing-full-monitoring-stack), also see [quick-start guide](https://github.com/anclrii/Storj-Exporter-dashboard/tree/master/quick_start) to set up the whole stack using docker-compose.

---

## Variables
Following environment variables are available:

| Variable name | Description | Docker default | Standalone default |
| --- | --- | --- | --- |
| STORJ_HOST_ADDRESS | Address of the storage node | storagenode | 127.0.0.1 |
| STORJ_API_PORT | Storage node api port | 14002 | 14002 |
| STORJ_EXPORTER_PORT | A port that exporter opens to expose metrics on | 9651 | 9651 |
| STORJ_COLLECTORS | A list of collectors | payout sat | payout sat |

### Collectors
By default exporter collects node, payout and satellite data from api. Satellite data is particularly expensive on cpu resources and disabling it might be useful on smaller systems

### Netdata
For users that use Netdata:
Netdata by default has a prometheus plugin enabled, which pulls all the data from the exporter every 5 seconds. This results in high CPU spikes on the storagenode. It is therefore advisable to disable the prometheus plugin of Netdata:
```
cd /etc/netdata
sudo ./edit-config go.d.conf
```
Then under "modules:" uncomment "prometheus" and change its value to "no":
```
modules:
#  activemq: yes
[...]
#  powerdns_recursor: yes
  prometheus: no
```
After that restart the netdata service:
```
sudo systemctl restart netdata
```
