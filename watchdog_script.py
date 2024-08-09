import os
import requests
from requests.auth import HTTPBasicAuth
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

# Lade die Konfigurationsdaten aus der config.json
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
username = config['flask']['username']
password_clear = config['flask']['password_clear']  # Passwort im Klartext

# API Credentials
auth = HTTPBasicAuth(username, password_clear)
base_url = 'http://127.0.0.1:5000/api/sounds'

# Funktion zum Hinzufügen eines Sounds
def add_sound(file_name):
    data = {
        "name": os.path.splitext(file_name)[0],  # Name ohne Dateiendung
        "path": f"sounds/{file_name}"
    }
    response = requests.post(f'{base_url}/add', json=data, auth=auth)
    print(f'Added: {data["name"]}', response.json())

# Funktion zum Entfernen eines Sounds
def remove_sound(file_name):
    data = {
        "name": os.path.splitext(file_name)[0]  # Name ohne Dateiendung
    }
    response = requests.post(f'{base_url}/remove', json=data, auth=auth)
    print(f'Removed: {data["name"]}', response.json())

# Event-Handler für Dateiänderungen
class SoundEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            add_sound(os.path.basename(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            remove_sound(os.path.basename(event.src_path))

# Hauptfunktion
if __name__ == "__main__":
    path = "./sounds"
    event_handler = SoundEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print(f"Watching directory: {path}")
    
    try:
        while True:
            # Hier könnten weitere Operationen durchgeführt werden, wenn nötig
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
