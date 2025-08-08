# Description

The repository contains all the configurations, scripts and tools needed to deploy and test a 5G O-RAN infrastructure, with mobility scenarios. 

Ndeye Birame DIA, Massamaesso NAROUWA and Léo MENDIBOURE are the main contributors to this work.

For any question/issue, please contact massamaesso.narouwa@univ-eiffel.fr

This code is currently being used to produce an article that is currently being evaluated.


# Prerequisites

Before using this repository, please ensure that your environment is correctly configured:
- Linux (Ubuntu 22.04 recommended but Ubuntu 24.04 also tested).
- Docker and Docker Compose
- GNU Radio Companion
- Python 3.11 and the necessary libraries
- Open5GS, srsRAN, et ORAN SC RIC (this last one is not required to reproduce the article results)

# Files Available in the Repository

This repository contains a number of files that are essential for configuring and running the various mobility scenarios. Here is a detailed description of the files and how they are used:

### Yaml files (amf, upf and smf)
The ``amf.yaml``, ``upf.yaml`` and ```smf.yaml`` files are essential for configuring the Open5GS network core. They define the parameters required for the correct operation of each network component and their interconnection with the gNB.

These files are located in the following directory: ``/etc/open5gs/ ````.

It is essential to maintain consistency between these YAML files and the gNB configuration file. Parameters to check include
- The IP addresses used for the core network interfaces (AMF, UPF and SMF) and their correspondence with the IP addresses configured in the gNB YAML file.
- The ports specified for communications between the core components and the gNB.

### Configuration files for UEs and gNBs
- Configuration files are available for 4 UEs operating at bandwidths of 10 Hz and 20 Hz.
- Configuration files are also provided for one gNB configured for 10 Hz and 20 Hz bandwidths.
- For a deployment with two gNBs, specific files are provided: ```gnb1.yaml`` and ```gnb2.yaml``, each configured for a separate gNB.

### GNU Radio files (GRC)
Several GNU Radio Companion (GRC) files are available to simulate different scenarios.
GRC files are named according to a clear convention: ngnb_scenariom.grc, where :
- n represents the number of gNBs.
- m represents the number of UEs.
- For example :
- 1gnb_scenario4.grc corresponds to a simulation with 1 gNB and 4 SUs.
- 2gnb_scenario3.grc corresponds to a simulation with 2 gNBs and 3 SUs.

### Results files 

This folder contains, in an ods format, the pre-processed data generated for the different evaluation scenarios discussed in the article currently being submitted.

# Operating Instructions

## 1 Launching the Basic Components
To launch the basic components needed to deploy the platform (such as the gNB, the network core (5GC), and the Near-RT-RIC etc), you can follow the detailed guide
available in the official srsRAN documentation: https://docs.srsran.com/projects/project/en/latest/tutorials/source/near-rt-ric/source/index.html 

To launch Grafana, which allows you to view metrics, you can consult the documentation here: https://docs.srsran.com/projects/project/en/latest/user_manuals/source/grafana_gui.html


## 2 Launching the xApp for metrics feedback
The custom xApp, which collects and centralises metrics from UEs and gNB, needs to be launched in the RIC's Docker container. Here's how to start it:

```bash
cd ./oran-sc-ric
sudo docker compose exec python_xapp_runner2 ./simple_mon_xapp.py
```
The python executor ``python_xapp_runner2`` has been added (docker-compose.yml from the ric) to meet the needs of the xApp created. However the ``python_xapp_runner`` executor given by ORAN is kept and must be used for xApps provided by ORAN SC RIC.

This xApp created will collect key metrics, such as CQI, throughput (UL/DL), and latency etc, and save them to a JSON file for later analysis.

## 3 Scripts Made (7 Python and 1 Shell), and How to Use Them

This repository contains eight main scripts (seven in Python and one in Shell) used to manage, deploy and analyse the infrastructure. Each script is designed to meet a specific need and can be run from the directory where it is placed in the Git repository.

### Running scripts

To run a Python script, use the following command :

```bash
python3.11 script_name.py  
```
The Shell script, called launch.sh, is launched with the following command:

```bash
./launch.sh <nombre_gnb> <nombre_ue> <nombre_ric>  
```
For example, to deploy 1 gNB, 4 UEs, and 1 RIC :
```bash
./launch.sh 1 4 1  
```

### Current limits

For the moment, the launch.sh script can launch up to 2 gNBs without integrating a RIC. However, it is easy to add gNBs or configure the RIC launch. Simply :

- Add a new loop or command in the launch.sh file to manage the additional gNBs.
- Modify the associated configurations (IP addresses, ports, etc.) in the necessary files.

NB: To integrate ORAN SC RIC in this environment, you will need as many RICs as gNBs (one ric for one gNB).

The script is designed to be flexible and extensible, allowing more complex architectures to be managed with little effort.

### Customisation and Flexibility
The launch.sh script is designed to be flexible. Before running it, some modifications may be necessary to adapt it to your environment:
- Directories: Readjust the directory paths depending on where the files are located.
- User accounts: Modify the passwords or identifiers used in the script so that they match your configuration.
- Custom additions: This script is flexible enough to allow new features or additional components to be added if required.

### Location of Scripts
Some Python scripts are located in :
```bash
/srsRAN_Project/build/apps/gnb/ 
```
Other Python scripts and the Shell script are located in the same directory as the ```srsRAN_Project``` folder.

### Script descriptions
Each script contains a description at the top of the file explaining :
- Its purpose: What the script does (e.g. collecting metrics, generating datasets).
- Prerequisites: what you need to run it properly (e.g. Python libraries, specific configurations).

### Sending metrics to influxDB
Another ``influxdb1`` container has been added to the docker-compose.yml (the one in /srsRAN_Project/docker/) to add another instance of InfluxDB. 
This container should create an influxdb user account that can be accessed at http://localhost:8087/.
However, this account may not be created, and can therefore be created with this:
```bash
sudo docker exec -it influxdb1 influx setup \
--username admin1 \
--password admin12345
--org srs1 \
--bucket srsran1 \
--token 605bc59413b7d5457d181ccf20f9fda15693f81b068d70396cc183081b264fbb \
--host http://localhost:8087
```
If you change one of these parameters when you create the account, do the same with the ``send_influxdb.py`` script!
Metrics are sent to the InfluxDB database using the ``send_influxdb.py`` script. This script transfers the metrics generated by the UEs to InfluxDB in real time, making them easier to view and analyse at a later date.

When deploying for the first time, it is necessary to ensure that the necessary files exist before running the script. To do this, first start the UEs (without running GNU Radio), then stop them immediately afterwards. This step allows the UEs to create the files needed for the script to run.

Once the files have been generated, the ``send_influxdb.py`` script must be run before restarting the UEs so that the metrics can be monitored and sent to InfluxDB in real time.

### Dataset generation
Dataset generation is based on two main scripts: metrics_udp_receiver.py and subband.py. The first is used to collect real-time network metrics transmitted by the gNB via the UDP protocol. This script must be run after the gNB is started and can be run before or after the UEs are launched. Once the metrics have been collected, the subband.py script is used to process and enrich them. This script, which is run at the end of the experiment after metrics_udp_receiver.py has been stopped, calculates the IQC subbands by breaking down the overall IQC into several sub-values. The final data is then saved in JSON files, constituting the datasets required for future analysis or experimentation.

### Retrieving grafana dashboards as images (png)
A renderer container (name to be retained) has been added to the docker-compose.yml file (the one in /srsRAN_Project/docker/) and linked to grafana. 
Here are the steps to take to retrieve the files from the grafana interface:
- On the dashboard to be exported, in the top right-hand corner, click on the three vertical dots to open an additional menu.
- In this menu, click on the ‘Share’ option.
- Once in the Share interface, you'll see several customisation options for the export:
- You can choose the theme of the image: either the default theme (black), dark, or light. If you want the background of the image to be white, choose light.


### JSON files for datasets

The JSON files generated represent the datasets produced for the five mobility scenarios, thanks to the ```subband.py`` script.

Here is a description of each scenario:

#### Scenario 1:

This scenario involves four UEs travelling at a speed of 60 km/h. UE1 remains fixed at a constant distance of 500m from the gNB, while the other three UEs (UE2, UE3, and UE4) move in the positive direction, with initial positions of X0=100, -900, and 700 respectively.

#### Scenario 2:

This scenario is similar to the previous one, except that the UEs move in the negative direction.

#### Scenario 3:

In this scenario, UE1 is no longer fixed and starts at X0=-300, moving in the positive direction with UE2. UE3 and UE4 move in the negative direction.

#### Scenario 4:

This scenario involves two UEs moving in opposite directions:
- UE1 starts at X0=1500 and moves in the negative direction.
- UE2 starts at X0=-1300 and moves in the positive direction.

#### Scenario 5:
This last scenario repeats the initial positions of scenario 4, but this time the two UEs both move in the positive direction.
