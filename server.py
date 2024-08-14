from flask import Flask, request, make_response, send_file, jsonify
from flask_cors import CORS
from osgeo import gdal
from google.oauth2.service_account import Credentials
import ee
import os
import shutil
import requests
import zipfile
import cv2
import subprocess
import numpy as np
import time
import spacy
import warnings
import base64
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)

warnings.filterwarnings("ignore")

# Pfad zur JSON-Datei mit Key
key_file = './credentials/ee-heinich04-1b69aee5f34b.json'
scopes = ['https://www.googleapis.com/auth/earthengine']

# Authentifizierung mit JWT
credentials = Credentials.from_service_account_file(key_file, scopes=scopes)

# Earth Engine initialisieren
ee.Initialize(credentials)

# Trainiertes Modell laden
nlp = spacy.load(r"C:\Users\User\Documents\GitHub\bachelorThesis\trainiertesmodell")

# Funktion zum Registrieren von Bildern
# Quelle: https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html (abgeändert), Zugriff: 22.07.2024
def register_images(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # Sortiere nach Distanz und wähle mehr Übereinstimmungen aus
    matches = sorted(matches, key=lambda x: x.distance)
    best_matches = matches[:100]  # Erhöhe auf 100 für mehr Übereinstimmungen
    
    src_pts = np.float32([kp1[m.queryIdx].pt for m in best_matches]).reshape(-1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in best_matches]).reshape(-1, 2)
    
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    if M is None:
        print("Homographie-Matrix konnte nicht berechnet werden.")
    else:
        print(f"Homographie-Matrix: {M}")
    
    return M


# Funktion zum Warpen eines Bildes
def warp_image(img, M, shape):
    warped_img = cv2.warpPerspective(img, M, (shape[1], shape[0]))
    return warped_img

# Funktion zum Finden des überlappenden Bereichs zwischen zwei Bildern
# Quelle: https://docs.opencv.org/4.x/d3/d05/tutorial_py_table_of_contents_contours.html (abgeändert), Zugriff: 22.07.2024
def find_overlap_area(img1, img2):
    overlap_mask = cv2.bitwise_and(img1, img2)
    overlap_gray = cv2.cvtColor(overlap_mask, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(overlap_gray, 1, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        
        # Validierung der Überlappungsgröße
        img1_h, img1_w = img1.shape[:2]
        img2_h, img2_w = img2.shape[:2]
        
        w = min(w, img1_w - x)
        h = min(h, img1_h - y)
        
        # Sicherstellen, dass Überlappung nicht größer als das Bild ist
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            return None
        
        return x, y, w, h
    else:
        return None

# Funktion zum finden des überlappenden Bereichs zwischen zwei Bildern. Probiert verschiedene Verschiebungen aus
def find_overlap_area_with_adjustments(img1, img2):
    best_overlap = None
    best_overlap_size = 0

    for dx in range(-10, 11, 5):  # Versuche Verschiebungen in x-Richtung
        for dy in range(-10, 11, 5):  # Versuche Verschiebungen in y-Richtung
            img2_shifted = np.roll(img2, shift=(dy, dx), axis=(0, 1))
            overlap_rect = find_overlap_area(img1, img2_shifted)
            
            if overlap_rect:
                x, y, w, h = overlap_rect
                overlap_size = w * h
                if overlap_size > best_overlap_size:
                    best_overlap = overlap_rect
                    best_overlap_size = overlap_size
    
    return best_overlap

# Funktion zum Löschen aller Dateien in einem Verzeichnis
# Quelle: https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder , Zugriff: 22.07.2024
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# Funktion zum Ausführen der Change Detection zwischen zwei Bildern
def run_detect_change(first_image_path, second_image_path, output_directory):
    # Lösche alle Dateien im Ausgabeordner
    clear_directory(output_directory)
    
    # Lade die Bilder
    img1 = cv2.imread(first_image_path)
    img2 = cv2.imread(second_image_path)

    if img1 is None or img2 is None:
        print("Fehler beim Laden der Bilder.")
        return None

    print(f"Original Image1 size: {img1.shape}")
    print(f"Original Image2 size: {img2.shape}")

    # Vorverarbeitung der Bilder
    # Stelle sicher, dass img1 auf img2's Größe skaliert wird, ohne negative oder Null-Dimensionen
    target_size = (img2.shape[1], img2.shape[0])
    img1 = cv2.resize(img1, target_size)
    print(f"Resized Image1 size: {img1.shape}")

    # Registriere die Bilder
    M = register_images(img1, img2)

    if M is None:
        print("Homographie-Matrix konnte nicht berechnet werden.")
        return None

    print(f"Homographie-Matrix: {M}")

    # Warp Image1
    warped_img1 = warp_image(img1, M, img2.shape)
    print(f"Warped Image1 size: {warped_img1.shape}")
    
    # Finde den überlappenden Bereich
    overlap_rect = find_overlap_area_with_adjustments(warped_img1, img2)

    if overlap_rect:
        x, y, w, h = overlap_rect
        print(f"Overlap area: x={x}, y={y}, w={w}, h={h}")

        if w <= 0 or h <= 0:
            print("Ungültiger überlappender Bereich.")
            return None
        
        # Zuschnitt der Bilder
        cropped_img1 = warped_img1[y:y+h, x:x+w]
        cropped_img2 = img2[y:y+h, x:x+w]

        if cropped_img1.size == 0 or cropped_img2.size == 0:
            print("Fehler beim Zuschneiden der Bilder.")
            return None

        print(f"Cropped Image1 size: {cropped_img1.shape}")
        print(f"Cropped Image2 size: {cropped_img2.shape}")

        # Speichere die ausgeschnittenen Bilder temporär
        cropped_img1_path = os.path.join(output_directory, "cropped_image1.png")
        cropped_img2_path = os.path.join(output_directory, "cropped_image2.png")
        cv2.imwrite(cropped_img1_path, cropped_img1)
        cv2.imwrite(cropped_img2_path, cropped_img2)

        # Führe die Change Detection mit den ausgeschnittenen Bildern durch
        detect_change_script = "C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\Change-detection-in-multitemporal-satellite-images-master\\scripts\\DetectChange.py"

        command = [
            "python",
            detect_change_script,
            "-io", cropped_img1_path,
            "-it", cropped_img2_path,
            "-o", output_directory + "\\"
        ]
        
        subprocess.run(command)

        # Hier wird angenommen, dass das Skript eine Datei 'difference.jpg' im output_directory erstellt
        processed_image_path = os.path.join(output_directory, "difference.jpg")

        if not os.path.exists(processed_image_path):
            print("Change Detection hat keine Ausgabedatei erstellt.")
            return None
        stretch_image(processed_image_path, processed_image_path)
        return processed_image_path
    else:
        print("Kein überlappender Bereich gefunden.")
        return None

# Funktion zum Skalieren eines Bildes, um die Seitenverhältnisse beizubehalten
def stretch_image(input_path, output_path):
    # Öffne das Bild
    with Image.open(input_path) as img:
        # Hole die aktuellen Dimensionen
        width, height = img.size
        
        # Erstelle ein neues Bild mit vertauschten Dimensionen
        new_img = Image.new(img.mode, (height, width))
        
        # Berechne das Skalierungsverhältnis
        scale_x = height / width
        scale_y = width / height
        
        # Gehe durch jeden Pixel des neuen Bildes
        for x in range(height):
            for y in range(width):
                # Berechne die entsprechende Position im Originalbild
                orig_x = int(x / scale_x)
                orig_y = int(y / scale_y)
                
                # Kopiere den Pixel
                pixel = img.getpixel((orig_x, orig_y))
                new_img.putpixel((x, y), pixel)
        
        # Speichere das neue Bild
        new_img.save(output_path)


# Funktion zum Geocoden von extrahierten Entitäten (Text -> Koodinaten)
# Nutzt die Nominatim API
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

@app.route('/detectchange', methods=['POST'])
def detect_change():
    try:
        data = request.get_json()
        social_media_bild_data = data['socialMediaBild'].split(",")[1]  # Entfernt den Base64-Header
        satellitenbild_data = data['satellitenbild'].split(",")[1]  # Entfernt den Base64-Header
        date = 1234567
        # Konvertiert Base64 in ein PIL-Bild
        social_media_bild = Image.open(BytesIO(base64.b64decode(social_media_bild_data)))
        satellitenbild = Image.open(BytesIO(base64.b64decode(satellitenbild_data)))

        # Beispiel: Speichern der Bilder (optional)
        social_media_bild.save("social_media_bild.png")
        satellitenbild.save("satellitenbild.png")

        # Antwort (Beispiel)
        output_file_new = run_detect_change(
            "C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\social_media_bild.png",
            "C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\satellitenbild.png",
            "C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\change\\"
        )

        # Bildinhalt als Base64-kodierten String lesen
        with open(output_file_new, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        # JSON-Antwort mit Bildinhalt und Datum erstellen
        response_data = {
            'image': encoded_string,
            'date': date,
            'filename': os.path.basename(output_file_new)
        }
        
        return jsonify(response_data)
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
            # Nominatim gibt eine Liste von Ergebnissen zurück, erstes Ergebnis auswählen
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
        data = request.get_json()
        mapcoordinates = data['coords']
        zeitfuersatellitenbild = data['date']  # Unix-Timestamp
        coords = ee.Geometry.Rectangle([mapcoordinates['minLng'], mapcoordinates['minLat'], mapcoordinates['maxLng'], mapcoordinates['maxLat']])
        maxCloudCover = 20

        # Die Sentinel-2-Bildsammlung laden und filtern
        sentinel2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(coords)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', maxCloudCover))
            .filter(ee.Filter.date(datetime.utcfromtimestamp(zeitfuersatellitenbild / 1000) - timedelta(days=30),
                                   datetime.utcfromtimestamp(zeitfuersatellitenbild / 1000) + timedelta(days=30)))
            .map(lambda image: image.set('time_diff', ee.Number(image.get('system:time_start')).subtract(zeitfuersatellitenbild).abs()))
            .sort('time_diff'))

        # Das Bild auswählen, das dem gegebenen Datum am nächsten ist
        image = sentinel2.first()

        if image is None:
            raise Exception("Kein Bild gefunden für die angegebenen Parameter.")

        date = image.get('system:time_start').getInfo()

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
        output_file_base = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\mergedtif'

        # Den Unix-Timestamp hinzufügen
        timestamp = str(date)

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

        # Bildinhalt als Base64-kodierten String lesen
        with open(output_file_new, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        # JSON-Antwort mit Bildinhalt und Datum erstellen
        response_data = {
            'image': encoded_string,
            'date': date,
            'filename': os.path.basename(output_file_new)
        }
        
        return jsonify(response_data)

    except Exception as e:
        app.logger.exception(e)
        return str(e), 500

# Route, die in script.js mit Koordinaten des in der Leaflet Map gezeichneten Rechtecks aufgerufen wird und ein TIF und ein PNG der entsprechenden Region erstellt
# Spezial-Route nur für NAIP-Bilder (USA)
@app.route('/imagefrommapusaonly', methods=['POST'])
def get_image_from_map_usa_only():
    try:
        # Koordinaten und Parameter festlegen
        data = request.get_json()
        mapcoordinates = data['coords']
        coords = ee.Geometry.Rectangle([mapcoordinates['minLng'], mapcoordinates['minLat'], mapcoordinates['maxLng'], mapcoordinates['maxLat']])
        #maxCloudCover = 20
        #bufferSize = 4000
        # Die NAIP/DOQQ - Bildsammlung laden
        naipdoqq = (ee.ImageCollection("USDA/NAIP/DOQQ")
            .filterBounds(coords)
            .filter(ee.Filter.date('2020-01-01', '2024-12-31'))
            .sort('system:index', False))

        # Das neueste Bild auswählen
        image = naipdoqq.first()
        date = image.get('system:time_start').getInfo()

        # Ein rechteckiges Gebiet um den Punkt erstellen
        region = coords.bounds()

        # RGB-Bänder auswählen und auf das rechteckige Gebiet zuschneiden
        rgbImage = image.select(['R', 'G', 'B']).clip(region)

        # Eine Download-URL für das Bild generieren
        url = rgbImage.getDownloadUrl({
            'scale': 2,
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
        tif_files = ['C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\R.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\G.tif', 
                    'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B.tif']

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
            time.sleep(1)  # 1 Sekunde warten zwischen den Überprüfungen

        # Das TIF in PNG umwandeln mithilfe von gdal_translate
        gdal_translate = 'C:\\Program Files\\GDAL\\gdal_translate.exe'
        input_file_new = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif'

        # Basis-Output-Dateiname
        output_file_base = 'C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\mergedtif'

        # Den Unix-Timestamp hinzufügen
        timestamp = str(date)

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
        
        command = [gdal_translate, '-ot', 'Byte', '-scale', '-of', 'PNG', '-b', '1', '-b', '2', '-b', '3', input_file_new, output_file_new]

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
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\R.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\G.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\B.tif')
        os.remove('C:\\Users\\User\\Documents\\GitHub\\bachelorThesis\\public\\tifs\\merged.tif')

        # Bildinhalt als Base64-kodierten String lesen
        with open(output_file_new, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        # JSON-Antwort mit Bildinhalt und Datum erstellen
        response_data = {
            'image': encoded_string,
            'date': date,
            'filename': os.path.basename(output_file_new)
        }
        
        return jsonify(response_data)
    except Exception as e:
        app.logger.exception(e)
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)