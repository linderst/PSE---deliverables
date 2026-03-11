# Testkonzept

Das System besteht aus folgenden Komponenten:

-   ICD‑10 Datenbank
-   Synonym Mapping
-   Suchfunktion (ICD Code oder Synonym)
-   Backend Logik
-   LLM Schnittstelle
-   Web Interface

Die Tests werden auf mehreren Ebenen durchgeführt:

-   Unit Tests
-   Datenbank Tests
-   Integrationstests
-   Installationstests
-   GUI Tests
-   Stress Tests
-   Usability Tests

------------------------------------------------------------------------

# 1. Unit Tests

## Ziel

Überprüfung einzelner Programmkomponenten unabhängig voneinander.

Unit Tests werden mit **pytest** implementiert.

## Komponenten

### ICD Code Detection

Tests prüfen, ob das System erkennt, ob eine Eingabe ein ICD Code ist.

  | Input | Erwartetes Resultat |
  |------|---------------------|
  | E11.9 | als Code erkannt |
  | diabetes | als Text erkannt |

Beispiel:

``` python
def test_detect_icd_code():
    assert detect_code("E11.9") == True
    assert detect_code("diabetes") == False
```

### Synonym Lookup

Tests prüfen, ob Synonyme auf den korrekten ICD Code verweisen.

  |Synonym         | Erwarteter Code
  |---------------- |-----------------
  |Altersdiabetes   |011
  |Herzinfarkt      |021

### Search Routing

Tests prüfen, ob der richtige Suchpfad verwendet wird.

  |Input           |Erwartetes Verhalten
  |----------------|----------------------
  |E11.9           |direkte Code Suche
  |Altersdiabetes  |Synonym Suche

### LLM Prompt Erstellung

Tests prüfen, ob der korrekte ICD Eintrag an das LLM gesendet wird.

``` python
def test_prompt_contains_icd_title():
    prompt = build_prompt("E11.9", "Diabetes mellitus Typ 2")
    assert "Diabetes mellitus Typ 2" in prompt
```

------------------------------------------------------------------------

# 2. Datenbank Tests

## Ziel

Sicherstellen, dass ICD Codes und Synonyme korrekt gespeichert sind.

### Synonym Mapping

Tests prüfen, ob Synonyme korrekt mit ICD Codes verknüpft sind.

  |Synonym           |Erwarteter ICD Code
  |----------------- |---------------------
  |Altersdiabetes    |011
  |Lumboischialgie   |054

### Datenbank Integrität

Überprüfen, ob jedes Synonym auf einen existierenden ICD Code
verweist.

``` sql
SELECT synonym
FROM synonyms
LEFT JOIN icd_codes ON synonyms.code = icd_codes.code
WHERE icd_codes.code IS NULL;
```

Erwartetes Resultat: **0 Ergebnisse**

------------------------------------------------------------------------

# 3. Integrationstests

## Ziel

Überprüfung des Zusammenspiels aller Systemkomponenten.

## Use Case 1 -- Suche nach ICD Code

Input:

    E11.9

Erwartetes Verhalten:

1.  Code wird erkannt
2.  Datenbankeintrag wird geladen
3.  ICD Thema wird an das LLM gesendet
4.  LLM generiert Erklärung

------------------------------------------------------------------------

## Use Case 2 -- Suche nach Synonym

Input:

    Altersdiabetes

Erwartetes Verhalten:

1.  Synonym wird gefunden
2.  ICD Code E11.9 wird ermittelt
3.  ICD Eintrag wird geladen
4.  Erklärung wird generiert

------------------------------------------------------------------------

## Use Case 3 -- Unbekannter Begriff

Input:

    xyzabc

Erwartetes Verhalten:

System zeigt Meldung:

"No matching diagnosis found"

------------------------------------------------------------------------

## Edge Cases

  |Fall              |Erwartetes Verhalten
  |----------------- |----------------------
  |Kleinschreibung   |Suche funktioniert
  |Leerzeichen       |wird ignoriert
  |Teilwort          |wird abgefangen

------------------------------------------------------------------------

# 4. Installationstest

Der Installationstest überprüft, ob das System anhand der
Installationsanleitung korrekt installiert werden kann.
Das finale Produkt soll auf einem Linux server laufen.

Getestete Systeme:

-   Windows
-   macOS
-   Linux

Testschritte:

1.  Repository klonen
2.  Python Dependencies installieren
3.  PostgreSQL starten
4.  ICD Daten importieren
5.  Backend starten
6.  Web Interface öffnen

Erwartetes Ergebnis:

System startet ohne Fehler und die Suche funktioniert.

------------------------------------------------------------------------

# 5. GUI Test

Das GUI wird hauptsächlich **manuell getestet**.

Testfälle:

  |Test                |Erwartetes Ergebnis
  |------------------- |------------------------------
  |ICD Code eingeben   |richtige Krankheit erscheint
  |Synonym eingeben    |richtige Krankheit erscheint
  |Ungültige Eingabe   |Fehlermeldung

Getestet wird:

-   Verständlichkeit
-   Übersichtlichkeit
-   Benutzerfreundlichkeit

------------------------------------------------------------------------

# 6. Stress Test

Ziel ist es zu überprüfen, ob das System mehreren gleichzeitigen
Anfragen standhalten kann.

Test Setup:

-   50-100 gleichzeitige Benutzer

Tools:

-   Locust
-   Apache Benchmark

Gemessen werden:

-   Antwortzeit
-   CPU Auslastung
-   Fehlerrate

Erwartetes Verhalten:

Antwortzeit bleibt unter wenigen Sekunden.

------------------------------------------------------------------------

# 7. Usability Test

## Zielgruppe

Das System richtet sich an **Patienten ohne medizinisches Fachwissen**.

## Testaufgaben

Testpersonen sollen folgende Aufgaben lösen:

1.  

    Finden Sie heraus, was der ICD Code E11.9 bedeutet.

2.  


    Suchen Sie nach Lumboischialgie.

3.  


    Wie wird Diabetes behandelt?

## Bewertet werden

-   Verständlichkeit der Antworten
-   Bedienbarkeit der Suchfunktion
-   Geschwindigkeit der Informationsfindung

Feedback der Testpersonen wird dokumentiert.

------------------------------------------------------------------------

# Dokumentation der Testresultate

Nach Durchführung aller Tests werden dokumentiert:

-   Anzahl der Tests
-   Erfolgreiche Tests
-   Fehlgeschlagene Tests
-   Gefundene Fehler
-   Behobene Fehler

