# Frontend Design-Dokumentation — Medcode (Stand 30.03.2026)

## 1. Technologie-Stack

Komponente/Technologie/Version:
UI-Framwork: React (19.2.0)
Build-Tool: Vite (7.3.1)
Sprache: Javascript (ES2020+)
Styling: CSS
Paketmanager: npm
Laufzeit: Node.js (Docker: 20-alpine)

Die Applikation ist eine **Single Page Application (SPA)** ohne serverseitiges Rendering. Es wird bewusst kein TypeScript und kein externes State-Management (Redux, Zustand etc.) eingesetzt, um die Komplexität gering zu halten.


## 2. Komponentendiagramm

<img width="3709" height="864" alt="Klassendiagram Frontend" src="https://github.com/user-attachments/assets/d7fd4ce3-36e4-4c8f-b53c-f3d6e90a5c65" />



### Erläuterung der Beziehungen

- **App.jsx** ist der einzige Container mit Zustand. Alle anderen Komponenten sind **reine Präsentationskomponenten** (Presentational Components), die ihren Zustand ausschliesslich über Props erhalten.
- **Prop-Drilling** wird bewusst eingesetzt (max. 2 Ebenen tief: App -> HeroView -> AlphabetIndex). Die flache Hierarchie macht Context API oder Zustandsbibliotheken überflüssig.
- **formatText()** wird von InfoBlocks und DialogPanel genutzt, um Gemini-Antworten in HTML umzuwandeln.
- **slugify()** wird von AlphabetIndex für SEO-freundliche URLs verwendet.


## 3. Komponentenbeschreibungen

### App.jsx: Root Container
- **Verantwortlichkeit**: Gesamtes State-Management, API-Kommunikation, Routing, View-Steürung
- **Zeilen**: ~460 (inkl. JSDoc)
- **Enthält**: 15 useState-Hooks, 6 useEffect-Hooks, 5 Handler-Funktionen
- **Muster**: Container-Komponente (besitzt allen Zustand, delegiert Darstellung an Kinder)

### HeroView.jsx: Landing Page
- **Verantwortlichkeit**: Startseite mit Suchfeld und A-Z-Index
- **Props**: 7 (searchTerm, setSearchTerm, handleSearch, cachedConditions, activeLetter, setActiveLetter, handleSelectCondition)
- **Besonderheit**: autoFocus auf dem Suchfeld

### AlphabetIndex.jsx: Navigation
- **Verantwortlichkeit**: Buchstaben-Buttons und gefilterte Diagnose-Liste
- **Abhängigkeiten**: slugify() aus helpers.js
- **Logik**: Extrahiert eindeutige Anfangsbuchstaben aus cachedConditions, filtert nach aktivem Buchstaben

### TopBar.jsx: Ergebnis-Header
- **Verantwortlichkeit**: medcode.ch-Logo (klickbar, zurück zur Startseite) + kompakte Suchleiste
- **Props**: 4 (handleReset, searchTerm, setSearchTerm, handleSearch)

### MatchCard.jsx — Hauptergebnis
- **Verantwortlichkeit**: ICD-10 Code-Badge, Diagnose-Titel, Katalogversion, SVG-Tachometer
- **Abhängigkeiten**: LoadingDots-Komponente
- **Besonderheiten**: Kreisförmiges SVG via `strokeDasharray` für den Konfidenzwert, "KI-verfeinert"-Badge

### OtherMatches.jsx — Alternative Treffer
- **Verantwortlichkeit**: Horizontale Chip-Reihe mit ICD-10-Codes
- **Logik**: Chips mit Score >= 0.95 erhalten grüne Hervorhebung und Häkchen-Badge
- **Tooltip**: Zeigt Diagnosename und Konfidenz-Prozent bei Hover

### InfoBlocks.jsx — KI-Erklärungen
- **Verantwortlichkeit**: 3-Spalten-Grid mit unabhängig ladenden KI-Blöcken
- **Blöcke**: "Was ist das?" / "Wer behandelt das?" / "Wie wird behandelt?"
- **Abhängigkeiten**: formatText() aus helpers.js
- **Besonderheit**: Specialist-Block enthält einen extradoc.ch-Link (Geschäftsanforderung)

### SubcodesPanel.jsx — Unterkategorien
- **Verantwortlichkeit**: Auf-/zuklappbare Liste der 4-stelligen ICD-10-Untercodes
- **Logik**: Berechnet relative Relevanzbalken basierend auf synonym_count (max-normalisiert)

### DialogPanel.jsx — Folgefragen-Chat
- **Verantwortlichkeit**: Chat-Interface für kontextuelle Folgefragen
- **Zustände**: Vor erster Nachricht nur Input-Leiste; danach klappbarer Gesprächsverlauf
- **Abhängigkeiten**: formatText() aus helpers.js, messagesEndRef für Auto-Scroll

### LoadingDots.jsx — Lade-Animation
- **Verantwortlichkeit**: Drei animierte Punkte ("...") mit CSS-Animation "typing-blink"


## 4. State-Management-Konzept

Sämtlicher Zustand ist in `App.jsx` zentralisiert. Die 15 useState-Hooks lassen sich in 5 Kategorien einteilen:

### 4.1 Such- & Ergebnis-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `searchTerm` | string | Aktueller Suchbegriff |
| `currentCondition` | object / null | Hauptergebnis {code, title, version, score} |
| `otherMatches` | array | Alternative Treffer [{code, title, score}] |
| `searchLoading` | boolean | Suche läuft |
| `searchRefined` | boolean | Ergebnis wurde durch Gemini verbessert |
| `searchError` | string / null | Fehlermeldung |
| `longLoading` | boolean | Suche dauert >2.5s (Gemini-Fallback aktiv) |

### 4.2 View-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `view` | 'hero' / 'results' | Aktive Ansicht |
| `activeLetter` | string | Gewahlter Buchstabe im A-Z-Index |

### 4.3 KI-Block-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `explain` | {loading, data, error} | "Was ist das?" Block |
| `specialist` | {loading, data, error} | "Wer behandelt das?" Block |
| `guidance` | {loading, data, error} | "Wie wird behandelt?" Block |
| `disclaimer` | string | Medizinischer Haftungsausschluss (HTML) |

### 4.4 Dialog-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `dialogInput` | string | Eingabefeld-Wert |
| `dialogMessages` | array | Nachrichtenverlauf [{role, text}] |
| `dialogLoading` | boolean | Antwort wird generiert |
| `isChatOpen` | boolean | Gesprächsverlauf ausgeklappt |

### 4.5 Unterkategorie-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `subcodes` | array | ICD-10 Untercodes [{code, title, synonym_count}] |
| `subcodesLoading` | boolean | Untercodes werden geladen |
| `subcodesOpen` | boolean | Panel ist ausgeklappt |

### 4.6 Cache-State

| State | Typ | Beschreibung |
|-------|-----|-------------|
| `cachedConditions` | array | Vorgeladene Diagnosen für A-Z Index |


## 5. Sequenzdiagramme

### 5.1 Suche mit hoher Konfidenz (Score >= 75%)
//TODO noch erstellen


### 5.2 Suche mit KI-Verfeinerung (Score < 75%)

//TODO noch erstellen


### 5.3 Kontextueller Dialog (Folgefragen)

//TODO noch erstellen


### 5.4 URL-basiertes Routing (History API)

//TODO noch erstellen


## 6. Verwendete Entwurfsmuster (Design Patterns)

### Container / Presentational Pattern
- **App.jsx** ist die einzige Container-Komponente (besitzt allen Zustand und die Geschäftslogik).
- Alle anderen Komponenten sind reine Präsentationskomponenten (empfangen Daten und Callbacks als Props, rendern UI).

### Observ```er Pattern (useEffect)
- 6 useEffect-Hooks in App.jsx reagieren auf Zustandsänderungen:
  - SEO-Meta-Tags aktualisieren bei `currentCondition`-änderung
  - Subcodes laden bei `currentCondition.code`-änderung
  - `longLoading`-Timer bei `searchLoading`-änderung
  - Auto-Scroll bei `dialogMessages`-änderung
  - URL-Routing und popstate-Listener beim Mount

### Strategy Pattern (Confidence-Threshold)
- Die Konstante `REFINE_THRESHOLD = 0.75` bestimmt den Suchpfad:
  - Score >= 0.75: Sofortige Ergebnisdarstellung
  - Score < 0.75: Gemini-Verfeinerung mit Fallback

### Facade Pattern (fetchBlock)
- `fetchBlock(endpoint, question, setter)` abstrahiert die API-Kommunikation für alle drei KI-Blöcke hinter einer einheitlichen Schnittstelle. Der Aufrufer muss nur den Endpoint-Suffix und einen State-Setter angeben.

---

## 7. API-Schnittstellen (Frontend-Perspektive)

| Methode | Endpoint | Beschreibung | Aufruf in |
|---------|---------|-------------|-----------|
| GET | `/api/cached-conditions` | Alle vorgeseedeten Diagnosen für A-Z Index | useEffect (Mount) |
| GET | `/api/search?q=...&limit=5` | Schnelle Hybridsuche (Meili + pgvector) | handleSearch() |
| GET | `/api/search/refined?q=...&limit=5` | Gemini-verfeinerte Suche | handleSearch() (Fallback) |
| GET | `/api/subcodes?code=...` | 4-stellige Unterkategorien eines 3-Stellers | useEffect (currentCondition) |
| POST | `/api/chat/explain` | KI-Erklärung "Was ist das?" | fetchBlock() |
| POST | `/api/chat/specialist` | KI-Empfehlung "Wer behandelt das?" | fetchBlock() |
| POST | `/api/chat/guidance` | KI-Leitfaden "Wie wird behandelt?" | fetchBlock() |
| POST | `/api/chat/contextual` | Kontextuelle Folgefrage zum aktuellen Code | handleSendDialog() |

### Request-/Response-Formate

**Suche (GET):**
```
Response: { results: [{ code: "J18", title: "Pneumonie", score: 0.92, version: "2024" }] }
```

**Chat (POST):**
```
Request:  { question: "J18: Pneumonie" }
Response: { answer: "...", disclaimer: true }
```

**Kontextueller Chat (POST):**
```
Request:  { question: "Ist das ansteckend?", condition_code: "J18", condition_title: "Pneumonie" }
Response: { answer: "..." }
```


## 8. CSS-Architektur

### 8.1 Design Tokens (CSS Custom Properties)

//TODO, falls es sich öndert
```css
:root {
  --bg: #f5f5f3;            /* Hintergrund */
  --surface: #ffffff;        /* Karten/Flächen */
  --border: #e8e8e5;        /* Ränder */
  --text: #111110;           /* Primärtext */
  --muted: #7a7a75;          /* Sekundärtext */
  --accent: #2563eb;         /* Primärfarbe (Blau) */
  --accent-hover: #1d4ed8;   /* Primärfarbe Hover */
  --accent-light: #eef3ff;   /* Heller Blau-Hintergrund */
  --code-bg: #eef3ff;        /* Code-Hintergrund */
  --radius: 12px;            /* Standard-Abrundung */
  --font: 'Inter', system-ui; /* Schriftart */
  --shadow-sm/md/lg          /* Box-Schatten (3 Stufen) */
}
```

### 8.2 Responsive Breakpoints

| Breakpoint | Verhalten |
|-----------|----------|
| > 900px | 3-Spalten-Grid für InfoBlocks |
| <= 900px | 1-Spalte, gestapelte Blöcke |

### 8.3 Animationen

| Name | Verwendung | Dauer |
|------|-----------|-------|
| `slide-up-fade` | Einblenden von Elementen (Opacity + TranslateY) | 0.5s |
| `spin` | Lade-Spinner | 0.7s |
| `typing-blink` | LoadingDots-Punkte | 1.4s |

### 8.4 Datei-Organisation

Sämtliches Styling ist in einer einzigen Datei (`App.css`) zentralisiert. Die Klassen folgen einer BEM-ähnlichen Konvention (z.B. `.match-card`, `.match-content`, `.match-code`).


## 9. Testkonzept (Frontend)

### 9.1 Aktueller Stand

//TODO Tests, falls Automatisierte kommen

Das Frontend verfügt derzeit über keine automatisierten Tests. Alle Tests werden manuell durchgeführt:
- Funktionale Tests: Suche nach ICD-Code, Freitext-Symptome, A-Z Index, Folgefragen
- Responsive Tests: Browser-Fenster verkleinern auf < 900px
- Browser-Kompatibilität: Chrome, Firefox, Safari

### 9.2 Backend-Tests 

//TODO falls noch mehr dazukommen

- `src/backend/tests/test_api.py` — API-Endpoint-Tests (pytest + httpx)
- `src/backend/tests/evaluate_search.py` — Suchqualitäts-Evaluation

### 9.3 Empfehlung für zukünftige Erweiterung

Unit Tests (Komponenten) mit React Testing Library + Vitest
Integration Tests (API-Calls) mit MSW (Mock Service Worker) + Vitest
E2E Tests (User-Flows) mit Playwright

## 10. Sicherheitskonzept (Frontend)

### 10.1 CORS
//TODO muss sich noch in Zukunft ändern

- Backend erlaubt aktuell "allow_origins=["*"]"; akzeptabel für die Entwicklungsphase, muss für die Produktion auf die spezifische Domain eingeschränkt werden.

### 10.2 dangerouslySetInnerHTML
- Wird in "InfoBlocks" und "DialogPanel" verwendet, um formatierte KI-Antworten darzustellen.
- Die Inhalte stammen ausschliesslich vom eigenen Backend (Gemini-Antworten). Es gibt keine direkte Nutzereingabe, die als HTML gerendert wird.

### 10.3 API-Key-Handling
- Der Gemini API-Key wird ausschliesslich auf dem Backend in der ".env"-Datei gehalten.
- Das Frontend hat keinen direkten Zugriff auf API-Keys oder Credentials.

### 10.4 Datenschutz
- Keine Suchhistorie: Die Such-Sidebar wurde bewusst entfernt (V1.0), um keine sensiblen Diagnosesuchen zu speichern.
- Kein localStorage/sessionStorage: Es werden keine Nutzerdaten im Browser persistiert.
- Kein Tracking: Keine Analytics- oder Tracking-Scripts eingebunden.
