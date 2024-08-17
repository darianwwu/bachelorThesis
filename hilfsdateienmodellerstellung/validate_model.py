# Quelle: https://spacy.io/usage/training , Zugriff am 07.07.2024
import spacy
from sklearn.metrics import precision_recall_fscore_support
from collections import defaultdict


# Validierungsdaten
VALIDATION_DATA = [
("Neues Foto von der Pferdegasse im Viertel Algersdorf, Graz", {"entities": [(19, 29, "POI"), (54, 57, "STADT")]}),
("Elbphilharmonie in Deutschland Hamburg nach dem Erdbeben gestern Nacht", {"entities": [(0, 14, "POI"), (31, 37, "STADT"), (19, 29, "LAND")]}),
("Hier sehen Sie die Via Falerina in Italiens Hauptstadt Rom", {"entities": [(19, 30, "POI"), (55, 57, "STADT"), (35, 41, "LAND")]}),
("Die Boeselagerstrasse in Schwerin", {"entities": [(4, 20, "POI"), (25, 32, "STADT")]}),
("Dieses Bild stamt aus der Enneschtgass in Bech in Luxemburg", {"entities": [(26, 37, "POI"), (42, 45, "STADT"), (50, 58, "LAND")]}),
("Die Straße des 17. Juni in Berlin", {"entities": [(4, 22, "POI"), (27, 32, "STADT")]}),
("Die Straße der Pariser Kommune in Hamburg", {"entities": [(4, 29, "POI"), (34, 40, "STADT")]}),
("Die Straße der Republik in Frankfurt", {"entities": [(4, 22, "POI"), (27, 35, "STADT")]}),
("Via Montenapoleone in Milan, Italy", {"entities": [(0, 17, "POI"), (22, 26, "STADT"), (29, 33, "LAND")]}),
("Passeig de Gràcia in Barcelona, Spain", {"entities": [(0, 16, "POI"), (21, 29, "STADT"), (32, 36, "LAND")]}),
("Nevsky Prospect in Saint Petersburg, Russia", {"entities": [(0, 14, "POI"), (19, 34, "STADT"), (37, 42, "LAND")]}),
("Kärntner Strasse in Vienna, Austria", {"entities": [(0, 15, "POI"), (20, 25, "STADT"), (28, 34, "LAND")]}),
("Die Aaseekugeln aus Muenster Deutschland wurden ueber Nacht entwendet", {"entities": [(4, 14, "POI"), (20, 27, "STADT"), (29, 39, "LAND")]}),
("In Johannisburg wurde ein Fernsehturm im Viertel Newton gesprengt, die Polizei in Suedafrika ermittelt", {"entities": [(26, 36, "POI"), (3, 14, "STADT"), (82, 91, "LAND")]}),
("Ein Luftbild von der Katastrophe mit dem Big Ben aus London in der Hauptstadt von England", {"entities": [(41, 47, "POI"), (53, 58, "STADT"), (82, 88, "LAND")]}),
("Mustafas Gemuesekebab im Kreuzviertel Berlin hat seine Ladenflaeche verdreifacht wie auf diesem Bild zu sehen ist", {"entities": [(0, 20, "POI"), (38, 43, "STADT")]}),
("Der K2 auf der Seite von Pakistan ist jetzt der hoechste Berg der Welt nachdem dort Land aufgeschuettet wurde", {"entities": [(4, 6, "POI"), (25, 32, "LAND")]}),
("The Notre Dame in Paris France burnt down another time today", {"entities": [(4, 13, "POI"), (18, 22, "STADT"), (24, 29, "LAND")]}),
("The Canberra Parliament Building was completely destroyed by a huge thunderstorm in Australias seventh biggest city", {"entities": [(13, 31, "POI"), (4, 11, "STADT"), (84, 92, "LAND")]}),
("After an earthquake the whole Mariscal District of Quito was destroyed", {"entities": [(51, 55, "STADT")]}),
("Santa Monica Pier has begun the construction of a second ferry wheel in Los Angeles USA", {"entities": [(0, 16, "POI"), (57, 67, "POI"), (72, 82, "STADT"), (84, 86, "LAND")]}),
("The new 80 foot Messi statue in Buenos Aires Argentinas capital city was erected this Saturday", {"entities": [(16, 27, "POI"), (32, 43, "STADT"), (45, 54, "LAND")]}),
("Innenstadt Winterthur Schweiz", {"entities": [(11, 20, "STADT"), (22, 28, "LAND")]}),
("Alexanderplatz Berlin", {"entities": [(0, 13, "POI"), (15, 20, "STADT")]}),
("Nieuwe Kerk in Delft Niederlande wurde um ein neues Gebaeude erweitert", {"entities": [(0, 10, "POI"), (15, 19, "STADT"), (21, 31, "LAND")]}),
("McDonalds in Zhenjiang", {"entities": [(13, 21, "STADT"), (0, 8, "POI")]}),
("Ground Zero New York", {"entities": [(12, 19, "STADT"), (0, 10, "POI")]}),
("The White House in Washington D.C. USA", {"entities": [(19, 33, "STADT"), (4, 14, "POI"), (35, 37, "LAND")]}),
("Space Needle in Seattle", {"entities": [(16, 22, "STADT"), (0, 11, "POI")]}),
("Azadi Tower Tehran Iran", {"entities": [(12, 17, "STADT"), (19, 22, "LAND"), (0, 10, "POI")]}),
("Circuit de Catalonia in Barcelona Spain quarter Sant Marti", {"entities": [(0, 19, "POI"), (24, 32, "STADT"), (34, 38, "LAND")]})
]

for item in VALIDATION_DATA:
    # Zugriff auf das Tupel mit den Entities
    entities = item[1]["entities"]
    
    # Durch jedes Tupel in 'entities' iterieren
    for i, entity in enumerate(entities):
        # Das Tupel dekonstruieren, um auf die Endposition (zweite Zahl) zuzugreifen und zu ändern
        start, end, label = entity
        # Hier die Endposition um 1 erhöhen
        end_neu = end + 1
        # Das geänderte Tupel wieder zusammensetzen und in die Liste zurückschreiben
        entities[i] = (start, end_neu, label)


# Laden des trainierten Modells
nlp = spacy.load(r"C:\Users\User\Documents\GitHub\bachelorThesis\trainiertesmodell")

# Liste der erlaubten Klassen
allowed_labels = {'STADT', 'LAND', 'POI'}

# Funktion zur Berechnung der Metriken für jede Klasse
def calculate_class_metrics(true_entities, pred_entities):
    true_set = set(true_entities)
    pred_set = set(pred_entities)

    # True Positives, False Positives, False Negatives für jede Klasse
    metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
    
    for ent in true_set:
        if ent[2] in allowed_labels:
            if ent in pred_set:
                metrics[ent[2]]['tp'] += 1
            else:
                metrics[ent[2]]['fn'] += 1
    
    for ent in pred_set:
        if ent[2] in allowed_labels:
            if ent not in true_set:
                metrics[ent[2]]['fp'] += 1
    
    return metrics

# Gesamtmetriken initialisieren
class_metrics = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})

# Validierung des Modells
for text, annotations in VALIDATION_DATA:
    doc = nlp(text)  # Verarbeite den Text mit dem Modell

    # Wahre und vorhergesagte Entitäten in das Format (start, end, label) umwandeln
    y_true = [(start, end, label) for start, end, label in annotations['entities'] if label in allowed_labels]
    y_pred = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in allowed_labels]

    # Berechne Metriken für diese Instanz
    instance_metrics = calculate_class_metrics(y_true, y_pred)
    
    # Addiere die Metriken zur Gesamtmetrik
    for label, metrics in instance_metrics.items():
        class_metrics[label]['tp'] += metrics['tp']
        class_metrics[label]['fp'] += metrics['fp']
        class_metrics[label]['fn'] += metrics['fn']

# Durchschnittliche Metriken berechnen
precisions = []
recalls = []
f1_scores = []

for label, metrics in class_metrics.items():
    precision = metrics['tp'] / (metrics['tp'] + metrics['fp']) if (metrics['tp'] + metrics['fp']) > 0 else 0
    recall = metrics['tp'] / (metrics['tp'] + metrics['fn']) if (metrics['tp'] + metrics['fn']) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    precisions.append(precision)
    recalls.append(recall)
    f1_scores.append(f1)
    
    print(f"Class: {label}")
    print(f"  Precision: {precision:.2f}")
    print(f"  Recall: {recall:.2f}")
    print(f"  F1-Score: {f1:.2f}")

# Mikro-Durchschnitte berechnen
total_tp = sum(metrics['tp'] for metrics in class_metrics.values())
total_fp = sum(metrics['fp'] for metrics in class_metrics.values())
total_fn = sum(metrics['fn'] for metrics in class_metrics.values())

micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0

print(f"\nMicro-Averaged Precision: {micro_precision:.2f}")
print(f"Micro-Averaged Recall: {micro_recall:.2f}")
print(f"Micro-Averaged F1-Score: {micro_f1:.2f}")

# Makro-Durchschnitte berechnen
macro_precision = sum(precisions) / len(precisions) if precisions else 0
macro_recall = sum(recalls) / len(recalls) if recalls else 0
macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0

print(f"\nMacro-Averaged Precision: {macro_precision:.2f}")
print(f"Macro-Averaged Recall: {macro_recall:.2f}")
print(f"Macro-Averaged F1-Score: {macro_f1:.2f}")

