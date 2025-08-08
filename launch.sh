#!/bin/bash

# run: ./file_name nb_gnbs nb_ues nb_rics

PASSWORD="ligm"

# Checking parameters
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <gnbs_number> <ues_number> <rics_number>"
    exit 1
fi

NUM_GNBS=$1
NUM_UES=$2
NUM_RIC=$3

# Function to start Core
launch_core() {
    echo "Starting Core Network..."
    gnome-terminal -- bash -c "cd ./srsRAN_Project/docker; echo $PASSWORD | sudo -S docker compose up 5gc; exec bash"
}

# Function to start RIC
launch_ric() {
    echo "Starting RIC..."
    gnome-terminal -- bash -c "cd ./oran-sc-ric; echo $PASSWORD | sudo -S docker compose up; exec bash"
}

# Function to start gNBs
launch_gnbs() {
    echo "Starting gNBs..."
    for i in $(seq 1 $NUM_GNBS); do
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb${i}.yaml e2; exec bash"
        sleep 2  # Attendre quelques secondes avant de lancer le prochain gNB
    done
}

# Function to launch a single gNB with or without RIC

launch_single_gnb() {
    if [ $NUM_RIC -eq 1 ]; then
        echo "Starting GNb with RIC..."
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb_zmq10.yaml e2 --addr='10.0.2.10' --bind_addr='10.0.2.1'; exec bash"
    else
        echo "Starting gNB without RIC..."
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb1.yaml e2; exec bash"
    fi
}

# Function for adding UE namespaces

add_ue_namespaces() { 
    echo "Ajout des namespaces des UEs..." 
    for i in $(seq 1 $NUM_UES); do 
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ip netns add ue$i; exec bash" 
        sleep 2 #Wait a few seconds before launching the next namespace
    done 
} 

# Function to start UEs
launch_ues() {
    echo "Lancement des UEs..."
    for i in $(seq 1 $NUM_UES); do
        gnome-terminal -- bash -c "cd ./srsRAN_4G/build/srsue/src/; echo $PASSWORD | sudo -S ./srsue ue${i}_zmq10.conf; exec bash"
    done
}

# Function to start Grafana
launch_grafana() {
    echo "Starting Grafana..."
    gnome-terminal -- bash -c "cd ./srsRAN_Project; echo $PASSWORD | sudo -S docker compose -f docker/docker-compose.yml up grafana; exec bash"
}

# Envoie des métriques à influsdb pour leur visualisation
send_to_influxdb() {
    #To launch for the first time, create the csv files in /tmp/ : touch ue1_metrics.csv
    echo "Sending metrics to InfluxDB..."
    gnome-terminal -- bash -c "cd ~/srsran/; python3.11 envoie_influxdb.py; exec bash"
}

# Fonction pour lancer GNU Radio Companion
launch_gnuradio() {
    #The GRC files to be launched are named as follows: ignb_scenarioj.grc with i: number of gNBs and j: number of UEs.
    echo "Starting GNU Radio..."
    gnome-terminal -- bash -c "cd ~/gnuradio; source ~/gnuradio_prefix/setup_env.sh; gnuradio-companion ./${NUM_GNBS}gnb_scenario${NUM_UES}.grc; exec bash"
}

launch_metrics_xapp(){	
    echo "Starting Xapp...."
    gnome-terminal -- bash -c "cd ./oran-sc-ric; echo $PASSWORD |sudo -S docker compose exec python_xapp_runner2 ./simple_mon_xapp.py; exec bash"
}

# Calling up functions
launch_core
sleep 5  # Wait for the core to launch

if [ $NUM_GNBS -eq 1 ]; then
    if [ $NUM_RIC -eq 1 ]; then
        launch_ric
        sleep 5  # Attendre que le RIC se lance
    fi
    launch_single_gnb
else
    launch_gnbs
fi

sleep 5  # AWaiting for GNBs to take the plunge
add_ue_namespaces
sleep 5  # Wait for namespaces to be added
launch_grafana
sleep 1
#send_to_influxdb
#sleep 1
launch_ues
sleep 5  # Attendre que les UEs se lancent
launch_gnuradio  # Lancer GNU Radio
#sleep 10
#launch_metrics_xapp
