#!/bin/bash

# lancement: ./nom_du_fichier nb_gnbs nb_ues nb_rics

PASSWORD="changeme"

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
    echo "Lancement du gNB avec RIC..."
    gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ./gnb -c gnb_zmq_nearRT.yaml e2; exec bash"
}

# Fonction pour ajouter les namespaces des UEs
add_ue_namespaces() { 
    echo "Ajout des namespaces des UEs..." 
    gnome-terminal -- bash -c "cd ./srsRAN_Project/build/apps/gnb/; echo $PASSWORD | sudo -S ip netns add ue1; exec bash" 
    sleep 2 # Attendre quelques secondes avant de lancer le prochain namespace 
} 

# Fonction pour lancer les UEs
launch_ues() {
    echo "Lancement des UEs..."
    gnome-terminal -- bash -c "cd ./srsRAN_4G/build/srsue/src/; echo $PASSWORD | sudo -S ./srsue ue_zmq_nearRT.conf; exec bash"
}

# Fonction pour lancer les tests IP
launch_tests0() {
    echo "Lancement de tests."
    gnome-terminal -- bash -c "echo $PASSWORD | sudo -S ip netns exec ue1 ping -i 0.1 10.45.1.1; exec bash"
}
launch_tests1() {
    echo "Lancement de tests.."
    gnome-terminal -- bash -c "echo $PASSWORD | sudo -S ip ro add 10.45.0.0/16 via 10.53.1.2; sudo ip netns exec ue1 ip route add default via 10.45.1.1 dev tun_srsue; exec bash"
}
launch_tests2() {
    echo "Lancement de tests..."
    gnome-terminal -- bash -c "ping -i 0.1 10.45.1.2; exec bash"
}

send_xApps() {	
    echo "Lancement de l'xapp...."
    gnome-terminal -- bash -c "cd ./oran-sc-ric; echo $PASSWORD |sudo -S docker compose exec python_xapp_runner ./kpm_mon_xapp.py --metrics=DRB.UEThpDl,DRB.UEThpUl --kpm_report_style=5; exec bash"
}

# Appel des fonctions
launch_core
sleep 5  # Attendre que le core se lance
launch_ric
sleep 5  # Attendre que le RIC se lance
launch_gnbs
sleep 5  # Attendre que les gNBs se lancent
add_ue_namespaces
sleep 5  # Attendre que les namespaces soient ajoutés
launch_ues
sleep 5  # Attendre que les UEs se lancent
#launch_tests0
sleep 1
launch_tests1
sleep 1
#launch_tests2
sleep 1
#send_xApps
#sleep 1
