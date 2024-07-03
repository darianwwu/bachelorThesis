const imageUpload = document.getElementById('imageUpload');
const previewImage = document.getElementById('previewImage');
const buttonLocation = document.getElementById('locationInputApply');
const feldLocationLat = document.getElementById('locationInputLat');
const feldLocationLon = document.getElementById('locationInputLon');
const bildUeberKarteButton = document.getElementById('uebereinanderlegenButton');
const bildTransaparenzRegler = document.getElementById('transparenzRegler');
const bildDuplikatTransparenz = document.getElementById('transparentesOverlay');
const tifanzeige = document.getElementById('my-img');
const textNLPButton = document.getElementById('textInputApply');
const kartenCoordsButton = document.getElementById('kartenCoordsApply');

let coordinates = { lat: 52.96251, lng: 17.625188 }; //Test-Koordinaten, werden später durch dynamische Koordinaten ersetzt
let mapcoordinates = {minLng: 0, minLat: 0, maxLng: 0, maxLat: 0};
let inputtext = "Das Atomium in Brüssel Belgien ist ein sehr interessantes Bauwerk, hier its ien Bild davon.";
let ueberlagert = false;
let entitaetenarray = [];

kartenCoordsButton.addEventListener('click', () => {
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
    const tifanzeige = document.getElementById('my-img');
    tifanzeige.src = url;
    console.log(blob);
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
textNLPButton.addEventListener('click', () => {
  fetch('http://localhost:5000/classify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: inputtext
    }),
  })
  .then(response => response.json())
  .then(data => {
    // Extrahiere und formatiere die Entitäten basierend auf den Indizes und Labels in `data`
    const entities = data.entities.map(([start, end, label]) => {
      // Extrahiere den Text der Entität basierend auf den Start- und Endindizes
      const entityText = inputtext.slice(start, end);
      // Erstelle ein Tupel aus dem Text der Entität und dem Label
      return { text: entityText, label: label };
    });
  
    // Finde POI, STADT, und LAND in den Entitäten
    const poi = entities.find(entity => entity.label === 'POI');
    const stadt = entities.find(entity => entity.label === 'STADT');
    const land = entities.find(entity => entity.label === 'LAND');
  
    // Zusammenstellen des Textes basierend auf den verfügbaren Informationen
    let textForGeocode = '';
    //let testtextGeoCode = 'Atomium, Brüssel';
    if (poi) textForGeocode += poi.text;
    if (stadt) textForGeocode += (textForGeocode ? ', ' : '') + stadt.text;
    if (!poi && !stadt && land) textForGeocode = land.text; // Nur LAND, wenn weder POI noch STADT vorhanden sind

    // Entfernen der Artikel
    textForGeocode = removeArticles(textForGeocode);
    console.log('Text for Geocode:', textForGeocode);
  
    // Führe die POST-Anfrage mit dem zusammengestellten Text aus
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
    // Verarbeite die Antwort der /geocode Route
    //console.log('Coordinates vor Änderung:', coordinates);
    //console.log('Geocode Data:', data);
    coordinates= { lat: parseFloat(data.coords.lat), lng: parseFloat(data.coords.lon) };
    console.log('Coordinates nach Änderung:', coordinates);
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
    bildDuplikatTransparenz.src = previewImage.src;
    previewImage.style.display = 'none';
    bildDuplikatTransparenz.style.display = 'block';
    bildDuplikatTransparenz.style.pointerEvents = 'none'; // Klicks gehen durch das Bild hindurch
    ueberlagert = true;
  }
  else {
    previewImage.style.display = 'block';
    bildDuplikatTransparenz.style.display = 'none';
    ueberlagert = false;
  }
});

/**
 * Event-Listener, der die Transparenz des über die Karte gelegten Bildes ändert.
 */
bildTransaparenzRegler.addEventListener('change', () => {
  console.log(bildTransaparenzRegler.value);
  bildDuplikatTransparenz.style.opacity = bildTransaparenzRegler.value /100;
});
/**
 * Event-Listener, der die Koordinaten an den python Server schickt und ein Earth Engine Bild erstellt und anzeigt.
 */
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
    const tifanzeige = document.getElementById('my-img');
    tifanzeige.src = url;
    console.log(blob);
  })
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
    console.log(mapcoordinates);
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