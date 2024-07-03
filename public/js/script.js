const imageUploadInput = document.getElementById('imageUploadInput');
const socialMediaBild = document.getElementById('socialMediaBild');
const bildUeberKarteButton = document.getElementById('uebereinanderlegenButton');
const bildTransaparenzRegler = document.getElementById('transparenzRegler');
const transparentesBildOverlay = document.getElementById('transparentesBildOverlay');
const tifanzeige = document.getElementById('my-img');
const textInputApplyButton = document.getElementById('textInputApplyButton');
const kartenCoordsApplyButton = document.getElementById('kartenCoordsApplyButton');
const mapUndBildOverlayContainer = document.getElementById('mapUndBildOverlayContainer');
const textInput = document.getElementById('textInput');

let coordinates = { lat: 52.96251, lng: 17.625188 }; //Test-Koordinaten, werden später durch dynamische Koordinaten ersetzt
let mapcoordinates = {minLng: 0, minLat: 0, maxLng: 0, maxLat: 0};
let ueberlagert = false;

kartenCoordsApplyButton.addEventListener('click', () => {
  fetch('http://localhost:5000/imagefrommap', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(mapcoordinates),
  })
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    tifanzeige.src = url;
    mapUndBildOverlayContainer.style.display = 'none';
    //console.log(blob);
    //let durchschnittLat = (mapcoordinates.maxLat + mapcoordinates.minLat) /2;
    //let durchschnittLng = (mapcoordinates.maxLng + mapcoordinates.minLng) /2;
    //let differenceLat = mapcoordinates.maxLat - mapcoordinates.minLat;
    //let differenceLng = mapcoordinates.maxLng - mapcoordinates.minLng;
    let eckenkoordinaten = L.latLngBounds(L.latLng(mapcoordinates.minLat, mapcoordinates.minLng), L.latLng(mapcoordinates.maxLat, mapcoordinates.maxLng));
    map.fitBounds(eckenkoordinaten);
    //console.log("durchschnittLat: ",durchschnittLat, " durchschnittLng: ",durchschnittLng, " differenceLat: ",differenceLat, " differenceLng: ",differenceLng);
    drawnItems.clearLayers();
  })
  .catch((error) => console.error('Error:', error));
  });

/**
 * Event-Listener, der die NLP Analyse des Textes mit Klicken auf den entsprechenden Button ausführt.
 */
textInputApplyButton.addEventListener('click', () => {
  fetch('http://localhost:5000/classify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: textInput.value
    }),
  })
  .then(response => response.json())
  .then(data => {
    const entities = data.entities.map(([start, end, label]) => {
      const entityText = textInput.value.slice(start, end);
      return { text: entityText, label: label };
    });
  
    const poi = entities.find(entity => entity.label === 'POI');
    const stadt = entities.find(entity => entity.label === 'STADT');
    const land = entities.find(entity => entity.label === 'LAND');
  
    let textForGeocode = '';
    if (poi) textForGeocode += poi.text;
    if (stadt) textForGeocode += (textForGeocode ? ', ' : '') + stadt.text;
    if (!poi && !stadt && land) textForGeocode = land.text;

    textForGeocode = removeArticles(textForGeocode);
    console.log('Text for Geocode:', textForGeocode);
  
    return fetch('http://localhost:5000/geocode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: textForGeocode
      }),
    });
  })
  .then(response => response.json())
  .then(data => {
    console.log('Coordinates vor Änderung:', coordinates);
    coordinates = { lat: parseFloat(data.coords.lat), lng: parseFloat(data.coords.lon) };
    console.log('Coordinates nach Änderung:', coordinates);

    return fetch('http://localhost:5000/image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(coordinates),
    });
  })
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    tifanzeige.src = url;
    mapUndBildOverlayContainer.style.display = 'none';
  })
  .catch((error) => {
    console.error('Error:', error);
  });
});

/**
 * Event-Listener, der das Bild über die Karte legt, wenn der Button geklickt wird.
 */
bildUeberKarteButton.addEventListener('click', () => {
  if(ueberlagert == false) {
    transparentesBildOverlay.src = socialMediaBild.src;
    socialMediaBild.style.display = 'none';
    transparentesBildOverlay.style.display = 'block';
    transparentesBildOverlay.style.pointerEvents = 'none'; // Klicks gehen durch das Bild hindurch
    ueberlagert = true;
  }
  else {
    socialMediaBild.style.display = 'block';
    transparentesBildOverlay.style.display = 'none';
    ueberlagert = false;
  }
});

/**
 * Event-Listener, der die Transparenz des über die Karte gelegten Bildes ändert.
 */
bildTransaparenzRegler.addEventListener('change', () => {
  //console.log(bildTransaparenzRegler.value);
  transparentesBildOverlay.style.opacity = bildTransaparenzRegler.value /100;
});
/**
 * Event-Listener, der die Koordinaten an den python Server schickt und ein Earth Engine Bild erstellt und anzeigt.
 */
/** 
buttonLocation.addEventListener('click', () => {
  fetch('http://localhost:5000/image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(coordinates),
  })
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    tifanzeige.src = url;
    mapundoverlay.style.display = 'none';
    //console.log(blob);
  })
  .catch((error) => console.error('Error:', error));
});
*/

/**
 * Event-Listener, der dafür sorgt, dass das über den Datei-Upload ausgewählte Bild auf der Webseite angezeigt wird.
 * Benötigte DOM-Elemente: imageUploadInput, socialMediaBild
 */
imageUploadInput.addEventListener('change', function() {
    const file = this.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', function() {
        socialMediaBild.src = reader.result;
    });

    if (file) {
        reader.readAsDataURL(file);
    }
});

// Initialisierung der Karte
var map = L.map('map').setView([51.505, -0.09], 13);
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

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
  draw: {
    polyline: false,
    polygon: false,
    circle: false,
    marker: false,
    circlemarker: false,
    rectangle: true
  },
  edit: {
    featureGroup: drawnItems
  }
});
map.addControl(drawControl);

map.on('draw:created', function (e) {
  var type = e.layerType,
    layer = e.layer;

  drawnItems.addLayer(layer);

  if (type === 'rectangle') {
    var bounds = layer.getBounds();
    //var topLeft = bounds.getNorthWest();
    var topRight = bounds.getNorthEast();
    var bottomLeft = bounds.getSouthWest();
    //var bottomRight = bounds.getSouthEast();
    mapcoordinates = {minLng: bottomLeft.lng, minLat: bottomLeft.lat, maxLng: topRight.lng, maxLat: topRight.lat};
    //console.log(mapcoordinates);
  }
});

/**
 * Ließt die Koordinaten aus den Eingabefeldern aus und gibt sie als Objekt zurück.
 * @returns Kombinierte Koordinaten aus den Eingabefeldern
 */
function koordinatenAuslesen() {
  let coordinateLat;
  let coordinateLon;
  let combinedCoordinates;
  if(feldLocationLat.value === "" || feldLocationLon.value === "") {
    alert("Bitte geben Sie gültige Koordinaten ein.");
    return;
  }
  else {
  coordinateLat = feldLocationLat.value;
  coordinateLon = feldLocationLon.value;
  combinedCoordinates = { lat: coordinateLat, lng: coordinateLon };
  return combinedCoordinates;
  }
}

/**
 * Entfernt Artikel aus einem Text. Artikel werden nur entfernt, wenn sie alleine stehen (mit Leerzeichen dahinter), das Leerzeichen wird mit entfernt.
 * @param {String} text Text, aus dem die Artikel entfernt werden sollen
 * @returns Text ohne Artikel
 */
function removeArticles(text) {
  const articles = ["der ", "die ", "das ", "ein ", "eine ", "eines ", "einer ", "einem ", "den ", "dem ", "des ", "the ", 
                    "Der ", "Die ", "Das ", "Ein ", "Eine ", "Eines ", "Einer ", "Einem ", "Den ", "Dem ", "Des ", "The "];
  articles.forEach(article => {
      const regex = new RegExp('\\b' + article, 'gi'); // Word boundary to match articles only at word start
      text = text.replace(regex, '');
  });
  return text;
}