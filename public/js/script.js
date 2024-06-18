const imageUpload = document.getElementById('imageUpload');
const previewImage = document.getElementById('previewImage');
const buttonLocation = document.getElementById('locationInputApply');
const feldLocation = document.getElementById('locationInput');

let coordinates = { lat: 37.7749, lng: -122.4194 }; //Test-Koordinaten, werden später durch dynamische Koordinaten ersetzt

/**
 * Event-Listener, ...
 */
buttonLocation.addEventListener('click', () => {
  fetch('http://localhost:5000/image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(coordinates),
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch((error) => console.error('Error:', error));
});

/**
 * Event-Listener, der dafür sorgt, dass das über den Datei-Upload ausgewählte Bild auf der Webseite angezeigt wird.
 * Benötigte DOM-Elemente: imageUpload, previewImage
 */
imageUpload.addEventListener('change', function() {
    const file = this.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', function() {
        previewImage.src = reader.result;
    });

    if (file) {
        reader.readAsDataURL(file);
    }
});

// Initialisierung der Karte
var map = L.map('map').setView([-41.2858, 174.78682], 14);

// Hinzufügen der Tile Layer, gefunden unter https://leaflet-extras.github.io/leaflet-providers/preview/
var satelliteLayer = L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZHdlaXNzd3d1IiwiYSI6ImNsd3oxN2g5dDAyeGwycHF1Z29mYjV5enUifQ.7PQUPuJn6Nzz_tXGsIWdUw', {
	minZoom: 0,
	maxZoom: 20,
	attribution: 'Map data &copy; <a href="https://www.mapbox.com/">Mapbox</a>'
}).addTo(map);

var labelLayer = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{z}/{x}/{y}.png', {
  minZoom: 0,
  maxZoom: 20,
  attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  ext: 'png'
});

var baseMaps = {
  "OpenStreetMap": L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }),
  "Satellite": satelliteLayer
};

var overlayMaps = {
  "Labels": labelLayer
};

// Hinzufügen des Geocoders
L.Control.geocoder().addTo(map);
// Hinzufügen des Satellite Layers und des Label Layers
satelliteLayer.addTo(map);
labelLayer.addTo(map);
// Hinzuügen des Screenshoters
L.simpleMapScreenshoter().addTo(map);
// Hinzufügen der Layer Controls
L.control.layers(baseMaps, overlayMaps).addTo(map);