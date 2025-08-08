"""

Description: This script monitors a specified CSV file and adds a timestamp for each new line added. 
The timestamped data is written to an output file. This is useful for tracking changes 
on the input file.

Main features:
- Monitor changes to a CSV file using the `watchdog` library.
- Automatically adds a timestamp for each new line detected.

Prerequisite:
- The `watchdog` library installed (`pip install watchdog`).
- Valid paths for input and output files.

"""



import time
import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class ObservateurFichier(FileSystemEventHandler):
    def __init__(self, chemin_fichier, fichier_sortie):
        # Initialisation de l'observateur pour surveiller un fichier spécifique.
        self.chemin_fichier = chemin_fichier
        self.fichier_sortie = fichier_sortie
        self.derniere_position = 0  # Position pour continuer la lecture du fichier
        self.premiere_ligne = True  # Indicateur pour la première ligne
        """
        Method called when the file being monitored is modified.
        : param event: Modification event detected by watchdog.
        """
    def on_modified(self, event):

        if event.src_path == self.chemin_fichier:
            with open(self.chemin_fichier, 'r') as fichier:
                fichier.seek(self.derniere_position)
                lignes = fichier.readlines()
                self.derniere_position = fichier.tell()

            if lignes:
                for ligne in lignes:
                    # Vérifier si c'est la première ligne écrite dans le fichier de sortie
                    if self.premiere_ligne:
                        contenu = f"timestampss;{ligne.strip()}\n"
                        self.premiere_ligne = False  # Marquer que la première ligne a été écrite
                    else:
                        # Utiliser l'horodatage réel pour les lignes suivantes
                        horodatage = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        contenu = f"{horodatage};{ligne.strip()}\n"

                    with open(self.fichier_sortie, 'a') as fichier_sortie:
                        fichier_sortie.write(contenu)

if __name__ == "__main__":
    chemin_fichier = "/tmp/ue1_metrics.csv"
    fichier_sortie = "/home/rufus/srsran_projet/metrics_timestamp.csv"

    # Supprimer le fichier de sortie s'il existe déjà
    if os.path.exists(fichier_sortie):
        os.remove(fichier_sortie)

    # Vérifier que le fichier d'entrée existe
    if os.path.exists(chemin_fichier):
        gestionnaire_evenement = ObservateurFichier(chemin_fichier, fichier_sortie)
        observateur = Observer()
        observateur.schedule(gestionnaire_evenement, path=chemin_fichier, recursive=False)
        observateur.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observateur.stop()
        observateur.join()
    else:
        print(f"Erreur : Le fichier {chemin_fichier} n'existe pas.")

