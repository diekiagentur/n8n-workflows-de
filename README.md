# n8n-Workflows für den deutschen Mittelstand

Praxiserprobte n8n-Automatisierungen auf Deutsch — mit DSGVO- und EU-AI-Act-Hinweisen,
Plausibilitätsprüfungen und einer Kurzanleitung direkt im Canvas.

**Warum noch eine Workflow-Sammlung?** Weil die großen Sammlungen englischsprachig sind und
Masse über Qualität stellen. Hier gilt das Gegenteil: Jeder Workflow ist importierbar
(automatisch validiert), auf deutsche Betriebsabläufe zugeschnitten und dokumentiert.
Wo personenbezogene Daten oder KI-Inhalte im Spiel sind, steht der rechtliche Hinweis dabei.

## Kategorien

| Ordner | Inhalt |
|---|---|
| [`01-vertrieb-leads`](workflows/01-vertrieb-leads) | Leads erfassen, anreichern, nachfassen |
| [`02-rechnungen-buchhaltung`](workflows/02-rechnungen-buchhaltung) | Eingangsrechnungen, Mahnwesen, Vorkontierung |
| [`03-email-kommunikation`](workflows/03-email-kommunikation) | Posteingang sortieren, Entwürfe, Newsletter |
| [`04-ki-agenten-rag`](workflows/04-ki-agenten-rag) | Firmenwissen als RAG, Assistenten, lokale Modelle |
| [`05-marketing-content`](workflows/05-marketing-content) | Social Media, SEO-Briefings |
| [`06-kundenservice`](workflows/06-kundenservice) | FAQ-Chatbot, Reklamationen |
| [`07-daten-reporting`](workflows/07-daten-reporting) | KPI-Berichte, Wettbewerbsbeobachtung |
| [`08-dsgvo-compliance`](workflows/08-dsgvo-compliance) | KI-Inventar, Auskunftsersuchen |
| [`09-handwerk-produktion`](workflows/09-handwerk-produktion) | Terminvorschläge, Wartungsplanung |
| [`10-personal-hr`](workflows/10-personal-hr) | Bewerbungen vorprüfen, Onboarding |

## Verwendung

1. JSON-Datei herunterladen
2. In n8n: **Workflows → Import from File**
3. Zugangsdaten hinterlegen (im JSON stehen bewusst nur Platzhalter, nie echte Schlüssel)
4. Die Sticky Note im Canvas nennt die konkreten Voraussetzungen
5. Erst inaktiv testen, dann scharfschalten

## Qualitätssicherung

Jeder Workflow durchläuft `scripts/validate.py`. Geprüft wird, was beim Import real scheitert:

```bash
python3 scripts/validate.py
```

Kaputtes JSON, Verbindungen auf nicht existierende Nodes, verwaiste Nodes, fehlende Trigger,
doppelte Namen — und ob versehentlich ein echter API-Schlüssel im JSON gelandet ist.

## Rechtliche Hinweise

Die Workflows sind Vorlagen, keine Rechtsberatung. Zwei wiederkehrende Punkte:

- **DSGVO:** Sobald personenbezogene Daten an einen KI-Anbieter gehen, braucht es einen
  Auftragsverarbeitungsvertrag — oder ein lokal betriebenes Modell.
- **EU AI Act:** Die KI-Kompetenzpflicht nach Artikel 4 gilt seit 02.02.2025, die
  Transparenzpflichten nach Artikel 50 und die Hochrisiko-Regeln nach Anhang III seit
  02.08.2026. Chatbots müssen sich als KI zu erkennen geben, KI-generierte Inhalte
  gekennzeichnet werden. Anhang I folgt am 02.08.2027.

Eine ausführliche Einordnung samt kostenlosem Compliance-Kit:
[die-ki-agentur.de/eu-ai-act](https://die-ki-agentur.de/eu-ai-act/)

## Wer dahintersteht

Gepflegt von [**die KI Agentur**](https://die-ki-agentur.de/) aus Hechingen — wir bauen und
betreiben Automatisierungen für mittelständische Unternehmen.

- [n8n-Agentur: Workflows umsetzen lassen](https://die-ki-agentur.de/n8n-agentur/)
- [n8n-Hosting in Deutschland](https://die-ki-agentur.de/n8n-hosting-deutschland/)
- [KI-Schulungen nach Artikel 4 EU AI Act](https://die-ki-agentur.de/ki-schulung/)
- [Kostenloses EU AI Act Compliance Kit (PDF)](https://die-ki-agentur.de/downloads/eu-ai-act-compliance-kit.pdf)

Fragen und Erfahrungsaustausch: [r/ki_agentur](https://www.reddit.com/r/ki_agentur/)

## Beitragen

Pull Requests willkommen. Bitte `docs/WORKFLOW-SPEC.md` lesen und vor dem PR
`python3 scripts/validate.py` laufen lassen.

## Lizenz

MIT — kommerzielle Nutzung ausdrücklich erlaubt. Ohne Gewähr; vor dem Produktiveinsatz testen.
