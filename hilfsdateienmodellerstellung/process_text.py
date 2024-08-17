# Quelle: https://spacy.io/usage/training , Zugriff am 07.07.2024
# Imports aller benötigten Module, die mit pip installiert werden müssen
import spacy
from spacy.training import Example
from spacy.language import Language
import json
from pathlib import Path

# Laden des deutschen und englischen Modells, für Social Media/ News
nlp_en = spacy.load("en_core_web_sm")
nlp_de = spacy.load("de_core_news_sm")

# Erstellen eine neue leere Pipeline
nlp_combined = Language()

# Kopieren aller Komponenten aus dem englischen Modell
for name, component in nlp_en.pipeline:
    nlp_combined.add_pipe(name, source=nlp_en)

# Kopieren aller Komponenten aus dem deutschen Modell, die noch nicht in der Pipeline enthalten sind
for name, component in nlp_de.pipeline:
    if name not in nlp_combined.pipe_names:
        nlp_combined.add_pipe(name, source=nlp_de)


#Trainingsdaten
TRAIN_DATA = [
    ("Ein Bild von Kapstadt zeigt den Tafelberg und die Küste am Atlantischen Ozean", {"entities": [(13, 20, "STADT"), (32, 40, "POI")]}),
    ("Ein wunderschönes Satellitenbild von Innsbruck zeigt die Alpen und die Innenstadt", {"entities": [(37, 45, "STADT"), (57, 61, "POI"), (71, 80, "POI")]}),
    ("Today its exactly 90 years since the first photo of the LochNess Monster This satelliteimage was collected over Urquhart Castle Scotland on the shore of the Loch Ness lake Many sightings of Nessie have occurred just in front of the castle WorldView3 Maxar Provided by EUSI", {"entities": [(112, 126, "POI"), (128, 135, "LAND"), (157, 165, "POI"), (190, 195, "POI")]}),
    ("SATLANTIS iSIM90 VNIR payload captured this SatelliteImage at a 2meter resolution over Bilbao showcasing our impressive EarthObservation capabilitiesRemoteSensing EO satelliteimagery", {"entities": [(87, 92, "STADT")]}),
    ("On EarthDay2024 EarthDay reaffirms its mission to eliminate plastic usage for the wellbeing of the planet calling for a reduction in plastic production This SatelliteImage shows Vancouver Canada where significant investments are being made to combat plastic waste", {"entities": [(178, 186, "STADT"), (188, 193, "LAND")]}),
    ("Celebrate StPatricksDay with this SatelliteImage of Boston USA processed with fresh Sentinel2 dataEvery year Boston holds a huge parade attracting hundreds of thousands of spectators showcasing Irish culture music dance and historyGeospatialData PlanetSAT", {"entities": [(52, 57, "STADT"), (109, 114, "STADT"), (59, 61, "LAND")]}),
    ("Check out this ICONIC stage set up at Taylor Swift Eras Tour  Thanks AirbusSpace for capturing this epic shot of taylorswift13 Eras Tour set up at Acrisure Stadium in Pittsburgh from SPACE Taylornation13", {"entities": [(147, 162, "POI"), (167, 176, "STADT")]}),
    ("Now this is one incredible satelliteimage of SantiagoBernabeuStadium in Madrid Check out to see what other fantastic aerialviewimages and satelliteimagery our ImageHunter tool has in its collection", {"entities": [(45, 67, "POI"), (72, 77, "STADT")]}),
    ("The Paso Internacional Los Libertadores also called Cristo Redentor is a mountain pass in the Andes between Argentina and Chile It is the main transport route out of the Chilean capital city Santiago into Mendoza Province in Argentina and so carries quite heavy traffic", {"entities": [(4, 39, "POI"), (52, 67, "POI"), (108, 117, "LAND"), (225, 234, "LAND"), (122, 127, "LAND"), (170, 175, "LAND"), (191, 199, "STADT")]}),
    ("Perdido Pass  Orange Beach Alabama  Hero12", {"entities": [(0, 11, "POI"), (14, 25, "POI"), (27, 33, "STADT")]}),
    ("Aerial view of Logan Airport in Boston", {"entities": [(15, 27, "POI"), (32, 37, "STADT")]}),
    ("Packard Factory Demolition Detroit MI USA", {"entities": [(0, 14, "POI"), (27, 33, "STADT"), (38, 40, "LAND")]}),
    ("La ChauxdeFonds the only city with a grid layout in Switzerland", {"entities": [(0, 14, "STADT"), (52, 62, "LAND")]}),
    ("Silent Blast Furnaces at USSs Great Lakes Works Zug Island MI USA", {"entities": [(25, 46, "POI"), (59, 60, "STADT"), (62, 64, "LAND")]}),
    ("Miles Park Methodist Church UnionMiles Park Cleveland OH USA", {"entities": [(0, 27, "POI"), (44, 52, "STADT"), (57, 59, "LAND")]}),
    ("Fort Bourtange Groningen Netherlands", {"entities": [(0, 13, "POI"), (15, 23, "STADT"), (25, 35, "LAND")]}),
    ("An aerial view of the Sofitel Legend Santa Clara in Cartagena Columbia The hotel is housed in a beautifully restored 17thcentury convent offering guests a unique blend of colonial charm and modern luxury", {"entities": [(22, 47, "POI"), (52, 60, "STADT"), (62, 69, "LAND")]}),
    ("Fox Photographer RJ Salmon dangels in a Crate suspended from a Crane to take an Aerial Shot of Fleet Street London with St Pauls in the Background", {"entities": [(95, 106, "POI"), (108, 113, "STADT"), (120, 127, "POI")]}),
    ("The Flamingos Are Back While travelling on the road between Barkley West and Kimberley Northern Cape South Africa I noticed a large amount of Flamingos happily going on about their business in a Newly Formed Wetland to the North  West of Kimberley", {"entities": [(60, 71, "STADT"), (77, 85, "STADT"), (238, 246, "STADT"), (101, 112, "LAND")]}),
    ("Ein sonniger Tag in Bilbao Spanien und der GuggenheimMuseum ragt majestaetisch ueber die Stadt", {"entities": [(20, 25, "STADT"), (27, 33, "LAND"), (43, 58, "POI")]}),
    ("In Vancouver Kanada erstreckt sich das belebte Viertel Gastown waehrend der Steam Clock stolz in den Himmel ragt", {"entities": [(3, 11, "STADT"), (13, 18, "LAND"), (76, 86, "POI")]}),
    ("Santiago Chile zeigt uns das bunte Viertel Bellavista und die Pio Nono Strasse", {"entities": [(0, 7, "STADT"), (9, 13, "LAND"), (62, 77, "POI")]}),
    ("Die Strassen von Detroit USA sind ein Labyrinth aus Farben und Formen mit dem Detroit Institute of Arts im Fokus", {"entities": [(17, 23, "STADT"), (78, 84, "STADT"), (25, 27, "LAND"), (86, 102, "POI")]}),
    ("La ChauxdeFonds in der Schweiz mit der Avenue LeopoldRobert und der Maison Blanche", {"entities": [(0, 14, "STADT"), (23, 29, "LAND"), (39, 58, "POI"), (68, 81, "POI")]}),
    ("Cleveland USA im Herzen des Ohio City mit der belebten West 25th Street und dem West Side Market", {"entities": [(0, 8, "STADT"), (10, 12, "LAND"), (55, 70, "POI"), (80, 95, "POI")]}),
    ("Groningen Niederlande bietet uns die malerische Grote Markt und den Martinitoren", {"entities": [(0, 8, "STADT"), (10, 20, "LAND"), (48, 58, "POI"), (68, 79, "POI")]}),
    ("Cartagena Kolumbien mit der charmanten Calle de la Media Luna und der Plaza de la Trinidad", {"entities": [(0, 8, "STADT"), (10, 18, "LAND"), (39, 60, "POI"), (70, 89, "POI")]}),
    ("Shoreditch in London Vereinigtes Koenigreich ist ein Paradies fuer Street Art auf der Brick Lane", {"entities": [(14, 19, "STADT"), (21, 43, "LAND"), (86, 95, "POI")]}),
    ("Die atemberaubende Skyline von Boston USA mit dem Massachusetts State House im Mittelpunkt", {"entities": [(31, 36, "STADT"), (38, 40, "LAND"), (50, 74, "POI")]}),
    ("Die malerischen Strassen von Vancouver Kanada fuehren uns durch das historische Gastown", {"entities": [(29, 37, "STADT"), (39, 44, "LAND")]}),
    ("In Santiago Chile finden wir das belebte Viertel Bellavista und die Pio Nono Strasse", {"entities": [(3, 10, "STADT"), (12, 16, "LAND"), (68, 83, "POI")]}),
    ("Ein sonniger Tag in Valencia Spanien und die Ciudad de las Artes y las Ciencias ragt majestaetisch ueber die Stadt", {"entities": [(20, 27, "STADT"), (29, 35, "LAND"), (45, 78, "POI")]}),
    ("In Montreal, Kanada, erstreckt sich das lebhafte Viertel Plateau-Mont-Royal, während der Mont Royal stolz in den Himmel ragt", {"entities": [(3, 10, "STADT"), (13, 18, "LAND"), (89, 98, "POI")]}),
    ("Die belebte Karl Johans gate in Oslo, Norwegen, umgeben von historischen Gebäuden und modernen Geschäften", {"entities": [(12, 27, "POI"), (32, 35, "STADT"), (38, 45, "LAND")]}),
    ("Die Skyline von Melbourne, Australien, bei Nacht, mit den leuchtenden Lichtern der Wolkenkratzer und dem Eureka Tower im Hintergrund", {"entities": [(16, 24, "STADT"), (27, 36, "LAND"), (105, 116, "POI")]}),
    ("Die malerische Amstel in Amsterdam, Niederlande, mit Blick auf die Magere Brug und die historischen Gebäude entlang des Flusses", {"entities": [(15, 20, "POI"), (25, 33, "STADT"), (36, 46, "LAND"), (67, 77, "POI")]}),
    ("Die belebte OConnell Street in Dublin, Irland, mit dem General Post Office im Mittelpunkt", {"entities": [(12, 26, "POI"), (31, 36, "STADT"), (39, 44, "LAND"), (55, 73, "POI")]}),
    ("Die farbenfrohe Nyhavn in Kopenhagen, Dänemark, mit den charakteristischen Giebelhäusern entlang des Hafens", {"entities": [(16, 21, "POI"), (26, 35, "STADT"), (38, 45, "LAND")]}),
    ("Die majestätische Akropolis in Athen, Griechenland, thront über der Stadt und bietet einen atemberaubenden Blick auf die Umgebung", {"entities": [(18, 26, "POI"), (31, 35, "STADT"), (38, 49, "LAND")]}),
    ("Die belebte Nevsky Prospekt in St. Petersburg, Russland, mit dem Winterpalast im Hintergrund", {"entities": [(12, 26, "POI"), (31, 44, "STADT"), (47, 54, "LAND"), (65, 76, "POI")]}),
    ("Die historische Altstadt von Krakau, Polen, mit dem Wawel-Schloss und der Marienkirche", {"entities": [(29, 34, "STADT"), (37, 41, "LAND"), (52, 64, "POI"), (74, 85, "POI")]}),
    ("Die beeindruckende Golden Gate Bridge in San Francisco, USA, verbindet die Stadt mit Marin County über die Bucht von San Francisco", {"entities": [(19, 36, "POI"), (41, 53, "STADT"), (117, 129, "STADT"), (56, 58, "LAND")]}),
    ("Die farbenfrohe La Boca in Buenos Aires, Argentinien, bekannt für ihre Tango-Musik und die bunten Caminito-Gassen", {"entities": [(27, 38, "STADT"), (41, 51, "LAND"), (98, 112, "POI")]}),
    ("Die belebte Istiklal Caddesi in Istanbul, Türkei, mit historischen Gebäuden, Geschäften und Cafés", {"entities": [(12, 27, "POI"), (32, 39, "STADT"), (42, 47, "LAND")]}),
    ("Die atemberaubende Küste von Amalfi in Italien, mit den charakteristischen Klippen und den Städten Positano und Ravello", {"entities": [(29, 34, "STADT"), (39, 45, "LAND"), (99, 106, "POI"), (112, 118, "POI")]}),
    ("Die beeindruckende Christuskirche in Windhoek, Namibia, ist ein Wahrzeichen der Stadt und ein beliebter Aussichtspunkt", {"entities": [(19, 32, "POI"), (37, 44, "STADT"), (47, 53, "LAND")]}),
    ("Die malerische Gamla Stan in Stockholm, Schweden, mit den engen Gassen, bunten Gebäuden und dem Königlichen Schloss", {"entities": [(29, 37, "STADT"), (40, 47, "LAND")]}),
    ("Die belebte Paseo de la Reforma in Mexiko-Stadt, Mexiko, mit dem berühmten Engel der Unabhängigkeit", {"entities": [(12, 30, "POI"), (35, 46, "STADT"), (49, 54, "LAND"), (75, 98, "POI")]}),
    ("Die historische Altstadt von Dubrovnik, Kroatien, mit den Stadtmauern und dem Fort Lovrijenac", {"entities": [(29, 37, "STADT"), (40, 47, "LAND"), (58, 68, "POI"), (78, 92, "POI")]}),
    ("Die beeindruckende Skyline von Kuala Lumpur, Malaysia, mit den Petronas Towers und dem KL Tower", {"entities": [(31, 42, "STADT"), (45, 52, "LAND"), (63, 77, "POI"), (87, 94, "POI")]}),
    ("Die farbenfrohe La Rambla in Barcelona, Spanien, mit Straßenkünstlern, Cafés und dem Mercat de la Boqueria", {"entities": [(16, 24, "POI"), (29, 37, "STADT"), (40, 46, "LAND"), (85, 105, "POI")]}),
    ("Die majestätische Hagia Sophia in Istanbul, Türkei, mit ihrer beeindruckenden Kuppel und den Mosaiken", {"entities": [(18, 29, "POI"), (34, 41, "STADT"), (43, 48, "LAND")]}),
    ("Seaford Head - East Sussex UK aerial image", {"entities": [(0, 11, "POI"), (27, 28, "LAND")]}),
    ("Aerial Image of a Ground Fed River - Central Oregon, USA. From u/Austinjamesjackson on Reddit", {"entities": [(53, 56, "LAND")]}),
    ("Brighton Railway Station aerial image", {"entities": [(0, 7, "STADT"), (9, 23, "POI")]}),
    ("The Loggia at Hever Castle - Kent UK aerial image", {"entities": [(14, 25, "POI"), (34, 35, "LAND")]}),
    ("St Annes Quarter development construction in Norwich - UK aerial image", {"entities": [(0, 15, "POI"), (45, 51, "STADT"), (55, 56, "LAND")]}),
    ("Southfields Business Park - Basildon Essex UK aerial image", {"entities": [(0, 24, "POI"), (28, 35, "STADT"), (43, 44, "LAND")]}),
    ("Sydney Opera House Sydney NSW Australia", {"entities": [(0, 17, "POI"), (19, 24, "STADT"), (30, 38, "LAND")]}),
    ("Zurich Hauptbahnhof Zurich Switzerland", {"entities": [(0, 18, "POI"), (20, 25, "STADT"), (27, 37, "LAND")]}),
    ("Brandenburger Tor Berlin Germany", {"entities": [(0, 16, "POI"), (18, 23, "STADT"), (25, 31, "LAND")]}),
    ("The Shard London United Kingdom", {"entities": [(0, 8, "POI"), (10, 15, "STADT"), (17, 30, "LAND")]}),
    ("Statue of Liberty New York NY USA", {"entities": [(0, 16, "POI"), (18, 25, "STADT"), (30, 32, "LAND")]}),
    ("Colosseum Rome Italy", {"entities": [(0, 8, "POI"), (10, 13, "STADT"), (15, 19, "LAND")]}),
    ("Christ the Redeemer Rio de Janeiro RJ Brazil", {"entities": [(0, 18, "POI"), (20, 33, "STADT"), (38, 43, "LAND")]}),
    ("Akropolis Athens Greece", {"entities": [(0, 8, "POI"), (10, 15, "STADT"), (17, 22, "LAND")]}),
    ("Machu Picchu Cusco Peru", {"entities": [(0, 11, "POI"), (13, 17, "STADT"), (19, 22, "LAND")]}),
    ("Petra Jordan", {"entities": [(0, 4, "POI"), (6, 11, "LAND")]}),
    ("Taj Mahal Agra India", {"entities": [(0, 8, "POI"), (10, 13, "STADT"), (15, 19, "LAND")]}),
    ("Sagrada Familia Barcelona Spain", {"entities": [(0, 14, "POI"), (16, 24, "STADT"), (26, 30, "LAND")]}),
    ("Golden Gate Bridge San Francisco CA USA", {"entities": [(0, 17, "POI"), (19, 31, "STADT"), (36, 38, "LAND")]}),
    ("Forbidden City Beijing China", {"entities": [(0, 13, "POI"), (15, 21, "STADT"), (23, 27, "LAND")]}),
    ("Louvre Museum Paris France", {"entities": [(0, 12, "POI"), (14, 18, "STADT"), (20, 25, "LAND")]}),
    ("Neuschwanstein Castle Schwangau Germany", {"entities": [(0, 20, "POI"), (22, 30, "STADT"), (32, 38, "LAND")]}),
    ("Grand Canyon National Park AZ USA", {"entities": [(0, 25, "POI"), (30, 32, "LAND")]}),
    ("Hagia Sophia Istanbul Turkey", {"entities": [(0, 10, "POI"), (13, 19, "STADT"), (22, 26, "LAND")]}),
    ("Acropolis Museum Athens Greece", {"entities": [(0, 15, "POI"), (17, 22, "STADT"), (24, 29, "LAND")]}),
    ("Buckingham Palace London United Kingdom", {"entities": [(0, 16, "POI"), (18, 23, "STADT"), (25, 38, "LAND")]}),
    ("The Alamo San Antonio TX USA", {"entities": [(0, 8, "POI"), (10, 20, "STADT"), (25, 27, "LAND")]}),
    ("Mount Rushmore Keystone SD USA", {"entities": [(0, 13, "POI"), (15, 22, "STADT"), (27, 28, "LAND")]}),
    ("Sydney Harbour Bridge Sydney NSW Australia", {"entities": [(0, 20, "POI"), (22, 27, "STADT"), (33, 41, "LAND")]}),
    ("St. Peters Basilica Vatican City", {"entities": [(0, 18, "POI"), (20, 31, "STADT")]}),
    ("Chichen Itza Yucatan Mexico", {"entities": [(0, 11, "POI"), (13, 19, "STADT"), (21, 26, "LAND")]}),
    ("Mount Everest Nepal", {"entities": [(0, 12, "POI"), (14, 18, "LAND")]}),
    ("Ipanema Beach Rio de Janeiro RJ Brazil", {"entities": [(0, 12, "POI"), (14, 27, "STADT"), (32, 37, "LAND")]}),
    ("Great Barrier Reef Queensland Australia", {"entities": [(0, 17, "POI"), (30, 38, "LAND")]}),
    ("Tower Bridge London United Kingdom", {"entities": [(0, 11, "POI"), (13, 18, "STADT"), (20, 33, "LAND")]}),
    ("Venice Canals Venice Italy", {"entities": [(0, 12, "POI"), (14, 19, "STADT"), (21, 25, "LAND")]}),
    ("Yellowstone National Park WY USA", {"entities": [(0, 24, "POI"), (29, 31, "LAND")]}),
    ("Louvre Abu Dhabi Abu Dhabi United Arab Emirates", {"entities": [(0, 15, "POI"), (17, 25, "STADT"), (27, 46, "LAND")]}),
    ("Mount Fuji Tokyo Japan", {"entities": [(0, 9, "POI"), (11, 15, "STADT"), (17, 21, "LAND")]}),
    ("Cathedral Cologne Germany", {"entities": [(0, 8, "POI"), (10, 16, "STADT"), (18, 24, "LAND")]}),
    ("Ngorongoro Crater Arusha Tanzania", {"entities": [(0, 16, "POI"), (18, 23, "STADT"), (25, 32, "LAND")]}),
    ("Canberra Lake Burley Griffin", {"entities": [(0, 7, "STADT"), (9, 27, "POI")]}),
    ("Empire State Building New York", {"entities": [(22, 29, "STADT"), (0, 20, "POI")]}),
    ("Sydney Opera House Australia", {"entities": [(0, 5, "STADT"), (7, 17, "POI"), (19, 27, "LAND")]}),
    ("Rom historische Sehenswürdigkeiten", {"entities": [(0, 2, "STADT")]}),
    ("Freiheitsstatue New York City", {"entities": [(0, 14, "POI"), (16, 28, "STADT")]}),
    ("Akropolis Athen griechische Antike", {"entities": [(0, 8, "POI"), (10, 14, "STADT"), (16, 33, "LAND")]}),
    ("Burj Khalifa Dubai höchste Gebäude der Welt", {"entities": [(0, 11, "POI"), (13, 17, "STADT")]}),
    ("Kolosseum Rom altes Amphitheater", {"entities": [(0, 8, "POI"), (10, 12, "STADT")]}),
    ("Die Chinesische Mauer beeindruckendsten Bauwerke der Welt", {"entities": [(4, 20, "POI")]}),
    ("Louvre Paris größten und bekanntesten Museen der Welt", {"entities": [(0, 5, "POI"), (7, 11, "STADT")]}),
    ("Taj Mahal Indien berühmtes Mausoleum", {"entities": [(0, 8, "POI"), (10, 15, "STADT")]}),
    ("Sagrada Familia Barcelona berühmte Basilika", {"entities": [(0, 14, "POI"), (16, 24, "STADT")]}),
    ("Pyramiden von Gizeh bekannteste ägyptische Bauwerk", {"entities": [(0, 8, "POI"), (14, 18, "STADT")]}),
    ("Opernhaus Sydney", {"entities": [(0, 8, "POI"), (10, 17, "STADT")]}),
    ("Central Park New York City", {"entities": [(0, 11, "POI"), (13, 25, "STADT")]}),
    ("Oper von Oslo Norwegen", {"entities": [(0, 3, "POI"), (9, 12, "STADT"), (14, 21, "LAND")]}),
    ("Ruinen Machu Picchu Peru", {"entities": [(0, 18, "POI"), (20, 23, "LAND")]}),
    ("Sydney Opera House", {"entities": [(7, 17, "POI"), (0, 5, "STADT")]}),
    ("Akropolis Athen Griechenland", {"entities": [(0, 8, "POI"), (10, 14, "STADT"), (16, 27, "LAND")]}),
    ("Freiheitsstatue New York", {"entities": [(0, 14, "POI"), (16, 23, "STADT")]}),
    ("Pyramiden Gizeh existieren nicht", {"entities": [(0, 8, "POI"), (10, 14, "STADT")]}),
    ("Eiffelturm Paris", {"entities": [(0, 9, "POI"), (11, 15, "STADT")]}),
    ("Niagara Falls Kanada USA", {"entities": [(0, 12, "POI"), (14, 19, "LAND"), (21, 23, "LAND")]}),
    ("Kolosseum Rom ist zerstoert", {"entities": [(0, 8, "POI"), (10, 12, "STADT")]}),
    ("Chinesische Mauer", {"entities": [(0, 16, "POI")]}),
    ("Buckingham Palace London", {"entities": [(0, 16, "POI"), (18, 23, "STADT")]}),
    ("Kölner Dom aus dem All", {"entities": [(0, 9, "POI")]}),
    ("Christusstatue Rio de Janeiro Brasilien", {"entities": [(0, 13, "POI"), (15, 28, "STADT"), (30, 38, "LAND")]}),
    ("Brandenburger Tor Berlin", {"entities": [(0, 16, "POI"), (18, 23, "STADT")]}),
    ("Burj Khalifa Dubai", {"entities": [(0, 11, "POI"), (13, 17, "STADT")]}),
    ("Louvre Paris von oben", {"entities": [(0, 5, "POI"), (7, 11, "STADT")]}),
    ("Sagrada Familia Barcelona", {"entities": [(0, 14, "POI"), (16, 24, "STADT")]}),
    ("Golden Gate Bridge San Francisco aus der Luft", {"entities": [(0, 17, "POI"), (19, 31, "STADT")]}),
    ("Berliner Mauer Deutschland", {"entities": [(0, 13, "POI"), (15, 25, "LAND")]}),
    ("Mount Everest mit seiner hohen Spitze", {"entities": [(0, 12, "POI")]}),
    ("Niagarafälle Kanada USA", {"entities": [(0, 11, "POI"), (13, 18, "LAND"), (20, 22, "LAND")]}),
    ("Luftbild der Stapenhorststraße in Bielefeld aus Deutschland", {"entities": [(13, 29, "POI"), (34, 42, "STADT"), (48, 58, "LAND")]}),
    ("Grundriss des neuen Flughafens am Baumschulenweg in Winterberg Nordrhein-Westfalen", {"entities": [(34, 47, "POI"), (52, 61, "STADT")]}),
    ("Die Ameisenbergstraße im Viertel Uhlandshöhe in Stuttgart", {"entities": [(4, 20, "POI"), (48, 56, "STADT")]}),
    ("Silo Rd und der Lake Hamp von oben nachdem er ausgetrocknet ist", {"entities": [(0, 6, "POI"), (16, 24, "POI")]}),
    ("Die Hauptstraße an der Stein-Schule in Hamburg", {"entities": [(23, 34, "POI"), (4, 14, "POI"), (39, 45, "STADT")]}),
    ("Beschreibung des Parks am See in Berlin", {"entities": [(17, 28, "POI"), (33, 38, "STADT")]}),
    ("Die Straße der Einheit in Leipzig", {"entities": [(4, 21, "POI"), (26, 32, "STADT")]}),
    ("Der Fluss Rhein in Köln", {"entities": [(10, 14, "POI"), (19, 22, "STADT")]}),
    ("Die Brücke am Hafen in Hamburg", {"entities": [(4, 9, "POI"), (23, 29, "STADT")]}),
    ("Die Allee der Bäume in München", {"entities": [(4, 18, "POI"), (23, 29, "STADT")]}),
    ("Aerial view of Fifth Avenue in New York City, United States", {"entities": [(15, 26, "POI"), (31, 38, "CITY"), (46, 58, "COUNTRY")]}),
    ("Map of Paddington Street in London, United Kingdom", {"entities": [(7, 23, "POI"), (28, 33, "CITY"), (36, 49, "COUNTRY")]}),
    ("Sunset Boulevard in Los Angeles, California, United States", {"entities": [(0, 15, "POI"), (20, 30, "CITY"), (33, 42, "STATE"), (45, 57, "COUNTRY")]}),
    ("Champs-Élysées in Paris, France", {"entities": [(0, 13, "POI"), (18, 22, "CITY"), (25, 30, "COUNTRY")]}),
    ("Nanjing Road in Shanghai, China", {"entities": [(0, 11, "POI"), (16, 23, "CITY"), (26, 30, "COUNTRY")]}),
    ("Kurfürstendamm in Berlin, Germany", {"entities": [(0, 13, "POI"), (18, 23, "CITY"), (26, 32, "COUNTRY")]}),
    ("Ginza Street in Tokyo, Japan", {"entities": [(0, 11, "POI"), (16, 20, "CITY"), (23, 27, "COUNTRY")]}),
    ("Rodeo Drive in Beverly Hills, California, United States", {"entities": [(0, 10, "POI"), (15, 27, "CITY"), (30, 39, "STATE"), (42, 54, "COUNTRY")]}),
    ("Orchard Road in Singapore", {"entities": [(0, 11, "POI"), (16, 24, "CITY")]})
    ]

# Trainingsdaten sind mit den falschen Indizes versehen, also werden diese korrigiert
for item in TRAIN_DATA:
    # Zugriff auf das Tupel mit den Entities
    entities = item[1]["entities"]
    
    # Durch jedes Tupel in 'entities' iterieren
    for i, entity in enumerate(entities):
        # Das Tupel dekonstruieren, um auf die Endposition (zweite Zahl) zuzugreifen und zu ändern
        start, end, label = entity
        # Endposition wird um 1 erhöht
        end_neu = end + 1
        # Das geänderte Tupel wird wieder zusammengesetzt und in die Liste zurückgeschrieben
        entities[i] = (start, end_neu, label)


# NER-Komponente hinzufügen oder holen, wenn sie bereits existiert
# NER (Named Entity Recognition) ist die Komponente, die für das Klassifizieren von Entitäten in Texten zuständig ist
if "ner" not in nlp_combined.pipe_names:
    ner = nlp_combined.add_pipe("ner", last=True)
else:
    ner = nlp_combined.get_pipe("ner")

# Labels aus den Trainingsdaten hinzufügen, in diesem Fall "POI", "STADT", "VIERTEL" und "LAND"
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities", []):
        ner.add_label(ent[2])

# Trainieren des kombinierten Modells
other_pipes = [pipe for pipe in nlp_combined.pipe_names if pipe != "ner"] # Alle Pipes außer der NER-Pipe speichern (Pipe ist einer der Schritte des Algorithmus)
with nlp_combined.disable_pipes(*other_pipes): # Alle Pipes außer der NER-Pipe deaktivieren, damit nur diese während der Ausführung geändert wird
    optimizer = nlp_combined.begin_training() # Erstellt Optimierer, der die Gewichte des Modells basierend auf den Trainingsdaten anpasst
    for i in range(20): #Trainingsdatenset wird 20 mal durchlaufen (Epochen)
        losses = {} # Leeres Dictionary für Speicherung der Verluste
        for text, annotations in TRAIN_DATA:
            doc = nlp_combined.make_doc(text) # Erstellt ein Doc-Objekt aus dem Text aus einem der Trainingsdaten
            example = Example.from_dict(doc, annotations) # Erstellt ein Beispielobjekt aus dem Doc-Objekt und den Annotationsdaten
            nlp_combined.update([example], losses=losses, drop=0.5, sgd=optimizer) # Aktualisiert das Modell mit dem Beispielobjekt, speichert Verluste in losses und verwendet den Optimierer zur Aktualiesierung der Gewichte
        print(losses) #Ausgabe der Verluste, während des Trainings Übersicht über den Fortschritt, wenn Verluste stagnieren, ist das Modell wahrscheinlich ausgelernt

# Speicheren des trainierten Modells im Ordner 'trainiertesmodell'
output_dir = r"C:\Users\User\Documents\GitHub\bachelorThesis\trainiertesmodell"
nlp_combined.to_disk(output_dir)