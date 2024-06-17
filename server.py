from flask import Flask
import ee
from google.oauth2.service_account import Credentials

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)