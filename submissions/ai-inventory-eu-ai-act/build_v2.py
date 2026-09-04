#!/usr/bin/env python3
"""Erzeugt workflow.json (Fassung 2) fuer die n8n-Template-Bibliothek.

Fassung 1 wurde mit der Begruendung "too basic" abgelehnt: acht fachliche Nodes
in einer Kette, ein einzelner OpenAI-Aufruf, ein Trigger. Diese Fassung setzt
darauf auf, wo n8n Substanz erwartet:

  * ein echter AI Agent mit Structured-Output-Parser und einem Nachschlagewerkzeug
    (Anhang III und die Geltungstermine als Code-Tool statt im Prompt),
  * eine deterministische Gegenpruefung, die dem Modell widersprechen darf,
  * vier Risikopfade statt einer if-Verzweigung,
  * ein zweiter, zeitgesteuerter Governance-Lauf, der das Inventar nachhaelt.

Der Generator existiert, weil das JSON von Hand nicht mehr ueberschaubar waere;
die Wahrheit ueber den Workflow steht in diesem Skript.
"""
import json
import pathlib

Y = 0  # Basiszeile fuer den Intake-Strang
G = 900  # Basiszeile fuer den Governance-Strang


def sticky(id_, x, y, w, h, farbe, text):
    return {
        "parameters": {"width": w, "height": h, "color": farbe, "content": text},
        "id": id_, "name": id_, "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1, "position": [x, y],
    }


REFERENZ = r"""
// Nachschlagewerk zum EU AI Act. Bewusst als Werkzeug und nicht als Prompt-Text:
// so steht die Rechtsgrundlage an einer Stelle und laesst sich pflegen, ohne den
// Systemprompt anzufassen — und das Modell muss sie nicht auswendig koennen.
const nachschlag = {
  annex_iii: [
    'Biometrics: remote biometric identification, categorisation, emotion recognition',
    'Critical infrastructure: safety components in traffic, water, gas, heating, electricity',
    'Education: admission, assessment, monitoring of exams',
    'Employment: recruitment, screening, promotion, termination, task allocation',
    'Essential services: creditworthiness, insurance pricing, emergency triage, public benefits',
    'Law enforcement: risk assessment of persons, evidence evaluation, profiling',
    'Migration and border control: visa and asylum assessment, risk assessment',
    'Justice and democracy: assisting judicial decisions, influencing elections',
  ],
  prohibited_article_5: [
    'Subliminal or manipulative techniques distorting behaviour to a persons detriment',
    'Exploiting vulnerabilities of age, disability or social or economic situation',
    'Social scoring by public or private actors leading to detrimental treatment',
    'Predicting criminal offences solely from profiling or personality traits',
    'Untargeted scraping of facial images to build recognition databases',
    'Emotion recognition at the workplace or in education, outside safety or medical use',
    'Biometric categorisation inferring race, political opinion, religion or sexual orientation',
    'Real-time remote biometric identification in public spaces for law enforcement',
  ],
  transparency_article_50: [
    'People must be told when they interact with an AI system, unless it is obvious',
    'Synthetic audio, image, video and text must be marked as machine-readable',
    'Deep fakes must be disclosed; emotion recognition must be disclosed to those exposed',
  ],
  dates: {
    '2025-02-02': 'Prohibited practices (Art. 5) and AI literacy duty (Art. 4) apply',
    '2025-08-02': 'GPAI obligations, governance structure and penalties apply',
    '2026-08-02': 'Transparency duties (Art. 50) and Annex III high-risk duties apply',
    '2027-08-02': 'High-risk duties for AI in regulated products (Annex I) apply',
  },
  penalties: {
    prohibited: 'up to EUR 35m or 7% of worldwide annual turnover',
    other_obligations: 'up to EUR 15m or 3%',
    misleading_information: 'up to EUR 7.5m or 1%',
  },
};

// Der Agent uebergibt ein Stichwort; ohne Treffer bekommt er alles zurueck,
// damit eine unglueckliche Suchanfrage nicht in einer leeren Antwort endet.
const frage = String(query || '').toLowerCase();
if (!frage) return JSON.stringify(nachschlag);
const treffer = {};
for (const [schluessel, wert] of Object.entries(nachschlag)) {
  if (schluessel.includes(frage)) { treffer[schluessel] = wert; continue; }
  if (Array.isArray(wert)) {
    const zeilen = wert.filter((z) => z.toLowerCase().includes(frage));
    if (zeilen.length) treffer[schluessel] = zeilen;
  }
}
return JSON.stringify(Object.keys(treffer).length ? treffer : nachschlag);
"""

NORMALISIEREN = r"""
// Formulareingaben aufraeumen, bevor sie an das Modell gehen: getrimmt, gedeckelt
// und mit einer stabilen ID, an der sich der Eintrag spaeter wiederfinden laesst.
const kuerzen = (wert, max) => String(wert ?? '').replace(/\s+/g, ' ').trim().slice(0, max);

return items.map((item) => {
  const f = item.json;
  const name = kuerzen(f['System name'], 120);
  const kennung = (name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'system')
    + '-' + String(Date.now()).slice(-6);

  return {
    json: {
      record_id: kennung,
      reported_at: new Date().toISOString(),
      system_name: name,
      department: kuerzen(f['Department'], 80),
      purpose: kuerzen(f['What does it do?'], 800),
      data_categories: kuerzen(f['Which data does it process?'], 400),
      affects_people: kuerzen(f['Does it affect people?'], 60),
      vendor: kuerzen(f['Vendor or model'], 120),
      owner_email: kuerzen(f['Who is responsible?'], 120),
      // Das Modell sieht nur diesen Block — ein Feld pro Zeile liest es zuverlaessiger
      // als einen Fliesstext, in dem Angaben ineinanderlaufen.
      briefing: [
        'System: ' + name,
        'Department: ' + kuerzen(f['Department'], 80),
        'Purpose: ' + kuerzen(f['What does it do?'], 800),
        'Data processed: ' + kuerzen(f['Which data does it process?'], 400),
        'Affects people: ' + kuerzen(f['Does it affect people?'], 60),
        'Vendor or model: ' + kuerzen(f['Vendor or model'], 120),
      ].join('\n'),
    },
  };
});
"""

GEGENPRUEFUNG = r"""
// Deterministische Gegenpruefung. Ein Sprachmodell stuft im Zweifel zu niedrig ein,
// weil harmlos formulierte Beschreibungen harmlos klingen. Diese Regeln duerfen die
// Einstufung deshalb nur nach OBEN korrigieren, nie nach unten.
const HOCH = [
  ['recruit', 'employment'], ['applicant', 'employment'], ['cv ', 'employment'],
  ['resume', 'employment'], ['promotion', 'employment'], ['performance review', 'employment'],
  ['credit', 'essential services'], ['scoring', 'essential services'],
  ['insurance', 'essential services'], ['triage', 'essential services'],
  ['exam', 'education'], ['admission', 'education'], ['grading', 'education'],
  ['biometric', 'biometrics'], ['face', 'biometrics'], ['fingerprint', 'biometrics'],
  ['emergency', 'essential services'], ['border', 'migration'], ['asylum', 'migration'],
];
const VERBOTEN = [
  ['social scoring', 'social scoring'], ['emotion', 'emotion recognition'],
  ['predict crime', 'predictive policing'], ['scrape face', 'facial scraping'],
];
const RANG = { minimal: 0, limited: 1, high: 2, prohibited: 3 };

return items.map((item) => {
  const d = item.json;
  // Der Agent liefert das Ergebnis je nach n8n-Version unter output oder direkt.
  const modell = d.output ?? d;
  const quelle = ($('Normalize the report').first().json.briefing || '').toLowerCase();

  const treffer_hoch = HOCH.filter(([w]) => quelle.includes(w)).map(([, k]) => k);
  const treffer_verboten = VERBOTEN.filter(([w]) => quelle.includes(w)).map(([, k]) => k);

  let klasse = String(modell.risk_class || 'unclear').toLowerCase();
  const vorschlag = klasse;
  const hinweise = [];

  if (treffer_verboten.length && RANG[klasse] < RANG.prohibited) {
    klasse = 'prohibited';
    hinweise.push('Raised to prohibited: wording matches ' + treffer_verboten.join(', '));
  } else if (treffer_hoch.length && RANG[klasse] < RANG.high) {
    klasse = 'high';
    hinweise.push('Raised to high: wording matches Annex III area ' + treffer_hoch.join(', '));
  }
  if (!(klasse in RANG)) { klasse = 'high'; hinweise.push('Model returned an unknown class — treated as high until reviewed'); }

  const zuversicht = Number(modell.confidence ?? 0);
  if (zuversicht < 0.6) hinweise.push('Low model confidence (' + zuversicht.toFixed(2) + ')');

  return {
    json: {
      ...$('Normalize the report').first().json,
      risk_class: klasse,
      model_proposal: vorschlag,
      article: String(modell.article || ''),
      reasoning: String(modell.reasoning || '').slice(0, 900),
      obligations: Array.isArray(modell.obligations) ? modell.obligations.join('; ') : String(modell.obligations || ''),
      confidence: zuversicht,
      // Jede Korrektur, jede unsichere Einstufung und alles ab "high" geht an einen Menschen.
      human_review: hinweise.length > 0 || RANG[klasse] >= RANG.high,
      review_notes: hinweise.join(' | ') || 'Model classification accepted without correction',
      next_review: new Date(Date.now() + (RANG[klasse] >= RANG.high ? 90 : 180) * 864e5)
        .toISOString().slice(0, 10),
    },
  };
});
"""

FAELLIG = r"""
// Faellige Wiedervorlagen und stehengebliebene Pruefungen aus dem Inventar ziehen.
// Ein Inventar, das niemand nachhaelt, ist zum Stichtag genauso wertlos wie keines.
const heute = new Date().toISOString().slice(0, 10);
const in14 = new Date(Date.now() + 14 * 864e5).toISOString().slice(0, 10);

const faellig = [], offen = [], hochrisiko = [];
for (const item of items) {
  const z = item.json;
  if (!z.system_name) continue;
  if (String(z.human_review).toLowerCase() === 'true') offen.push(z);
  if (z.risk_class === 'high' || z.risk_class === 'prohibited') hochrisiko.push(z);
  if (z.next_review && z.next_review <= in14) faellig.push({ ...z, overdue: z.next_review < heute });
}

return [{
  json: {
    generated_at: heute,
    total: items.filter((i) => i.json.system_name).length,
    due_count: faellig.length,
    open_review_count: offen.length,
    high_risk_count: hochrisiko.length,
    // Nur wenn wirklich etwas ansteht, geht spaeter eine Mail raus.
    has_work: faellig.length + offen.length > 0,
    due: faellig,
    open_reviews: offen,
  },
}];
"""

BERICHT = r"""
// Aus den faelligen Punkten eine Mail bauen, die man ohne Nachfragen abarbeiten kann:
// zuerst was ueberfaellig ist, dann was ansteht, dann die Zahlen.
const d = items[0].json;
const zeile = (z) => '<tr><td>' + z.system_name + '</td><td>' + (z.department || '-') +
  '</td><td>' + (z.risk_class || '-') + '</td><td>' + (z.next_review || '-') +
  '</td><td>' + (z.overdue ? 'overdue' : 'due') + '</td></tr>';

const tabelle = (titel, zeilen) => !zeilen.length ? '' :
  '<h3>' + titel + '</h3><table border="1" cellpadding="6" cellspacing="0">' +
  '<tr><th>System</th><th>Department</th><th>Risk class</th><th>Review date</th><th>Status</th></tr>' +
  zeilen.map(zeile).join('') + '</table>';

const ueberfaellig = d.due.filter((z) => z.overdue);
const anstehend = d.due.filter((z) => !z.overdue);

const html = [
  '<p>AI inventory status for ' + d.generated_at + '.</p>',
  '<ul>',
  '<li>' + d.total + ' systems in the inventory</li>',
  '<li>' + d.high_risk_count + ' classified high risk or prohibited</li>',
  '<li>' + d.open_review_count + ' still waiting for a human decision</li>',
  '</ul>',
  tabelle('Overdue reviews', ueberfaellig),
  tabelle('Due within 14 days', anstehend),
  tabelle('Waiting for a human decision', d.open_reviews),
  '<p>Reminder of the milestones: transparency duties under Art. 50 and the Annex III ',
  'high-risk duties have applied since 2 August 2026; Annex I products follow on ',
  '2 August 2027. Penalties reach EUR 35m or 7% of worldwide turnover for prohibited practices.</p>',
].join('\n');

return [{ json: { ...d, subject: 'AI inventory: ' + d.due_count + ' reviews due, ' +
  d.open_review_count + ' open decisions', html } }];
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "risk_class": {"type": "string", "enum": ["prohibited", "high", "limited", "minimal", "unclear"]},
        "article": {"type": "string", "description": "The article or annex the classification rests on, e.g. 'Annex III(4) employment'"},
        "reasoning": {"type": "string", "description": "Two or three sentences, naming the decisive fact"},
        "obligations": {"type": "array", "items": {"type": "string"}, "description": "Concrete duties that follow from this class"},
        "confidence": {"type": "number", "description": "0 to 1; below 0.6 the case goes to a human"},
        "missing_information": {"type": "string", "description": "What the report failed to state, empty if nothing"},
    },
    "required": ["risk_class", "article", "reasoning", "obligations", "confidence"],
}

SYSTEMPROMPT = (
    "You are a compliance analyst classifying an AI system under Regulation (EU) 2024/1689 "
    "(the EU AI Act) for a European company.\n\n"
    "Method — follow it in this order:\n"
    "1. Call the tool `ai_act_reference` before you decide. Query it with a single keyword such as "
    "`prohibited`, `annex_iii`, `transparency` or the application area (`employment`, `credit`, "
    "`biometric`). Never rely on memory for the wording of the Act.\n"
    "2. Check the prohibited practices of Art. 5 first. They override everything else.\n"
    "3. Then check whether the described use falls into an Annex III area. Judge the actual use, "
    "not the vendor's marketing: a general purpose model becomes high risk through what it is "
    "used for.\n"
    "4. Only then consider the transparency duties of Art. 50 (limited risk) and, if nothing "
    "applies, minimal risk.\n\n"
    "Rules:\n"
    "- Classify what is described, never what you assume the company probably also does.\n"
    "- If a decisive fact is missing, say so in `missing_information`, lower your `confidence` "
    "and pick the higher of the two plausible classes. Under-classification is the expensive "
    "mistake here, not over-classification.\n"
    "- `obligations` must be actionable for the named system — 'set up a risk management system "
    "under Art. 9' rather than 'comply with the Act'.\n"
    "- Write in English, plainly, without hedging phrases. This text goes into a register that "
    "an auditor may read.\n\n"
    "You are not giving legal advice. Your output is a first pass that a responsible human "
    "confirms or overrides."
)


def main():
    nodes = []
    conns = {}

    def verbinde(von, nach, typ="main", index=0, ausgang=0):
        conns.setdefault(von, {}).setdefault(typ, [])
        while len(conns[von][typ]) <= ausgang:
            conns[von][typ].append([])
        conns[von][typ][ausgang].append({"node": nach, "type": typ, "index": index})

    def node(name, typ, version, x, y, params, extra=None):
        n = {"parameters": params, "id": name.lower().replace(" ", "-").replace("?", ""),
             "name": name, "type": typ, "typeVersion": version, "position": [x, y]}
        if extra:
            n.update(extra)
        nodes.append(n)
        return name

    # ---------- Strang 1: Meldung entgegennehmen und einstufen ----------
    node("Report an AI system", "n8n-nodes-base.formTrigger", 2.2, -260, Y, {
        "formTitle": "Report an AI system",
        "formDescription": ("Every AI system used in the company has to be listed — bought, "
                            "built or embedded in another tool. Two minutes now save a scramble "
                            "before the next audit."),
        "formFields": {"values": [
            {"fieldLabel": "System name", "requiredField": True},
            {"fieldLabel": "Department", "requiredField": True},
            {"fieldLabel": "What does it do?", "fieldType": "textarea", "requiredField": True,
             "placeholder": "Plain language: what goes in, what comes out, who acts on the result"},
            {"fieldLabel": "Which data does it process?", "fieldType": "textarea", "requiredField": True},
            {"fieldLabel": "Does it affect people?", "fieldType": "dropdown", "requiredField": True,
             "fieldOptions": {"values": [
                 {"option": "It decides about people"},
                 {"option": "It prepares a decision about people"},
                 {"option": "It does not touch people at all"}]}},
            {"fieldLabel": "Vendor or model", "requiredField": True},
            {"fieldLabel": "Who is responsible?", "fieldType": "email", "requiredField": True},
        ]},
        "options": {},
    })

    node("Normalize the report", "n8n-nodes-base.code", 2, -40, Y,
         {"jsCode": NORMALISIEREN.strip()})

    node("Classify against the EU AI Act", "@n8n/n8n-nodes-langchain.agent", 1.7, 200, Y, {
        "promptType": "define",
        "text": "={{ $json.briefing }}",
        "hasOutputParser": True,
        "options": {"systemMessage": SYSTEMPROMPT},
    })
    node("Language model", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, 120, Y + 220,
         {"model": {"__rl": True, "value": "gpt-4.1-mini", "mode": "list"},
          "options": {"temperature": 0}})
    node("Structured classification", "@n8n/n8n-nodes-langchain.outputParserStructured", 1.2,
         320, Y + 220,
         {"schemaType": "manual", "inputSchema": json.dumps(SCHEMA, indent=2)})
    node("ai_act_reference", "@n8n/n8n-nodes-langchain.toolCode", 1.1, 500, Y + 220, {
        "name": "ai_act_reference",
        "description": ("Look up the EU AI Act. Query with one keyword: prohibited, annex_iii, "
                        "transparency, dates, penalties, or an application area such as "
                        "employment, credit, biometric."),
        # Ohne eigenes Input-Schema reicht n8n den Aufruf als String in `query` durch —
        # genau das, was der Code unten erwartet. Ein Schema wuerde ein Objekt liefern.
        "jsCode": REFERENZ.strip(),
    })

    node("Cross-check the classification", "n8n-nodes-base.code", 2, 480, Y,
         {"jsCode": GEGENPRUEFUNG.strip()})

    node("Route by risk class", "n8n-nodes-base.switch", 3, 720, Y, {
        "rules": {"values": [
            {"conditions": {"options": {"caseSensitive": False, "version": 2},
                            "conditions": [{"leftValue": "={{ $json.risk_class }}", "rightValue": "prohibited",
                                            "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"}, "outputKey": "prohibited"},
            {"conditions": {"options": {"caseSensitive": False, "version": 2},
                            "conditions": [{"leftValue": "={{ $json.risk_class }}", "rightValue": "high",
                                            "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"}, "outputKey": "high"},
            {"conditions": {"options": {"caseSensitive": False, "version": 2},
                            "conditions": [{"leftValue": "={{ $json.risk_class }}", "rightValue": "limited",
                                            "operator": {"type": "string", "operation": "equals"}}],
                            "combinator": "and"}, "outputKey": "limited"},
        ]},
        "options": {"fallbackOutput": "extra", "renameFallbackOutput": "minimal"},
    })

    pfade = [
        ("Stop and escalate", 0, 960, Y - 300,
         "Do not put this system into use. Art. 5 practices have been banned since "
         "2 February 2025; penalties reach EUR 35m or 7% of worldwide annual turnover. "
         "Document the decision and, if the system is already running, switch it off.",
         "Prohibited practice reported: "),
        ("Assign high-risk duties", 1, 960, Y - 110,
         "High-risk duties apply: risk management under Art. 9, data governance under Art. 10, "
         "technical documentation under Art. 11, logging under Art. 12, human oversight under "
         "Art. 14, and registration in the EU database. Annex III duties have applied since "
         "2 August 2026.",
         "High-risk AI system reported: "),
        ("Assign transparency duties", 2, 960, Y + 80,
         "Transparency duties under Art. 50 apply: tell people they are dealing with an AI "
         "system, mark synthetic content machine-readably, disclose deep fakes. In force since "
         "2 August 2026.", None),
        ("Log as minimal risk", 3, 960, Y + 270,
         "No specific duties beyond the AI literacy obligation of Art. 4, in force since "
         "2 February 2025. Keep the entry — classifications change when the use changes.", None),
    ]
    for name, ausgang, x, y, duties, betreff in pfade:
        node(name, "n8n-nodes-base.set", 3.4, x, y, {
            "assignments": {"assignments": [
                {"id": "duties", "name": "duties", "value": duties, "type": "string"},
                {"id": "action", "name": "action_required",
                 "value": "true" if betreff else "false", "type": "string"},
            ]},
            "options": {},
        })
        verbinde("Route by risk class", name, ausgang=ausgang)
        verbinde(name, "Append to the AI inventory")
        if betreff:
            verbinde(name, "Notify the responsible manager")

    node("Notify the responsible manager", "n8n-nodes-base.emailSend", 2.1, 1220, Y - 210, {
        "fromEmail": "ai-governance@example.com",
        "toEmail": "={{ $json.owner_email }}",
        "subject": "={{ $json.risk_class === 'prohibited' ? 'Prohibited practice reported: ' : 'High-risk AI system reported: ' }}{{ $json.system_name }}",
        "emailFormat": "text",
        "text": "={{ $json.system_name }} ({{ $json.department }}) was classified as {{ $json.risk_class }} risk.\n\n"
                "Basis: {{ $json.article }}\n{{ $json.reasoning }}\n\n"
                "Duties:\n{{ $json.duties }}\n\n"
                "Obligations proposed by the classifier:\n{{ $json.obligations }}\n\n"
                "Review notes: {{ $json.review_notes }}\n"
                "Model proposal was: {{ $json.model_proposal }} (confidence {{ $json.confidence }})\n\n"
                "This classification is a first pass. Confirm or override it, then set human_review to false in the inventory.",
        "options": {},
    })

    node("Append to the AI inventory", "n8n-nodes-base.googleSheets", 4.5, 1220, Y + 90, {
        "operation": "append",
        "documentId": {"__rl": True, "value": "", "mode": "list"},
        "sheetName": {"__rl": True, "value": "", "mode": "list"},
        "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": []},
        "options": {},
    })

    # ---------- Strang 2: Governance-Lauf ----------
    node("Every month", "n8n-nodes-base.scheduleTrigger", 1.2, -260, G,
         {"rule": {"interval": [{"field": "months", "triggerAtDayOfMonth": 1, "triggerAtHour": 7}]}})
    node("Read the inventory", "n8n-nodes-base.googleSheets", 4.5, -40, G, {
        "documentId": {"__rl": True, "value": "", "mode": "list"},
        "sheetName": {"__rl": True, "value": "", "mode": "list"},
        "options": {},
    })
    node("Find what is due", "n8n-nodes-base.code", 2, 200, G, {"jsCode": FAELLIG.strip()})
    node("Anything to do?", "n8n-nodes-base.if", 2, 440, G, {
        "conditions": {"options": {"caseSensitive": True, "version": 2},
                       "conditions": [{"leftValue": "={{ $json.has_work }}", "rightValue": "true",
                                       "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                       "combinator": "and"},
        "options": {},
    })
    node("Build the review report", "n8n-nodes-base.code", 2, 680, G - 110, {"jsCode": BERICHT.strip()})
    node("Send the governance report", "n8n-nodes-base.emailSend", 2.1, 920, G - 110, {
        "fromEmail": "ai-governance@example.com",
        "toEmail": "compliance@example.com",
        "subject": "={{ $json.subject }}",
        "emailFormat": "html",
        "html": "={{ $json.html }}",
        "options": {},
    })
    node("Nothing due this month", "n8n-nodes-base.noOp", 1, 680, G + 110, {})

    verbinde("Report an AI system", "Normalize the report")
    verbinde("Normalize the report", "Classify against the EU AI Act")
    verbinde("Language model", "Classify against the EU AI Act", "ai_languageModel")
    verbinde("Structured classification", "Classify against the EU AI Act", "ai_outputParser")
    verbinde("ai_act_reference", "Classify against the EU AI Act", "ai_tool")
    verbinde("Classify against the EU AI Act", "Cross-check the classification")
    verbinde("Cross-check the classification", "Route by risk class")
    verbinde("Every month", "Read the inventory")
    verbinde("Read the inventory", "Find what is due")
    verbinde("Find what is due", "Anything to do?")
    verbinde("Anything to do?", "Build the review report", ausgang=0)
    verbinde("Anything to do?", "Nothing due this month", ausgang=1)
    verbinde("Build the review report", "Send the governance report")

    # ---------- Erklaerende Zettel ----------
    nodes += [
        sticky("Overview", -300, Y - 620, 760, 300, 4,
               "## Keep an EU AI Act inventory that survives an audit\n\n"
               "Art. 4 has required AI literacy since 2 February 2025, and since 2 August 2026 "
               "the transparency duties of Art. 50 and the Annex III high-risk duties apply. "
               "Both start with one question a company has to be able to answer: **which AI "
               "systems are we actually running?**\n\n"
               "This workflow answers it continuously. Colleagues report a system through a form, "
               "an agent classifies it against the Act, a rule set checks the agent, and a monthly "
               "run makes sure nobody's entry quietly goes stale.\n\n"
               "**Setup:** OpenAI credentials, a Google Sheet with a header row matching the "
               "fields, and an SMTP account. Replace the two example addresses. Nothing else."),
        sticky("Intake", -300, Y - 260, 400, 220, 7,
               "### 1 — Intake\n\nThe form is deliberately short: seven fields, plain wording, no "
               "legal vocabulary. People fill in what they know; the classification is not their job.\n\n"
               "The Code node trims the input and builds one briefing block per system — a model "
               "reads field-per-line far more reliably than prose."),
        sticky("Classification", 140, Y - 260, 560, 220, 5,
               "### 2 — Classification, then contradiction\n\nThe agent looks the Act up through the "
               "`ai_act_reference` tool instead of reciting it from memory, and returns a structured "
               "verdict.\n\n**The Code node afterwards may only raise the class, never lower it.** "
               "Language models under-classify: a recruiting tool described as \"pre-sorting "
               "applications\" sounds harmless and is Annex III employment. Whatever it corrects, "
               "and anything above limited risk, is flagged for a human."),
        sticky("Routing", 700, Y - 260, 700, 220, 3,
               "### 3 — Four paths, not a yes/no\n\nEach class carries different duties, so each gets "
               "its own branch and its own text — the person who reported the system receives "
               "something actionable, not a label.\n\nProhibited and high-risk cases also alert the "
               "responsible manager. Everything lands in the same sheet: the inventory is the point."),
        sticky("Governance", -300, G - 300, 1300, 240, 6,
               "### 4 — The part most inventories skip\n\nA register built once and never touched is "
               "worthless on the day it matters. On the first of each month this branch reads the "
               "sheet, collects overdue reviews, upcoming ones and entries still waiting for a human "
               "decision, and mails a single summary — and stays silent when there is nothing to do, "
               "so the mail keeps meaning something.\n\nReview cadence: 90 days for high risk and "
               "prohibited, 180 days for the rest."),
    ]

    wf = {
        "name": "Keep an EU AI Act inventory with an AI classifier and monthly reviews",
        "nodes": nodes,
        "connections": conns,
        "settings": {"executionOrder": "v1"},
        "pinData": {},
    }
    ziel = pathlib.Path(__file__).parent / "workflow.json"
    ziel.write_text(json.dumps(wf, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    fach = [n for n in nodes if n["type"] != "n8n-nodes-base.stickyNote"]
    print(f"=> {ziel.name}: {len(fach)} fachliche Nodes, {len(nodes) - len(fach)} Notizen, "
          f"{len(conns)} Verbindungsquellen")


if __name__ == "__main__":
    main()
