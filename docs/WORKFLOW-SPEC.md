# Bau-Spezifikation für Workflows in diesem Repo

Arbeitsverzeichnis: `/Users/felixwilhelm/projects/n8n-workflows-de`

## Was dieses Repo von den 10.000er-Ramsch-Sammlungen unterscheidet
Jeder Workflow ist **importierbar, dokumentiert und auf deutsche Betriebe zugeschnitten**.
Lieber 5 exzellente als 50 halbe. Ein Workflow, der beim Import kracht, ist wertlos.

## Pflichtstruktur jeder Datei
`workflows/<kategorie-ordner>/<slug>.json` — gültiges n8n-Workflow-JSON mit:

```
{
  "name": "Sprechender deutscher Titel",
  "meta": {
    "beschreibung": "2–4 Sätze: Was passiert, für wen lohnt es sich, welcher DSGVO-/EU-AI-Act-Hinweis gilt.",
    "kategorie": "…", "schwierigkeit": "einfach|mittel|fortgeschritten",
    "benoetigt": ["Dienst A", "Dienst B"],
    "quelle": "https://die-ki-agentur.de/n8n-agentur/"
  },
  "nodes": [...], "connections": {...},
  "settings": {"executionOrder": "v1"}, "pinData": {}
}
```

## Harte Regeln (der Validator prüft sie)
1. **Genau ein Trigger** pro Workflow (`scheduleTrigger`, `webhook`, `emailReadImap`, `formTrigger`…).
2. **Jeder Node** braucht `id`, `name` (deutsch, eindeutig), `type`, `typeVersion`, `position` `[x,y]`.
3. **Alle `connections` zeigen auf existierende Node-Namen.** Kein Node ohne Verbindung.
4. **Keine echten Zugangsdaten** im JSON. Platzhalter: `HIER_SHEET_ID_EINTRAGEN`, `HIER_WEBHOOK_URL`.
   Credentials-Referenzen weglassen — der Nutzer wählt sie beim Import selbst.
5. **Eine Sticky Note** als Kurzanleitung im Canvas: Ablauf, Voraussetzungen (nummeriert),
   Link `https://die-ki-agentur.de/n8n-agentur/`.
6. Positionen sauber von links nach rechts (x-Abstand ~220), keine Überlappungen.

## Inhaltliche Regeln
- **Deutsch**: Node-Namen, Sticky Note, Prompts, Beispieldaten (Beträge in EUR, Datum TT.MM.JJJJ).
- **Echte Logik statt Attrappe**: Prüfschritte, Fehlerzweige, Plausibilitätschecks einbauen —
  wie im Referenz-Workflow `workflows/02-rechnungen-buchhaltung/eingangsrechnungen-auslesen.json`
  (LESEN, bevor du anfängst — er ist das Qualitätsmuster).
- **Code-Nodes**: kommentiert auf Deutsch, erklären *warum*, nicht *was*.
- **KI-Nodes**: `temperature: 0` bei Extraktion, System-Prompt fordert striktes JSON.
- **DSGVO/EU-AI-Act**: Wo personenbezogene Daten oder KI-Inhalte im Spiel sind, gehört ein
  konkreter Hinweis in `meta.beschreibung` (AV-Vertrag, lokales Modell, Kennzeichnung nach Art. 50).
  Keine Panikmache, keine Rechtsberatung — ein sachlicher Satz.

## Gängige Node-Typen (typeVersion in Klammern)
`n8n-nodes-base.scheduleTrigger` (1.2) · `webhook` (2) · `emailReadImap` (2) · `formTrigger` (2.2)
`httpRequest` (4.2) · `code` (2) · `if` (2) · `switch` (3) · `set` (3.4) · `splitInBatches` (3)
`googleSheets` (4.5) · `emailSend` (2.1) · `telegram` (1.2) · `slack` (2.2) · `extractFromFile` (1)
`@n8n/n8n-nodes-langchain.openAi` (1.8) · `@n8n/n8n-nodes-langchain.agent` (1.7)
`@n8n/n8n-nodes-langchain.lmChatOpenAi` (1.2) · `n8n-nodes-base.stickyNote` (1)

## Abgabe
Nach jedem Workflow: `python3 scripts/validate.py workflows/<datei>` ausführen und Fehler beheben,
bis „ok". Antworte am Ende mit einer Zeile je Workflow: `<pfad>: ok, <n> Nodes` oder `FEHLER <grund>`.
