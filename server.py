from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from osgeo import gdal
from skimage import io, filters, feature
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from google.oauth2.service_account import Credentials
from PIL import Image, ImageChops, ImageEnhance
from collections import Counter
from scipy.stats import entropy
from scipy.fftpack import dct
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import numpy as np
import cv2
import ee
import os
import shutil
import requests
import zipfile
import subprocess
import time
import spacy
import geocoder
import tweepy
import torch
import warnings
import torchvision.transforms as transforms
from torchvision.models import resnet50
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

app = Flask(__name__)
CORS(app)

warnings.filterwarnings("ignore")

# Pfad zur JSON-Datei mit Key
key_file = './credentials/ee-heinich04-805b2e12705e.json'
scopes = ['https://www.googleapis.com/auth/earthengine']
#api_key = 'AIzaSyB5OacCI7Nt76RIUn0qeyoGMKhFBdEWUaU'

# Authentifizierung mit JWT
credentials = Credentials.from_service_account_file(key_file, scopes=scopes)

# Earth Engine initialisieren
ee.Initialize(credentials)

# Trainiertes Modell laden
nlp = spacy.load(r"C:\Users\User\Documents\GitHub\bachelorThesis\trainiertesmodell")

# Funktion zum Geocoden von extrahierten Entitäten (Text -> Koodinaten)
def geocode_address(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'Bachelor Thesis localhost (dweiss1@uni-muenster.de)'
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {}


# Basis-Route
@app.route('/')
def hello_world():
    return 'Earth Engine initialized successfully.'

# Metadaten-Route
@app.route('/metadata')
def get_metadata():
    # Abrufen der Metadaten eines Bildes (Beispielaufruf)
    image = ee.Image('LANDSAT/LC08/C01/T1/LC08_044034_20140318')
    info = image.getInfo()
    return info

# Route, die in script.js mit dem Text aus dem Social Media Post aufgerufen wird und die relevanten Entitäten für das Geocoding extrahiert
@app.route('/classify', methods=['POST'])
def classify_text():
    try:
        # Text aus der Anfrage abrufen
        data = request.get_json()
        text = data['text']
        print('text classify:', text)
        # Text mit dem Modell verarbeiten
        doc = nlp(text)

        # Entitäten extrahieren
        entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        print(entities)
        return {'entities': entities}
    except Exception as e:
        app.logger.exception(e)
        return str(e), 500

# Route, die in script.js mit den extrahierten Entitäten aus dem Text aufgerufen wird und die entsprechenden Koordinaten zurückgibt (Geocoding)
@app.route('/geocode', methods=['POST'])
def geocode():
    try:
        data = request.get_json()
        text = data['text']
        print('text geocode:', text)
        result = geocode_address(text)
        if result:
            # Nominatim gibt eine Liste von Ergebnissen zurück; wir nehmen das erste
            first_result = result[0]
            coords = {
                'lat': first_result['lat'],
                'lon': first_result['lon']
            }
            return jsonify({'coords': coords})
        else:
            return jsonify({'error': 'Keine Ergebnisse gefunden'}), 404
    except Exception as e:
        app.logger.exception(e)
        return str(e), 500

# Route, die in script.js mit Koordinaten des in der Leaflet Map gezeichneten Rechtecks aufgerufen wird und ein TIF und ein PNG der entsprechenden Region erstellt
@app.route('/imagefrommap', methods=['POST'])
def get_image_from_map():
    try:
        # Koordinaten und Parameter festlegen
        mapcoordinates = request.get_json()
        coords = ee.Geometry.Rectangle([mapcoordinates['minLng'], mapcoordinates['minLat'], mapcoordinates['maxLng'], mapcoordinates['maxLat']])
        maxCloudCover = 10
        #bufferSize = 4000
        # Die Sentinel-2-Bildsammlung laden
        sentinel2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(coords)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', maxCloudCover))
            .sort('system:time_start', False))

        # Das neueste Bild auswählen
        #TODO: Zeitlichen Aspekt berücksichtigen
        image = sentinel2.first()

        # Ein rechteckiges Gebiet um den Punkt erstellen
        region = coords.bounds()

        # RGB-Bänder auswählen und auf das rechteckige Gebiet zuschneiden
        rgbImage = image.select(['B4', 'B3', 'B2']).clip(region)

        # Eine Download-URL für das Bild generieren
        url = rgbImage.getDownloadUrl({
            'scale': 10,
            'crs': 'EPSG:4326',
            'region': region.getInfo()['coordinates'],
            'fileFormat': 'GeoTIFF'
        })
        
        # Das Bild herunterladen
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")

        # Die ZIP-Datei als temporäre Datei speichern
        zip_file_name = 'image.zip'
        with open(zip_file_name, 'wb') as f:
            f.write(response.content)

        # Die ZIP-Datei entpacken
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall('.')

        # Die TIF-Dateien durchlaufen und verschieben
        tif_files = []
        tifs_directory = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs'

        if not os.path.exists(tifs_directory):
            os.makedirs(tifs_directory)

        for tif_file_name in os.listdir('.'):
            if tif_file_name.endswith('.tif'):
                current_path = os.path.join(os.getcwd(), tif_file_name)
                band_name = tif_file_name.split('.')[-2].split('_')[-1]
                new_file_name = f"{band_name}.tif"
                new_path = os.path.join(tifs_directory, new_file_name)
                shutil.move(current_path, new_path)

        # Die TIF-Dateien zu einer einzigen Datei zusammenführen
        python_exe = 'C:\\Users\\User\\anaconda3\\python.exe'
        gdal_merge = 'C:\\Users\\User\\anaconda3\\Scripts\\gdal_merge.py'
        output_file = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif'
        tif_files = ['C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B4.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B3.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B2.tif']

        command = [python_exe, gdal_merge, '-init', '255', '-o', output_file, '-separate'] + tif_files

        try:
            result = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Ausgabe:", result.stdout.decode())
            print("Fehlerausgabe:", result.stderr.decode())
        except subprocess.CalledProcessError as e:
            print("Fehler beim Ausführen von gdal_merge:", e)
            print("Befehl:", ' '.join(command))
            print("Fehlerausgabe:", e.stderr.decode())
            raise

        # Warten, bis die Datei existiert und ihre Größe sich nicht mehr ändert
        old_file_size = 0
        while not os.path.isfile(output_file) or old_file_size != os.path.getsize(output_file):
            print("Warten auf die Erstellung der Datei...")
            old_file_size = os.path.getsize(output_file) if os.path.isfile(output_file) else 0
            time.sleep(1)  # Warten Sie 1 Sekunde zwischen den Überprüfungen

        # Das TIF in PNG umwandeln mithilfe von gdal_translate
        gdal_translate = 'C:\\Program Files\\GDAL\\gdal_translate.exe'
        input_file_new = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif'

        # Basis-Output-Dateiname
        output_file_base = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\mergedtif.png'

        # Überprüfen, ob die Datei bereits existiert
        if os.path.exists(output_file_base):
            # Falls die Datei existiert, eine neue Nummer suchen
            count = 1
            while True:
                # Neuen Dateinamen erstellen
                output_file_new = f'{output_file_base[:-4]}{count}.png'
                if not os.path.exists(output_file_new):
                    break
                count += 1
        else:
            # Falls die Datei nicht existiert, den ursprünglichen Dateinamen verwenden
            output_file_new = output_file_base
        
        command = [gdal_translate, '-ot', 'Byte', '-scale', '0', '3000', '0', '255', '-of', 'PNG', '-b', '1', '-b', '2', '-b', '3', input_file_new, output_file_new]

        try:
            result = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Ausgabe:", result.stdout.decode())
            print("Fehlerausgabe:", result.stderr.decode())
        except subprocess.CalledProcessError as e:
            print("Fehler beim Ausführen von gdal_translate:", e)
            print("Befehl:", ' '.join(command))
            print("Fehlerausgabe:", e.stderr.decode())
            raise

        # Nicht mehr benötigte Dateien löschen
        os.remove(zip_file_name)
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B4.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B3.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B2.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif')

        # Das PNG-Bild zurückgeben
        return send_file(output_file_new, mimetype='image/png')
    except Exception as e:
        app.logger.exception(e)
        return str(e), 500
    
#Route, die in script.js mit aus dem Text estrahierten Koordinaten aufgerufen wird und ein TIF und ein PNG der entsprechenden Region erstellt
@app.route('/image', methods=['POST'])
def get_image():
    try:
        # Koordinaten und Parameter festlegen
        coordinates = request.get_json()
        coords = ee.Geometry.Point([coordinates['lng'], coordinates['lat']])
        maxCloudCover = 10
        bufferSize = 4000

        # Die Sentinel-2-Bildsammlung laden
        sentinel2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(coords)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', maxCloudCover))
            .sort('system:time_start', False))

        # Das neueste Bild auswählen
        #TODO: Zeitlichen Aspekt berücksichtigen
        image = sentinel2.first()

        # Ein rechteckiges Gebiet um den Punkt erstellen
        region = coords.buffer(bufferSize).bounds()

        # RGB-Bänder auswählen und auf das rechteckige Gebiet zuschneiden
        rgbImage = image.select(['B4', 'B3', 'B2']).clip(region)

        # Eine Download-URL für das Bild generieren
        url = rgbImage.getDownloadUrl({
            'scale': 10,
            'crs': 'EPSG:4326',
            'region': region.getInfo()['coordinates'],
            'fileFormat': 'GeoTIFF'
        })
        
        # Das Bild herunterladen
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Request failed with status {response.status_code}")

        # Die ZIP-Datei als temporäre Datei speichern
        zip_file_name = 'image.zip'
        with open(zip_file_name, 'wb') as f:
            f.write(response.content)

        # Die ZIP-Datei entpacken
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall('.')

        # Die TIF-Dateien durchlaufen und verschieben
        tif_files = []
        tifs_directory = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs'

        if not os.path.exists(tifs_directory):
            os.makedirs(tifs_directory)

        for tif_file_name in os.listdir('.'):
            if tif_file_name.endswith('.tif'):
                current_path = os.path.join(os.getcwd(), tif_file_name)
                band_name = tif_file_name.split('.')[-2].split('_')[-1]
                new_file_name = f"{band_name}.tif"
                new_path = os.path.join(tifs_directory, new_file_name)
                shutil.move(current_path, new_path)

        # Die TIF-Dateien zu einer einzigen Datei zusammenführen
        python_exe = 'C:\\Users\\User\\anaconda3\\python.exe'
        gdal_merge = 'C:\\Users\\User\\anaconda3\\Scripts\\gdal_merge.py'
        output_file = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif'
        tif_files = ['C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B4.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B3.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B2.tif']

        command = [python_exe, gdal_merge, '-init', '255', '-o', output_file, '-separate'] + tif_files

        try:
            result = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Ausgabe:", result.stdout.decode())
            print("Fehlerausgabe:", result.stderr.decode())
        except subprocess.CalledProcessError as e:
            print("Fehler beim Ausführen von gdal_merge:", e)
            print("Befehl:", ' '.join(command))
            print("Fehlerausgabe:", e.stderr.decode())
            raise

        # Warten, bis die Datei existiert und ihre Größe sich nicht mehr ändert
        old_file_size = 0
        while not os.path.isfile(output_file) or old_file_size != os.path.getsize(output_file):
            print("Warten auf die Erstellung der Datei...")
            old_file_size = os.path.getsize(output_file) if os.path.isfile(output_file) else 0
            time.sleep(1)  # Warten Sie 1 Sekunde zwischen den Überprüfungen

        # Das TIF in PNG umwandeln mithilfe von gdal_translate
        gdal_translate = 'C:\\Program Files\\GDAL\\gdal_translate.exe'
        input_file_new = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif'

        # Basis-Output-Dateiname
        output_file_base = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\mergedtif.png'

        # Überprüfen, ob die Datei bereits existiert
        if os.path.exists(output_file_base):
            # Falls die Datei existiert, eine neue Nummer suchen
            count = 1
            while True:
                # Neuen Dateinamen erstellen
                output_file_new = f'{output_file_base[:-4]}{count}.png'
                if not os.path.exists(output_file_new):
                    break
                count += 1
        else:
            # Falls die Datei nicht existiert, den ursprünglichen Dateinamen verwenden
            output_file_new = output_file_base
        
        command = [gdal_translate, '-ot', 'Byte', '-scale', '0', '3000', '0', '255', '-of', 'PNG', '-b', '1', '-b', '2', '-b', '3', input_file_new, output_file_new]

        try:
            result = subprocess.run(command, shell=False, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Ausgabe:", result.stdout.decode())
            print("Fehlerausgabe:", result.stderr.decode())
        except subprocess.CalledProcessError as e:
            print("Fehler beim Ausführen von gdal_translate:", e)
            print("Befehl:", ' '.join(command))
            print("Fehlerausgabe:", e.stderr.decode())
            raise

        # Nicht mehr benötigte Dateien löschen
        os.remove(zip_file_name)
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B4.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B3.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B2.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif')

        # Das PNG-Bild zurückgeben
        return send_file(output_file_new, mimetype='image/png')
    except Exception as e:
        app.logger.exception(e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)