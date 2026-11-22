# C1-Lernapp – Spec

## Kontext
- Nutzerin: Freundin von Nastia, ~40, aus der Ukraine, schreibt **diese Woche** ihre Deutsch-C1-Prüfung (Korrektur: C1, nicht C2) (Goethe oder telc – aus den hochgeladenen Dateien ablesen).
- Ziel: Handy-App zum schnellen Lernen. **Einfach, große Buttons, keine Überladung.** Low effort, aber voll funktional.
- Deadline: in wenigen Stunden nutzbar, nicht perfekt.

## Was Nastia gleich hochlädt
Ihre Texte (Prüfungstexte, eigene Aufsätze, Vokabellisten, evtl. Modelltests).
→ Claude liest sie, sortiert sie in **Texte** (zum Hören) und **Wörter** (Vokabeln/Redemittel) und baut sie direkt in die App ein.

## Tech (bewusst minimal)
- **Eine einzige `index.html`** (HTML + CSS + JS inline), kein Framework, kein Backend, kein Login.
- Speichern im Browser (`localStorage`): Fortschritt, eigene eingefügte Texte.
- Als PWA (Manifest + Icon) → „Zum Home-Bildschirm“ → sieht aus wie eine echte App.
- Hosting: **GitHub Pages** (kostenlos, ein Link).

## Audio – das Wichtigste
Zwei Wege, beide drin:
1. **Vorbereitete MP3s** für ihre hochgeladenen Texte: lokal mit `edge-tts` (kostenlose, natürliche Stimme, z. B. `de-DE-KatjaNeural`) generiert. Vorteil: läuft wie ein Podcast, **auch bei gesperrtem Bildschirm mit Kopfhörern**, Tempo 0.75×/1×/1.25×.
2. **Live-Vorlesen** (Web Speech API) für Texte, die sie später selbst einfügt. Funktioniert sofort, aber stoppt evtl. bei gesperrtem Bildschirm.
- Beim Abspielen wird der aktuelle Satz im Text markiert (Mitlesen).

## 3 Tabs – mehr nicht
| Tab | Was sie macht |
|---|---|
| 🎧 **Hören** | Liste ihrer Texte → antippen → Play/Pause, Tempo, ±10 s. Text darunter zum Mitlesen. Button „Eigenen Text einfügen“. |
| ✍️ **Lücken** | Duolingo-Stil: Satz aus ihren Texten mit 1 Lücke, 4 Wort-Buttons zur Auswahl. Grün/Rot + richtige Lösung + Satz wird vorgelesen. 10 Sätze pro Runde. |
| 🃏 **Wörter** | Karteikarten: Wort/Redemittel → antippen → Bedeutung (Ukrainisch/Deutsch) + Beispielsatz + 🔊. Buttons „Kann ich“ / „Nochmal“. |

Lücken werden automatisch erzeugt: bevorzugt Wörter aus der Vokabelliste, sonst lange Nomen/Verben/Konnektoren (C2-relevant: *nichtsdestotrotz, infolgedessen, …*).

## Mockup (Handy, Tab „Hören“)
```
┌───────────────────────────┐
│  Deutsch C2         🔥 3  │
├───────────────────────────┤
│  Text 2: Klimawandel      │
│                           │
│  Die Debatte um ... ███   │  ← aktueller Satz markiert
│  Nichtsdestotrotz ...     │
│                           │
│   ⏪10    ▶️ PLAY   10⏩   │  ← große Buttons
│   Tempo:  0.75  [1]  1.25 │
├───────────────────────────┤
│  🎧 Hören  ✍️ Lücken  🃏 Wörter │
└───────────────────────────┘
```
Tab „Lücken“:
```
┌───────────────────────────┐
│  Frage 4 / 10   ▓▓▓▓░░░░  │
│                           │
│  Die Maßnahme blieb ____  │
│  wirkungslos.             │
│                           │
│  [ weitgehend ] [ etwa  ] │
│  [ kaum       ] [ sofern] │
│                           │
│        [ PRÜFEN ]         │
└───────────────────────────┘
```

## Design-Regeln
- Schrift min. 18 px, Buttons min. 56 px hoch, hoher Kontrast, heller Modus.
- UI-Sprache Deutsch, kurze Wörter. Keine Einstellungen-Seite, keine Konten.
- Funktioniert auf iPhone (Safari) und Android (Chrome).

## Nicht bauen (bewusst)
Login, Cloud-Sync, KI-Chat, Schreib-Korrektur, Statistiken, Spracheingabe.

## Ablauf, sobald Dateien da sind
1. Dateien lesen → `data.js` mit `texte[]` und `woerter[]` erzeugen.
2. MP3s pro Text mit `edge-tts` generieren (`audio/`).
3. `index.html` bauen, lokal im Browser auf Handygröße testen.
4. Auf GitHub Pages hochladen → Link an sie schicken.

## Anleitung: Wie es auf ihr Handy kommt
**Nastia (einmalig, ~5 Min):**
1. Claude legt ein Repo an und pusht (`gh repo create c2-lernapp --public --source . --push`).
   *Hinweis: Public = Texte sind öffentlich erreichbar über den Link. Wenn das nicht ok ist → Netlify Drop (app.netlify.com/drop, Ordner reinziehen) – Link ist dann nur schwer erratbar.*
2. GitHub → Repo → Settings → Pages → Branch `main` → Save. Nach ~1 Min: `https://<user>.github.io/c2-lernapp/`.
3. Link per WhatsApp/Telegram an sie schicken.

**Sie (einmalig, ~1 Min):**
- **iPhone:** Link in **Safari** öffnen → Teilen-Symbol ⬆️ → „Zum Home-Bildschirm“ → Hinzufügen.
- **Android:** Link in **Chrome** öffnen → ⋮ → „Zum Startbildschirm hinzufügen“.
- Danach einfach das App-Icon antippen. Kopfhörer rein, 🎧 Hören, ▶️.
