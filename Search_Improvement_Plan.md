# Optimierungsplan: Suchalgorithmus & Synonym-Management

Aktuell basiert die Übersetzung von laienhaften Begriffen (z.B. "Kieferschmerzen" -> "Zahnschmerz", "CMD") auf fest codierten Dictionaries in `medical_synonyms.py` und `import_meili.py`. Dies ist auf Dauer unpraktisch, fehleranfällig und extrem schwer wartbar. 

Hier sind die besten strategischen und technischen Ansätze, um den Suchalgorithmus zu verbessern und "Hardcoding" dauerhaft zu eliminieren:

## 1. Datenbankgestütztes Synonym-Management (Kurzfristig realisierbar)
Anstatt die Synonyme im Python-Code zu pflegen, verlagern wir diese in die PostgreSQL-Datenbank (z.B. in eine neue Tabelle `search_synonyms`).
- **Funktionsweise:** Die Tabelle speichert Paare aus `laien_begriff` und einem Array aus `[medizinische_fachbegriffe]`.
- **Vorteile:** Man kann über ein simples Admin-Interface (oder kleine Backend-API) jederzeit neue umgangssprachliche Begriffe und Tippfehler hinzufügen, ohne den Code anzufassen oder den Server neu starten zu müssen.
- **Implementierung:** Beim Start oder periodisch lädt `main.py` und der Meilisearch-Importer das Dictionary aus der DB dynamisch in den Cache.

## 2. Spezialisiertes Medizinisches KI-Modell (Mittelfristig)
Das aktuell verwendete Open-Source Embedding-Modell (`paraphrase-multilingual-MiniLM-L12-v2`) ist generisch auf viele Sprachen trainiert und versteht medizinische Fachausdrücke daher schlecht – genau deshalb müssen wir momentan mit Synonym-Wörterbüchern "aushelfen".
- **Lösung:** Wechsel zu einem klinisch feingetunten deutschen Embedding-Modell (z.B. basierend auf *BioBERT German*, *G-ELECTRA* oder direkt einem kostenpflichtigen aber extrem starken Modell wie *OpenAI `text-embedding-3-small` / Gemini Embeddings*).
- **Vorteile:** Das KI-Modell "weiß" durch sein Training von Natur aus, dass "Kieferschmerzen" in den semantischen Raum von "Zahnschmerzen" oder "Krankheiten des stomatognathen Systems" gehört. **Das manuelle Pflegen von Synonymen entfällt damit fast komplett.**

## 3. Automatischer Import von Medizin-Ontologien (UMLS / SNOMED CT)
Es gibt riesige, staatlich und global gepflegte medizinische Datenbanken, die bereits hunderttausende Laienbegriffe auf ICD-Codes mappen (wie *SNOMED CT* oder das *UMLS*).
- **Lösung:** Wir schreiben ein Import-Skript, das die offiziellen deutschen SNOMED-to-ICD-10 Mappings als Synonyme aggregiert und direkt in Meilisearch lädt.
- **Vorteile:** Nur ein einmaliger Aufwand für den Import-Code. Danach hat man den absoluten Goldstandard der medizinischen Terminologie abgedeckt, ohne selbst Begriffe sammeln zu müssen.

## 4. Dynamische LLM-Query-Expansion mit Caching
Derzeit nutzen wir Gemini nur im "Refined Search" Fallback, wenn Meilisearch scheitert.
- **Lösung:** Gemini analysiert *jede* Suchanfrage. Da LLMs manchmal langsam sind (Latency), fügen wir dafür einen **Redis-Cache** oder eine simple Text-Datenbank-Tabelle hinzu.
- **Funktionsweise:** User sucht "Bauchweh nach fettigem Essen" -> Cache sagt "Kennt das System noch nicht" -> Gemini übersetzt es in "Biliäre Kolik, Cholezystolithiasis" -> Wird sofort gesucht UND für die Zukunft im Cache unter "Bauchweh nach fettigem Essen" verknüpft gespeichert.
- **Vorteile:** Die Synonym-Datenbank baut sich durch echte Nutzersuchen mithilfe der KI komplett selbstständig auf.

## 5. Such-Analyse und "Active Learning" (Langfristig)
Die Suchmaschine lernt aus dem Nutzerverhalten ("Learning to Rank"):
- Wenn ein Nutzer nach "Zahnweh" sucht und nach einigem Scrollen auf das Ergebnis "Krankheiten des Kiefers" klickt, wird dies geloggt.
- Wenn z.B. 5 Nutzer denselben Klickpfad nehmen, evaluiert das System automatisch, dass "Zahnweh" ein perfekter Treffer für dieses Ergebnis ist und verstärkt die Relevanz in Meilisearch.
- **Vorteile:** Das System passt sich organisch an das Vokabular und die Denkweise der Patienten an.

---

### Mein empfohlener Fahrplan für dieses Projekt:
1. **Sofort:** Einrichten einer Datenbank-Tabelle `custom_synonyms`, welche die Python-Datei ersetzt.
2. **Phase 2 (Synonym Auto-Pilot):** Die dynamische LLM-Query-Expansion mit Caching (Ansatz 4) implementieren. Dadurch befüllt die Gemini-KI die gerade erstellte Synonym-Tabelle basierend auf tatsächlichen Nutzersuchen komplett automatisch.
3. **Phase 3:** Längerfristig das `SentenceTransformer` Baseline-Modell in Postgres durch ein echtes medizinisches Embedding Modell (Ansatz 2) ersetzen, falls Ansatz 4 nicht ausreicht.
