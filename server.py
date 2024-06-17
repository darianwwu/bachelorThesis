from flask import Flask
from flask_cors import CORS
from flask import request
import ee
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)
# Pfad zur JSON-Datei mit Key
key_file = './credentials/ee-heinich04-805b2e12705e.json'
scopes = ['https://www.googleapis.com/auth/earthengine']

# Authentifizierung mit JWT
credentials = Credentials.from_service_account_file(key_file, scopes=scopes)

# Earth Engine initialisieren
ee.Initialize(credentials)

@app.route('/')
def hello_world():
    return 'Earth Engine initialized successfully.'

@app.route('/metadata')
def get_metadata():
    # Abrufen der Metadaten eines Bildes (Beispielaufruf)
    image = ee.Image('LANDSAT/LC08/C01/T1/LC08_044034_20140318')
    info = image.getInfo()
    return info

@app.route('/image', methods=['POST'])
def get_image():
    # Koordinaten aus der Anfrage extrahieren
    coordinates = request.get_json()

    # Ein Satellitenbild anhand der Koordinaten abrufen
    image = (ee.ImageCollection('LANDSAT/LC08/C01/T1')
        .filterBounds(ee.Geometry.Point([coordinates['lng'], coordinates['lat']]))
        .first())

    # Die Metadaten des Bildes abrufen
    info = image.getInfo()

    return info

if __name__ == '__main__':
    app.run(debug=True)