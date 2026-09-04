# Spezifikation: Templates für die n8n-Template-Bibliothek aufbereiten

Quelle der Regeln: n8n Template Submission Guidelines (Stand 09/2026), zusammengetragen aus
den offiziellen Richtlinien und dokumentierten Review-Erfahrungen. **Englisch ist Pflicht.**

Zielordner: `submissions/<slug>/` mit zwei Dateien:
- `workflow.json` — die englische Fassung des Workflows
- `description.md` — der Beschreibungstext fürs Portal

## Titel (im JSON-Feld `name`)
- **Maximal 80 Zeichen**, Sentence case (nur erstes Wort und Eigennamen groß)
- **Beginnt mit einem Verb**, das die Aktion beschreibt
- **Nennt die eingesetzten Tools** — und zwar nur solche, die im JSON wirklich vorkommen
- Keine Emojis, keine Superlative
- Muster: `Track meal nutrition with LINE, Google Gemini, and Sheets`

## Beschreibung (`description.md`)
- **Rund 200 Wörter**, reines Markdown (kein HTML), **nur H2-Überschriften**
- Genau diese fünf Abschnitte, in dieser Reihenfolge:
  `## Who is this for` · `## What this workflow does` · `## How to set up` ·
  `## Requirements` · `## How to customize`
- Jedes genannte Tool muss als Node im JSON existieren — sonst Ablehnung

## Sticky Notes im Canvas
- **Eine gelbe Haupt-Notiz oben links** (Position ca. `[-140, -60]`), **100–300 Wörter**,
  mit den Abschnitten `## How it works` und `## Setup steps` (nummeriert).
  Ton: normaler Entwickler, keine gestelzte KI-Sprache, keine Marketingfloskeln.
- **Weiße Abschnitts-Notizen**, je **maximal 50 Wörter**, gruppieren zusammengehörige Nodes.
  Sie dürfen sich **nicht überlappen** — Position und Größe sauber setzen
  (`color: 3` für weiß/grau, Standard ist gelb).
- Kein Link auf die eigene Website in den Notizen — das gilt als Werbung und fliegt raus.
  Die Urheberschaft steht ohnehin am Creator-Profil.

## Sicherheit und Daten
- **Keine Zugangsdaten im JSON**, auch keine `credentials`-Referenzen mit echten IDs
- **Keine personenbezogenen Daten**: keine echten Mailadressen, keine Google-Sheet-IDs,
  keine Telefonnummern. Platzhalter in Großschreibung, z. B. `YOUR_SHEET_ID`,
  `your-team@example.com`, `YOUR_API_ENDPOINT`
- API-Schlüssel gehören in Credentials, niemals in HTTP-Nodes hartkodiert

## Sprache im Workflow
- **Node-Namen englisch**, ebenso Code-Kommentare, Prompts und Beispieldaten
- Beträge in Prompts weiterhin realistisch, aber neutral (EUR ist in Ordnung)

## Häufigste Ablehnungsgründe (vermeiden!)
1. Ein sehr ähnliches Template existiert bereits → Alleinstellung im Titel deutlich machen
2. Titel verletzt die Formatregeln
3. Sticky Notes fehlen, sind zu lang oder überlappen
4. Beschreibung nennt Tools, die im Workflow nicht vorkommen

## Prüfen vor Abgabe
`python3 scripts/validate.py submissions/<slug>/workflow.json` muss „ok" melden.
