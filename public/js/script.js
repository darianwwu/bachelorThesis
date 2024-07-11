const socialMediaBild = document.getElementById('socialMediaBild'); // Bild-Element zum Anzeigen des hochgeladenen Satellitenbild von Social Media
const bildUeberKarteButton = document.getElementById('uebereinanderlegenButton'); // Button zum Überlagern des Satellitenbildes von Social Media über die Karte
const bildTransaparenzRegler = document.getElementById('transparenzRegler'); // Regler zum Einstellen der Transparenz des über die Karte gelegten Bildes
const transparentesBildOverlay = document.getElementById('transparentesBildOverlay'); // Bild-Element zum Anzeigen des über die Karte gelegten Bildes
const satellitenbildEarthEngine = document.getElementById('satellitenbildEarthEngine'); // Bild-Element zum Anzeigen des Satellitenbildes von Earth Engine
const textInputApplyButton = document.getElementById('textInputApplyButton'); // Button zum Anwenden der NLP Analyse auf den eingegebenen Text und dem Erstellen eines Satellitenbilds an entsprechender Stelle
const kartenCoordsApplyButton = document.getElementById('kartenCoordsApplyButton'); // Button zum Erstellen eines Satellitenbilds mit den Koordinaten des auf der Karte gezeichneten Rechtecks
const mapUndBildOverlayContainer = document.getElementById('mapUndBildOverlayContainer'); // Container für die Karte und das (transparente) Bild Overlay
const textInput = document.getElementById('textInput'); // Text-Input-Feld für die Eingabe des zu analysierenden Textes eines Social Media Posts
const satellitenbildDatum  = document.getElementById('satellitenbildDatum '); // Text-Element für das Datum des Satellitenbildes
let coordinates = {lat: 0, lng: 0};
let mapcoordinates = {minLng: 0, minLat: 0, maxLng: 0, maxLat: 0};
let ueberlagert = false;

/**
 * Event-Listener, der den eingegebenen Text analysiert und die gefundenen Entitäten an den Geocoding-Service sendet, um die Koordinaten zu ermitteln und die Leaflet Map entsprechend zu zentrieren.
 */
textInputApplyButton.addEventListener('click', () => {
  let abschicktext = removeSpecialCharacters(textInput.value);
  console.log('Abschicktext:', abschicktext);
  
  fetch('http://localhost:5000/classify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: abschicktext
    }),
  })
  .then(response => response.json())
  .then(data => {
    const entities = data.entities.map(([start, end, label]) => {
      const entityText = abschicktext.slice(start, end);
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
    // Zoomen auf die gefundenen Koordinaten
    let eckenkoordinaten = L.latLngBounds(L.latLng(coordinates.lat, coordinates.lng), L.latLng(coordinates.lat, coordinates.lng));
    map.fitBounds(eckenkoordinaten);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
});

/**
 * Event-Listener, der das in der Zwischenablage befindliche Bild auf der Webseite anzeigt, wenn ein Bild aus der Zwischenablage mittels Strg+V auf die Seite kopiert wird.
 */
document.addEventListener('paste', (event) => {
  const items = event.clipboardData.items;
  for (const item of items) {
      if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          const reader = new FileReader();
          reader.onload = (event) => {
              const imgElement = socialMediaBild;
              imgElement.src = event.target.result;
              imgElement.style.display = 'block';
          };
          reader.readAsDataURL(file);
      }
  }
});

/**
 * Event-Listener, der das in der Leaflet Map gezeichnete Rechteck ausliest und mit dessen Koordinaten ein Earth Engine Bild anzeigt, wenn der Button geklickt wird.
 * Es wird zwischen Bereichen, die innerhalb der USA und außerhalb der USA liegen, unterschieden.
 */
kartenCoordsApplyButton.addEventListener('click', () => {
  function isWithinUSA(coords) {
    const usaBounds = {
      minLat: 24.7433195,
      maxLat: 49.3457868,
      minLng: -124.7844079,
      maxLng: -66.9513812
    };

    return coords.minLat >= usaBounds.minLat && coords.maxLat <= usaBounds.maxLat &&
           coords.minLng >= usaBounds.minLng && coords.maxLng <= usaBounds.maxLng;
  }

  const route = isWithinUSA(mapcoordinates) ? '/imagefrommapusaonly' : '/imagefrommap';

  fetch(`http://localhost:5000${route}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(mapcoordinates),
  })
  .then(response => response.json())
  .then(data => {
    const { image, date, filename } = data;

    // Bildinhalt als Data URL setzen
    const url = `data:image/png;base64,${image}`;
    satellitenbildEarthEngine.src = url;
    mapUndBildOverlayContainer.style.display = 'none';
    let eckenkoordinaten = L.latLngBounds(
      L.latLng(mapcoordinates.minLat, mapcoordinates.minLng),
      L.latLng(mapcoordinates.maxLat, mapcoordinates.maxLng)
    );
    map.fitBounds(eckenkoordinaten);
    drawnItems.clearLayers();

    // Datum anzeigen
    const timestamp = parseInt(date, 10);
    if (!isNaN(timestamp)) {
      const dateObject = new Date(timestamp);
      const formattedDate = dateObject.toLocaleString();

      const satellitenbildDatum = document.getElementById('satellitenbildDatum');
      if (satellitenbildDatum) {
        satellitenbildDatum.textContent = formattedDate;
      } else {
        console.error('Element "satellitenbildDatum" nicht gefunden.');
      }
    } else {
      console.error('Ungültiger Timestamp:', date);
    }
  })
  .catch(error => console.error('Error:', error));
});

/**
 * Event-Listener, der das Social Media Bild über die Karte legt, wenn der Button geklickt wird.
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
 * Event-Listener, der die Transparenz des über die Karte gelegten Bildes ändert, wenn der Regler bewegt wird.
 */
bildTransaparenzRegler.addEventListener('change', () => {
  transparentesBildOverlay.style.opacity = bildTransaparenzRegler.value /100;
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
    var topRight = bounds.getNorthEast();
    var bottomLeft = bounds.getSouthWest();
    mapcoordinates = {minLng: bottomLeft.lng, minLat: bottomLeft.lat, maxLng: topRight.lng, maxLat: topRight.lat};
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
      const regex = new RegExp('\\b' + article, 'gi');
      text = text.replace(regex, '');
  });
  return text;
}

function removeSpecialCharacters(text) {
  const specialCharacters = ["#", "@", "|", "<", ">", ".", ":", ";"];
  specialCharacters.forEach(specialCharacter => {
    const regex = new RegExp('\\' + specialCharacter, 'g'); // Keine Wortgrenze, nur das Zeichen selbst
    text = text.replace(regex, '');
  });
  return text;
}