/**
 * Hilfsdatei zur Erstellung von TRAINING_DATA für die spaCy-Modellerstellung
 * Bringt die Beispieldaten in die richtige Form und fügt Indizes hinzu
 * Inzwischen korrekter End Index
 */
var beispielzeilen = [
        ["Neues Foto von der Pferdegasse im Viertel Algersdorf, Graz", ["POI", "Pferdegasse"], ["STADT", "Graz"], ["VIERTEL", "Algersdorf"]],
        ["Hier sehen Sie die Via Falerina in Italiens Hauptstadt Rom", ["POI", "Via Falerina"], ["STADT", "Rom"], ["LAND", "Italien"]],
        ["Die Boeselagerstrasse in Schwerin", ["POI", "Boeselagerstrasse"], ["STADT", "Schwerin"]],
        ["Dieses Bild stamt aus der Enneschtgass in Bech in Luxemburg", ["POI", "Enneschtgass"], ["STADT", "Bech"], ["LAND", "Luxemburg"]],
        ["Die Straße des 17. Juni in Berlin", ["POI", "Straße des 17. Juni"], ["STADT", "Berlin"]],
        ["Die Straße der Pariser Kommune in Hamburg", ["POI", "Straße der Pariser Kommune"], ["STADT", "Hamburg"]],
        ["Die Straße der Republik in Frankfurt", ["POI", "Straße der Republik"], ["STADT", "Frankfurt"]],
        ["Via Montenapoleone in Milan, Italy", ["POI", "Via Montenapoleone"], ["CITY", "Milan"], ["COUNTRY", "Italy"]],
        ["Passeig de Gràcia in Barcelona, Spain", ["POI", "Passeig de Gràcia"], ["CITY", "Barcelona"], ["COUNTRY", "Spain"]],
        ["Nevsky Prospect in Saint Petersburg, Russia", ["POI", "Nevsky Prospect"], ["CITY", "Saint Petersburg"], ["COUNTRY", "Russia"]],
        ["Kärntner Strasse in Vienna, Austria", ["POI", "Kärntner Strasse"], ["CITY", "Vienna"], ["COUNTRY", "Austria"]],
        ["Die Aaseekugeln aus Muenster Deutschland wurden ueber Nacht entwendet", ["POI", "Aaseekugeln"], ["STADT", "Muenster"], ["LAND", "Deutschland"]],
        ["In Johannisburg wurde ein Fernsehturm im Viertel Newton gesprengt, die Polizei in Suedafrika ermittelt", ["POI", "Fernsehturm"], ["STADT", "Johannisburg"], ["LAND", "Suedafrika"], ["Viertel", "Newton"]],
        ["Ein Luftbild von der Katastrophe mit dem Big Ben aus London in der Hauptstadt von England", ["POI", "Big Ben"], ["STADT", "London"], ["LAND", "England"]],
        ["Mustafas Gemuesekebab im Kreuzviertel Berlin hat seine Ladenflaeche verdreifacht wie auf diesem Bild zu sehen ist", ["POI", "Mustafas Gemuesekebab"], ["STADT", "Berlin"], ["VIERTEL", "Kreuzviertel"]],
        ["Der K2 auf der Seite von Pakistan ist jetzt der hoechste Berg der Welt nachdem dort Land aufgeschuettet wurde", ["POI", "K2 "], ["LAND", "Pakistan"]],
        ["The Notre Dame in Paris France burnt down another time today", ["POI", "Notre Dame"], ["STADT", "Paris"], ["LAND", "France"]],
        ["The Canberra Parliament Building was completely destroyed by a huge thunderstorm in Australias seventh biggest city", ["POI", "Parliament Building"], ["STADT", "Canberra"], ["LAND", "Australia"]],
        ["After an earthquake the whole Mariscal District of Quito was destroyed", ["VIERTEL", "Mariscal District"], ["STADT", "Quito"]],
        ["Santa Monica Pier has begun the construction of a second ferry wheel in Los Angeles USA", ["POI", "Santa Monica Pier"], ["POI", "ferry wheel"], ["STADT", "Los Angeles"], ["LAND", "USA"]],
        ["The new 80 foot Messi statue in Buenos Aires Argentinas capital city was erected this Saturday", ["POI", "Messi statue"], ["STADT", "Buenos Aires"], ["LAND", "Argentinas"]],
        ["Innenstadt Winterthur Schweiz", ["STADT", "Winterthur"], ["LAND", "Schweiz"], ["VIERTEL", "Innenstadt"]],
        ["Alexanderplatz Berlin", ["POI", "Alexanderplatz"], ["STADT", "Berlin"]],
        ["Nieuwe Kerk in Delft Niederlande", ["POI", "Nieuwe Kerk"], ["STADT", "Delft"], ["LAND", "Niederlande"]],
        ["Elbphilharmonie in Deutschland Hamburg Hafencity", ["POI", "Elbphilharmonie"], ["STADT", "Hamburg"], ["LAND", "Deutschland"], ["VIERTEL", "Hafencity"]],
        ["McDonalds in Zhenjiang", ["STADT", "Zhenjiang"], ["POI", "McDonalds"]],
        ["Ground Zero New York", ["STADT", "New York"], ["POI", "Ground Zero"]],
        ["The White House in Washington D.C. USA", ["STADT", "Washington D.C."], ["POI", "White House"], ["LAND", "USA"]],
        ["Space Needle in Seattle", ["STADT", "Seattle"], ["POI", "Space Needle"]],
        ["Azadi Tower Tehran Iran", ["STADT", "Tehran"], ["LAND", "Iran"], ["POI", "Azadi Tower"]],
        ["Circuit de Catalonia in Barcelona Spain quarter Sant Marti", ["POI", "Circuit de Catalonia"], ["STADT", "Barcelona"], ["LAND", "Spain"], ["VIERTEL", "Sant Marti"]]
        ];
        
    
    

function arrayfuellen(neuezeile) {
    let laenge = neuezeile.length;
    let text = neuezeile[0];
    let ausgabe = [];
    for (var i = 1; i < laenge; i++) {
        let label = neuezeile[i][0];
        let wert = neuezeile[i][1];
        let index = text.indexOf(wert);
        let startpositions = [];
        let endpositions = [];
        while (index !== -1) {
            let endIndex = index + wert.length -1;
            startpositions.push(index);
            endpositions.push(endIndex);
            index = text.indexOf(wert, index + 1);
        }
        if (startpositions.length === 1) {
            ausgabe.push(`(${startpositions[0]}, ${endpositions[0]}, "${label}")`);
        } else if (startpositions.length > 1) {
            console.log(`Mehrere Vorkommen für "${wert}" gefunden:`, startpositions);
            ausgabe.push(`(${startpositions[0]}, ${endpositions[0]}, "${label}")`);
            ausgabe.push(`(${startpositions[1]}, ${endpositions[1]}, "${label}")`);
        }
    }
    return `("${text}", [${ausgabe.join(", ")}])`;
}

var TRAINING_DATA = [];

for (var i = 0; i < beispielzeilen.length; i++) {
    let ergebnis = arrayfuellen(beispielzeilen[i]);
    TRAINING_DATA.push(ergebnis);
}

// Ausgabe von TRAINING_DATA
console.log(TRAINING_DATA);
