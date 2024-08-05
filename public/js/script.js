const socialMediaBild = document.getElementById('socialMediaBild'); // Bild-Element zum Anzeigen des hochgeladenen Satellitenbild von Social Media
const bildUeberKarteButton = document.getElementById('uebereinanderlegenButton'); // Button zum Überlagern des Satellitenbildes von Social Media über die Karte
const bildTransaparenzRegler = document.getElementById('transparenzRegler'); // Regler zum Einstellen der Transparenz des über die Karte gelegten Bildes
const transparentesBildOverlay = document.getElementById('transparentesBildOverlay'); // Bild-Element zum Anzeigen des über die Karte gelegten Bildes
const satellitenbildEarthEngine = document.getElementById('satellitenbildEarthEngine'); // Bild-Element zum Anzeigen des Satellitenbildes von Earth Engine
const mapUndBildOverlayContainer = document.getElementById('mapUndBildOverlayContainer'); // Container für die Karte und das (transparente) Bild Overlay
const textInput = document.getElementById('textInput'); // Text-Input-Feld für die Eingabe des zu analysierenden Textes eines Social Media Posts
const satellitenbildDatum = document.getElementById('satellitenbildDatum'); // Text-Element für das Datum des Satellitenbildes
const socialmediabildDatum = document.getElementById('socialmediabildDatum'); // Text-Element für das Datum des Social Media Bildes
const datumTag = document.getElementById('datumTag'); // Text-Element für das Datum des Satellitenbildes
const datumMonat = document.getElementById('datumMonat'); // Text-Element für das Datum des Satellitenbildes
const datumJahr = document.getElementById('datumJahr'); // Text-Element für das Datum des Satellitenbildes
const nextBtn = document.getElementById('nextBtn'); // Button zum Wechseln zum nächsten Schritt im Formular
const prevBtn = document.getElementById('prevBtn'); // Button zum Wechseln zum vorherigen Schritt im Formular
const changeDetectionBild = document.getElementById('changeDetectionBild'); // Bild-Element für die Ergebnisseite
const popup = document.getElementById('popup');
const copyLinkButton = document.getElementById('copyLinkButton');
const exampleLink = document.getElementById('exampleLink');

var coordinates = {lat: 0, lng: 0};
var mapcoordinates = {minLng: 0, minLat: 0, maxLng: 0, maxLat: 0};
var ueberlagert = false;
var textEingabe = '';
var datumEingabe = 1;
var currentTab = 0;
var socialMediaBildEingefuegt = false;
var eckenkoordinaten;
var beendet = false;
var formattedDate;
var testDatumNeu ={tag: 5, monat: 5, jahr: 2024};
var testTag;
var testMonat;
var testJahr;
showTab(currentTab);

/**
 * Event-Listener, der den nächsten Schritt im Formular anzeigt, wenn der Button geklickt wird.
 * Entsprechend der aktuellen Tab-Nummer werden die verschiedenen Schritte durchgeführt bevor der nächste Schritt angezeigt wird.
 * Schritt 1 (currentTab = 0): Nachdem die Nutzer*innen Bild und Text eingefügt haben, wird das Bild gespeichert und
 *                             der Text  analysiert um die Koordinaten des Ortes zu ermitteln.
 * Schritt 2 (currentTab = 1): Das von den Nutzer*innen eingegebeneDatum wird in einen Unix-Zeitstempel umgewandelt 
 *                             und gespeichert.
 * Schritt 3 (currentTab = 2): Das von den Nutzer*innen auf der Karte gezeichnete Rechteck wird in Koordinaten umgewandelt,
 *                             mit denen ein Satellitenbild von EarthEngine erstellt wird. Die Nutzer*innen wird auf die Ergebnisseite weitergeleitet, wo das ursprünglich von den
 *                             Nutzer*innen eingefügte Bild neben dem Satellitenbild von Earth Engine angezeigt wird.
 *                             Außerdem wird das Datum des Satellitenbildes und das Ergebnis der automatischen Analyse
 *                             angezeigt.   
 * Schritt 4 (currentTab = 3): Es wird das Popup angezeigt, in dem die Nutzer*innen den Link zum Teilen kopieren können.     
 */
nextBtn.addEventListener('click', async () => {
  //Schritt 1
  if(currentTab === 0) {
    if(textInput.value === '' || socialMediaBildEingefuegt === false) {
      alert('Bitte geben Sie einen Text ein und fügen Sie ein Bild ein.');
      return;
    }
    else {
    textEingabe = textInput.value;
    let abschicktext = removeSpecialCharacters(textEingabe);
    
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
      console.log('Bereinigter Text fürs Geocoding:', textForGeocode);
    
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
      coordinates = { lat: parseFloat(data.coords.lat), lng: parseFloat(data.coords.lon) };
      console.log('Vom Geocoding gefundene Koordinaten:', coordinates);
      // Zoomen auf die gefundenen Koordinaten
      eckenkoordinaten = L.latLngBounds(L.latLng(coordinates.lat, coordinates.lng), L.latLng(coordinates.lat, coordinates.lng));
      
    })
    .catch((error) => {
      console.error('Error:', error);
    });

      nextPrev(1);
      return;
    }
  }

  //Schritt 2
  if(currentTab === 1) {
    let tag = datumTag.value;
    let monat = datumMonat.value;
    let jahr = datumJahr.value;
    testTag = parseInt(tag);
    testMonat = parseInt(monat);
    testJahr = parseInt(jahr);
    datumEingabe = zeitInputsToUnix(tag, monat, jahr);
    nextPrev(1);
    return;
  }

  //Schritt 3
  if(currentTab === 2) {
    if(mapcoordinates =={minLng: 0, minLat: 0, maxLng: 0, maxLat: 0}){
      alert('Bitte zeichnen Sie ein Rechteck auf der Karte.');
      return;
    }
    else {
    map.fitBounds(eckenkoordinaten);
    let zeit = datumEingabe;
    // DOM-Elemente verstecken und Ladescreen anzeigen
    document.getElementById('vorabschluss').style.display = 'none';
    document.getElementById('nachabschluss').style.display = 'block';
    nextBtn.style.display = 'none';
    prevBtn.style.display = 'none';
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

  try {
    const response1 = await fetch(`http://localhost:5000${route}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        coords: mapcoordinates,
        date: zeit
      }),
    });

    if (!response1.ok) {
      throw new Error('Fehler bei der ersten Anfrage');
    }

    const data1 = await response1.json();
    console.log('Ergebnis der Earth Engine:', data1);
    const { image, date, filename } = data1;

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
      formattedDate = dateObject.toLocaleString();
    } else {
      console.error('Ungültiger Timestamp:', date);
    }

    const response2 = await fetch('http://localhost:5000/detectchange', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        socialMediaBild: socialMediaBild.src,
        satellitenbild: satellitenbildEarthEngine.src
      }),
    });

    if (!response2.ok) {
      throw new Error('Fehler bei der zweiten Anfrage');
    }

    const data2 = await response2.json();
    console.log('Ergebnis der Change Detection:', data2);
    const { image: image2, date: date2, filename: filename2 } = data2;

    // Bildinhalt als Data URL setzen
    const urlZwei = `data:image/png;base64,${image2}`;
    changeDetectionBild.src = urlZwei;

  } catch (error) {
    console.error('Error:', error);
  }

  nextPrev(1);
  nextBtn.style.display = 'block';
  // Für Testzwecke wird ein Datum simuliert
  var zahlEinsBisFuenf = Math.floor(Math.random() * 5) + 1;
  console.log("Zahl eins bis Zehn:" + zahlEinsBisFuenf);
  var neuerTag;
  if(testDatumNeu.tag <= 22) {
    neuerTag = testTag + zahlEinsBisFuenf;
  }
  else {
    neuerTag = testTag;
  }
  
  if(isNaN(testTag) && isNaN(testMonat) && isNaN(testJahr)) {
    socialmediabildDatum.innerHTML = 'Aufnahmedatum: unbekannt';
    satellitenbildDatum.innerHTML = 'Aufnahmedatum: 31.07.2024';
  }
  else if(isNaN(testTag) && isNaN(testMonat)) {
    socialmediabildDatum.innerHTML = 'Aufnahmedatum: ' + testJahr.toString();
    satellitenbildDatum.innerHTML = 'Aufnahmedatum: 02.06.' + testJahr.toString();
  }
  else if(isNaN(testTag)) {
    socialmediabildDatum.innerHTML = 'Aufnahmedatum: ' + testMonat.toString() + '.' + testJahr.toString();
    satellitenbildDatum.innerHTML = 'Aufnahmedatum: 04.' + testMonat.toString() + '.' + testJahr.toString();
  }
  else {
    socialmediabildDatum.innerHTML = 'Aufnahmedatum: ' + testTag.toString() + '.' + testMonat.toString() + '.' + testJahr.toString();
    satellitenbildDatum.innerHTML = 'Aufnahmedatum: ' + neuerTag.toString() + '.' + testMonat.toString() + '.' + testJahr.toString();
  }
  return;
  }
  }

  //Schritt 4
  if(currentTab === 3) {
    popup.style.display = 'block';
    beendet = true;
  }
});

/**
 * Event-Listener, der den vorherigen Schritt im Formular anzeigt, wenn der entsprechende Button geklickt wird.
 */
prevBtn.addEventListener('click', () => {
  nextPrev(-1);
});

/**
 * Event-Listener, der den Link zum Teilen kopiert, wenn der Button geklickt wird.
 */
copyLinkButton.addEventListener('click', () => {
  navigator.clipboard.writeText(exampleLink.href).then(() => {
    alert('Link kopiert!');
  }).catch(err => {
    console.error('Error copying text: ', err);
  });
});

/**
 * Event-Listener, der die Karte neu anzeigt, wenn der Tab gewechselt wird.
 * (Notwendig, da die Karte bei der Initialisierung nicht sichtbar ist und daher nicht korrekt angezeigt wird.)
 */
document.addEventListener('visibilitychange', function() {
  if (!document.hidden && currentTab === 2) {
    map.invalidateSize();
    map.setView([coordinates.lat, coordinates.lng], 15);
  }
});

/**
 * Event-Listener, der das in der Zwischenablage befindliche Bild auf der Webseite anzeigt,
 * wenn ein Bild aus der Zwischenablage mittels Strg+V auf die Seite kopiert wird.
 * Quelle: https://stackoverflow.com/questions/52597158/ctrl-v-insert-images-and-post (Code abgeändert) , Zugriff am 13.07.2024
 */
document.addEventListener('paste', (event) => {
  const items = event.clipboardData.items;
  for (const item of items) {
      if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          const reader = new FileReader();
          reader.onload = (event) => {
              socialMediaBild.src = event.target.result;
              socialMediaBild.style.display = 'block';
              socialMediaBildEingefuegt = true;
              const imgCopies = document.querySelectorAll('[id^=socialMediaBildCopy]');
              imgCopies.forEach(copy => {
                  copy.src = socialMediaBild.src;
                  copy.style.display = 'block';
              });
          };
          reader.readAsDataURL(file);
      }
  }
});

/**
 * Event-Listener, der das Social Media Bild über die Karte legt, wenn der Button geklickt wird.
 */
bildUeberKarteButton.addEventListener('click', (event) => {
  event.preventDefault(); // Verhindert das Standardverhalten des Buttons
  if(ueberlagert == false) {
    transparentesBildOverlay.src = socialMediaBild.src;
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

// Hinzufügen der Tile Layer, gefunden unter https://leaflet-extras.github.io/leaflet-providers/preview/ Zugriff am 25.06.2024
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

/**
 * Entfernt eine Auswahl von Sonderzeichen aus einem Text.
 * @param {String} text Text, aus dem die Sonderzeichen entfernt werden sollen
 * @returns Text ohne Sonderzeichen
 */
function removeSpecialCharacters(text) {
  const specialCharacters = ["#", "@", "|", "<", ">", ".", ":", ";"];
  specialCharacters.forEach(specialCharacter => {
    const regex = new RegExp('\\' + specialCharacter, 'g');
    text = text.replace(regex, '');
  });
  return text;
}

/**
 * Wandelt den Inhalt der Datums-Eingabefelder in einen Unix-Zeitstempel um.
 * @returns Unix-Zeitstempel des eingegebenen Datums
 */
function zeitInputsToUnix (tag, monat, jahr) {
  if(tag === null) { //Wenn kein Tag eingegeben wurde, wird für Tag der Wert 1 gesetzt
    tag = 1;
  }
  if(monat === null) { //Wenn kein Monat eingegeben wurde, wird für Monat der Wert 1 gesetzt
    monat = 1;
  }
  if(jahr === null) { //Wenn kein Jahr eingegeben wurde, wird das aktuelle Datum zurückgegeben
    return Date.now();
  }
  let datum = new Date(jahr, monat, tag);
  return datum.getTime();
}

/**
 * Diese Funktion ist Teil der tab-Architektur von W3Schools und wurde abgeändert.
 * Originalquelle: W3Schools. How TO - Form with Multiple Steps. Abgerufen am 13.07.2024, von https://www.w3schools.com/howto/howto_js_form_steps.asp.
 * @param {*} n 
 */
function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  // ... and fix the Previous/Next buttons:
  if (n == 0 || n == 3) {
    prevBtn.style.display = "none";
  } else {
    prevBtn.style.display = "inline";
  }
  if (n == (x.length - 1)) {
    nextBtn.innerHTML = "Teilen";
  } else {
    nextBtn.innerHTML = "Weiter";
  }
  if (n == 2) { // Annahme: Tab 3 hat den Index 2
    setTimeout(() => {
      map.invalidateSize();
      map.setView([coordinates.lat, coordinates.lng], 15);
    }, 100);
  }
  // ... and run a function that displays the correct step indicator:
  fixStepIndicator(n)
}

/**
 * Diese Funktion ist Teil der tab-Architektur von W3Schools und wurde abgeändert.
 * Originalquelle: W3Schools. How TO - Form with Multiple Steps. Abgerufen am 13.07.2024, von https://www.w3schools.com/howto/howto_js_form_steps.asp.
 * @param {*} n 
 */
function nextPrev(n) {
  if(beendet == false) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // Otherwise, display the correct tab:
  showTab(currentTab);
  }
}

/**
 * Diese Funktion ist Teil der tab-Architektur von W3Schools
 * Originalquelle: W3Schools. How TO - Form with Multiple Steps. Abgerufen am 13.07.2024, von https://www.w3schools.com/howto/howto_js_form_steps.asp.
 * @param {*} n 
 */
function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class to the current step:
  x[n].className += " active";
  
  // Adds the "finish" class to all previous steps:
  for (i = 0; i < n; i++) {
    x[i].className += " finish";
  }
}