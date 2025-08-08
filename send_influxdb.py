"""
Description: This script monitors several CSV files for modifications 
and sends the extracted metrics to an InfluxDB database. It uses the 
`watchdog` library to observe changes in the files and processes the data in real time 
using threads and a queue.

Key features:
- Monitors multiple CSV files for changes.
- Extraction of columns and conversion of values into appropriate types (integers, floats, etc.).
- Aggregate metrics and add information about the data source.
- Send processed data to InfluxDB via its client API.
- Simultaneous management of files and database connections using threads.

Prerequisites:
- Install the necessary libraries (`watchdog`, `influxdb_client`, etc.).
- Configure the access information for your InfluxDB instance (URL, token, organisation, bucket).
- Ensure that the CSV files to be monitored exist in the specified paths.

Important note: 
- The number of CSV files monitored (number of SUs) corresponds to the number of paths specified in the `file_paths` list. 
To monitor more or fewer files, modify this list by adding or removing file paths.
Ensure that each file corresponds to the processing requirements (CSV format).

"""






import argparse
import json
import logging
import signal
import socket
import os
from contextlib import suppress
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Any, Dict, Optional, Tuple

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from influxdb_client import InfluxDBClient, WriteApi
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration InfluxDB
bucket = "srsran1" #"srsran11"
org = "srs1"
token = "U6PQI4mNkJEc-ZFA55AN82uzXIcGUADBPTMBpRW2bT5faYDQSMP2GRX1cht0URLvfi96b-iD6OvvB5ZDNzgdTA=="   #"605bc59413b7d5457d181ccf20f9fda15693f81b068d70396cc183081b264fbb"
url = "http://localhost:8087"  # ou l'URL de ton instance InfluxDB
username = "admin1"
password = "admin12345"


class FileWatcherHandler(FileSystemEventHandler):
    def __init__(self, file_path, queue, source_name):
        self.file_path = file_path # Initialise un gestionnaire pour surveiller les modifications du fichier.
        self.queue = queue
        self.source_name = source_name
        self.last_position = 0
        self.columns = []
        self.partial_data = {}

    def on_modified(self, event):
        """
        Gère les modifications apportées au fichier surveillé.
        """
        if event.src_path == self.file_path:
            with open(self.file_path, 'r') as file:
                file.seek(self.last_position)
                lines = file.readlines()
                self.last_position = file.tell()

            if lines:
                for line in lines:
                    # Lecture des colonnes depuis la première ligne si elles ne sont pas encore initialisées
                    if not self.columns:
                        self.columns = line.strip().split(';')
                    else:
                        fields = line.strip().split(';')
                        data_dict = {col: self._convert_value(val) for col, val in zip(self.columns, fields) if val}

                        # Mise à jour des données partielles
                        self.partial_data.update(data_dict)

                        # Si toutes les métriques sont présentes, mettre à jour la file d'attente
                        if all(metric in self.partial_data for metric in self.columns):
                            self.partial_data["source"] = self.source_name  # Ajout de la source
                            self.queue.put((self.partial_data.copy(), self.columns))
                            self.partial_data.clear()  # Réinitialiser les données partielles

    def _convert_value(self, value):
        # Convertir les valeurs en leur type approprié
        if value.lower() == 'n/a':
            return None
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

def send_to_influxdb(client, bucket, queue):
    """
    Envoie les données extraites à InfluxDB.
    """
    write_api = client.write_api(write_options=SYNCHRONOUS)
    while True:
        item = queue.get()
        if item is None:
            break

        data_dict, columns = item
        point = {
            "measurement": "ue_metrics",
            "tags": {
                "source": data_dict.pop("source")
            },
            "fields": {},
        }

        for key in ['dl_bler', 'ul_bler', 'dl_brate', 'ul_brate','rsrp']:
            if key in data_dict:
                value = data_dict[key]
                if isinstance(value, int):
                    value = float(value)
                point["fields"][key] = value

        logging.info(f"Point envoyé à InfluxDB : {point}")
        write_api.write(bucket=bucket, org=org, record=point)
        #logging.info(f"DataDict : {data_dict}")

def recreate_bucket(client: InfluxDBClient, bucket_name: str) -> None:
    """
    Supprime et recrée le bucket spécifié dans InfluxDB.
    """
    logging.info("Recreating the bucket")
    api = client.buckets_api()
    bucket_ref = api.find_bucket_by_name(bucket_name)
    if bucket_ref:
        api.delete_bucket(bucket_ref)
    api.create_bucket(bucket_name)
    logging.info("Bucket cleaned")

def main():
    # Liste des chemins de fichiers à surveiller
    file_paths = ["/tmp/ue1_metrics.csv", "/tmp/ue2_metrics.csv", "/tmp/ue3_metrics.csv","/tmp/ue4_metrics.csv"]
    log_level = logging.INFO
    clean_bucket = False
    
    # Connexion au client InfluxDB
    client = InfluxDBClient(url=url, token=token, org=org, username=username, password=password)

    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=log_level)
    logging.info("Starting file watcher")

    if clean_bucket:
        recreate_bucket(client, bucket)

    queue_obj = Queue()

    observers = []
    threads = []
    
    # Initialisation des gestionnaires pour chaque fichier
    for i, file_path in enumerate(file_paths):
        source_name = f"ue{i+1}"
        file_watcher_handler = FileWatcherHandler(file_path, queue_obj, source_name)
        observer = Observer()
        observer.schedule(file_watcher_handler, path=os.path.dirname(file_path), recursive=False)
        observers.append(observer)

        thread = Thread(target=send_to_influxdb, args=(client, bucket, queue_obj))
        threads.append(thread)
    
    # Démarrer les observateurs
    for observer in observers:
        observer.start()

    def close():
        """
        Arrête les threads et observateurs proprement.
        """
        logging.info("Closing")
        queue_obj.put(None)
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
    
    # Gestion des signaux pour arrêter le script proprement
    signal.signal(signal.SIGINT, lambda signum, frame: close())
    signal.signal(signal.SIGTERM, lambda signum, frame: close())
    
    # Démarrer les threads 
    for thread in threads:
        thread.start()

    for observer in observers:
        observer.join()
    for thread in threads:
        thread.join()
    logging.info("End")

if __name__ == "__main__":
    main()

