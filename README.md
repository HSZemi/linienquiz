# linienquiz
Linien in Bonn - Ein Quiz. Welche Linie bin ich?

# script/json2image.py

Das Skript bekommt als Parameter die Ausgabedatei (.svg) und mindestens eine GeoJSON-Datei als Eingabe übergeben. Die erste Eingabe bestimmt den "Kartenausschnitt", alle weiteren Eingaben werden in den Ausschnitt eingepasst. Dargestellt werden LineString- und Polygon-Elemente, die Logik dazu ist aber nicht sehr intelligent.

# Pipeline

Aus den json-Dateien werden mit json2image.py SVG-Grafiken erzeugt, die dann mit Inkscape im Batch-Betrieb als PNG-Dateien exportiert werden. Die PNG-Dateien werden schließlich manuell in den img-Ordner im html-Ordner kopiert.

# Siehe auch

* [https://hszemi.de/2016/06/bonner-linien-erkennen/]
* [http://hscmi.de/linien/]

# Bekannte Probleme

* Die Darstellung von Linie 600 enthält eine nicht mehr aktive Umleitung
* Die Darstellung von Linie 635 hat im Norden eine Lücke, wo eigentlich keine sein sollte