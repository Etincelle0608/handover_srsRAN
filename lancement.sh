#!/bin/bash

# lancement: ./nom_du_fichier nb_gnbs nb_ues nb_rics

PASSWORD="changeme"

# Vérification des paramètres
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <nombre_de_gnbs> <nombre_de_ues> <nombre_de_ric>"
    exit 1
fi

NUM_GNBS=$1
NUM_UES=$2
NUM_RIC=$3

# Fonction pour lancer le core
launch_core() {
    echo "Lancement du core..."
    gnome-terminal -- bash -c "cd ./srsRAN_Project/docker; echo $PASSWORD | sudo -S docker compose up --build 5gc; exec bash"
}

# Fonction pour lancer le RIC
launch_ric() {
    echo "Lancement du RIC..."
    gnome-terminal -- bash -c "cd ./oran-sc-ric; echo $PASSWORD | sudo -S docker compose up; exec bash"
}

# Fonction pour lancer les gNBs
launch_gnbs() {
    echo "Lancement des gNBs..."
    for i in $(seq 1 $NUM_GNBS); do
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb${i}.yaml e2; exec bash"
        sleep 2  # Attendre quelques secondes avant de lancer le prochain gNB
    done
}

# Fonction pour lancer un seul gNB avec ou sans RIC
launch_single_gnb() {
    if [ $NUM_RIC -eq 1 ]; then
        echo "Lancement du gNB avec RIC..."
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb_zmq10.yaml e2 --addr='10.0.2.10' --bind_addr='10.0.2.1'; exec bash"
    else
        echo "Lancement du gNB sans RIC..."
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb1.yaml e2; exec bash"
    fi
}

# Fonction pour ajouter les namespaces des UEs
add_ue_namespaces() { 
    echo "Ajout des namespaces des UEs..." 
    for i in $(seq 1 $NUM_UES); do 
        gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ip netns add ue$i; exec bash" 
        sleep 2 # Attendre quelques secondes avant de lancer le prochain namespace 
    done 
} 

# Fonction pour lancer les UEs
launch_ues() {
    echo "Lancement des UEs..."
    for i in $(seq 1 $NUM_UES); do
        gnome-terminal -- bash -c "cd ./srsRAN_4G/build/srsue/src/; echo $PASSWORD | sudo -S ./srsue ue${i}_zmq10.conf; exec bash"
    done
}




# Fonction pour lancer grafana
launch_grafana() {
    echo "Lancement de grafana..."
    gnome-terminal -- bash -c "cd ./srsRAN_Project; echo $PASSWORD | sudo -S docker compose -f docker/docker-compose.yml up grafana; exec bash"
}

# Envoie des métriques à influsdb pour leur visualisation
send_to_influxdb() {
    # Pour un premier lancement, créer les fichiers csv dans /tmp/ : touch ue1_metrics.csv
    echo "Envoi des métriques à InfluxDB..."
    gnome-terminal -- bash -c "python3.11 send_influxdb.py; exec bash"
}

# Fonction pour lancer GNU Radio Companion
launch_gnuradio() {
    # Les fichiers GRC à lancer sont nommés comme ceci: ignb_scenarioj.grc avec i:nombre de gNB et j: nombre d'UE
    echo "Lancement de GNU Radio..."
    gnome-terminal -- bash -c "cd ./gnuradio; gnuradio-companion ./${NUM_GNBS}gnb_scenario${NUM_UES}.grc; exec bash"
}

launch_metrics_xapp(){	
    echo "Lancement de l'xapp...."
    gnome-terminal -- bash -c "cd ./oran-sc-ric/xApps/python/; echo $PASSWORD |sudo -S docker compose exec python_xapp_runner2 ./simple_mon_xapp.py; exec bash"
}

# Appel des fonctions
launch_core
sleep 5  # Attendre que le core se lance

if [ $NUM_GNBS -eq 1 ]; then
    if [ $NUM_RIC -eq 1 ]; then
        launch_ric
        sleep 5  # Attendre que le RIC se lance
    fi
    launch_single_gnb
else
    launch_gnbs
fi

sleep 5  # Attendre que les gNBs se lancent
add_ue_namespaces
sleep 5  # Attendre que les namespaces soient ajoutés
launch_grafana
sleep 1
#send_to_influxdb
#sleep 1
launch_ues
sleep 5  # Attendre que les UEs se lancent
launch_gnuradio  # Lancer GNU Radio
#sleep 10
#launch_metrics_xapp
