# Keep an EU AI Act inventory with an AI classifier and monthly reviews

**Eingereicht bei n8n.io am 04.09.2026 (Fassung 2).**

## Verlauf

Fassung 1 wurde am selben Tag abgelehnt: *„It is currently too basic to meet our
publishing criteria."* Acht fachliche Nodes in einer Kette, ein einzelner
OpenAI-Aufruf, ein Trigger — nach n8n-Massstab ein Einsteiger-Workflow.

Fassung 2 (21 fachliche Nodes, zwei Trigger) setzt dort an, wo n8n Substanz erwartet:

- **AI Agent statt Einzelaufruf** — mit Structured-Output-Parser und einem
  Code-Tool `ai_act_reference`, das Anhang III, die verbotenen Praktiken, die
  Geltungstermine und die Bussgeldrahmen nachschlägt. Die Rechtsgrundlage steht
  damit im Werkzeug und nicht im Prompt, und das Modell muss sie nicht auswendig können.
- **Deterministische Gegenprüfung** — ein Regelsatz, der die Einstufung nur nach
  oben korrigieren darf. Sprachmodelle stufen zu niedrig ein: „sortiert Bewerbungen
  vor" klingt harmlos und ist Anhang III, Beschäftigung.
- **Vier Risikopfade** statt einer if-Verzweigung, jeder mit den Pflichten, die
  tatsächlich aus dieser Klasse folgen.
- **Monatlicher Governance-Lauf** — liest das Inventar, sammelt überfällige und
  anstehende Wiedervorlagen sowie offene Entscheidungen und schickt eine Mail.
  Steht nichts an, bleibt er still.

## Zweite Rückmeldung: Layout

Fassung 2 wurde inhaltlich nicht mehr beanstandet, aber zurückgegeben, weil
Notizzettel und Nodes sich auf dem Canvas überlappten — fünf Stellen, gemessen
nachträglich mit demselben Prüfer, der jetzt im Generator sitzt.

Zwei Ursachen, beide vermeidbar:

1. **Notizhöhen geraten.** Eine zu knapp bemessene Notiz lässt den Text über den
   Rand laufen und ihn über dem nächsten Node landen. `sticky()` leitet die Höhe
   jetzt aus dem Text her; der übergebene Wert ist nur noch Untergrenze.
2. **Die Switch-Pfade fächerten in das Notizband hinein.** Positionen sind jetzt
   gestaffelt, und `pruefe_layout()` bricht den Build ab, sobald sich zwei Kästen
   überschneiden — zwischen Node und Notiz zusätzlich mit 60 Einheiten Luft.

Damit ist der Befund nicht mehr eine Frage der Aufmerksamkeit beim Hinsehen,
sondern ein Gate, das kein Build passiert.

## Warum das Thema

Seit dem 02.08.2026 gelten die Transparenzpflichten aus Art. 50 und die
Hochrisiko-Pflichten aus Anhang III. Beide setzen voraus, dass ein Unternehmen
weiss, welche KI-Systeme es betreibt — die Frage, an der die meisten scheitern.

Deutsche Fassung im Repo: [`workflows/08-dsgvo-compliance/ki-inventar-pflegen.json`](../../workflows/08-dsgvo-compliance/ki-inventar-pflegen.json)

## Aufbau

Generiert von `build_v2.py` — das JSON ist von Hand nicht mehr überschaubar,
die Wahrheit über den Workflow steht im Skript.

```bash
python3 build_v2.py
python3 ../../scripts/validate.py workflow.json
```
