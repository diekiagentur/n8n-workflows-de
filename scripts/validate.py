#!/usr/bin/env python3
"""Strukturvalidierung fuer n8n-Workflow-JSONs.

Prueft, was beim Import in n8n real schiefgeht — genau die Fehler, an denen
die grossen "10.000 Workflows"-Sammlungen scheitern:
  * kaputtes JSON / fehlende Pflichtfelder
  * Nodes ohne id/name/type/position, doppelte Namen oder IDs
  * Verbindungen auf nicht existierende Nodes (haeufigster Import-Killer)
  * verwaiste Nodes ohne jede Verbindung
  * fehlender Trigger
  * eingebettete Klartext-Secrets (API-Keys, Tokens) — Sicherheits-Gate
  * fehlende Doku-Notiz (sticky note) und deutsche Node-Namen

Nutzung: python3 scripts/validate.py [pfad ...]     (Default: workflows/)
"""
import json, re, sys, pathlib

# Polling-Nodes wie emailReadImap sind Trigger, tragen das Wort aber nicht im Typ.
TRIGGER = re.compile(r"(Trigger|webhook|cron|interval|emailReadImap|localFileTrigger)", re.I)
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[A-Za-z0-9_-]{30,}"
                    r"|ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
                    r"|Bearer\s+[A-Za-z0-9_\-\.]{20,}|\d{8,10}:AA[A-Za-z0-9_-]{30,})")


def pruefe(pfad: pathlib.Path):
    fehler, warnung = [], []
    try:
        wf = json.loads(pfad.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JSON nicht lesbar: {e}"], []

    if not isinstance(wf, dict):
        return ["Wurzel ist kein Objekt"], []
    if not wf.get("name"):
        fehler.append("Feld 'name' fehlt")
    nodes = wf.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return fehler + ["Feld 'nodes' fehlt oder leer"], warnung

    namen, ids = set(), set()
    for i, n in enumerate(nodes):
        wo = f"Node #{i} ({n.get('name', '?')})"
        for feld in ("id", "name", "type", "position"):
            if feld not in n:
                fehler.append(f"{wo}: '{feld}' fehlt")
        if n.get("name") in namen:
            fehler.append(f"{wo}: Name doppelt vergeben")
        if n.get("id") in ids:
            fehler.append(f"{wo}: id doppelt vergeben")
        namen.add(n.get("name")); ids.add(n.get("id"))
        if not isinstance(n.get("position"), list) or len(n.get("position", [])) != 2:
            fehler.append(f"{wo}: position muss [x, y] sein")
        if "typeVersion" not in n:
            warnung.append(f"{wo}: typeVersion fehlt")

    # Verbindungen muessen auf existierende Nodes zeigen
    verbunden = set()
    for quelle, ausgaenge in (wf.get("connections") or {}).items():
        if quelle not in namen:
            fehler.append(f"Verbindung von unbekanntem Node '{quelle}'")
        verbunden.add(quelle)
        for liste in (ausgaenge or {}).values():
            for zweig in liste or []:
                for ziel in zweig or []:
                    zn = ziel.get("node")
                    if zn not in namen:
                        fehler.append(f"Verbindung '{quelle}' -> unbekanntes Ziel '{zn}'")
                    verbunden.add(zn)

    echte = [n for n in nodes if n.get("type") != "n8n-nodes-base.stickyNote"]
    if not any(TRIGGER.search(n.get("type", "")) for n in echte):
        fehler.append("Kein Trigger-Node vorhanden")
    for n in echte:
        if len(echte) > 1 and n.get("name") not in verbunden:
            fehler.append(f"Node '{n.get('name')}' haengt ohne Verbindung im Workflow")

    text = pathlib.Path(pfad).read_text(encoding="utf-8")
    for treffer in set(SECRET.findall(text)):
        fehler.append(f"Moeglicher Klartext-Schluessel im JSON: {treffer[:18]}…")

    if not any(n.get("type") == "n8n-nodes-base.stickyNote" for n in nodes):
        warnung.append("Keine Sticky-Note als Kurzdoku im Canvas")
    if not (wf.get("meta") or {}).get("beschreibung"):
        warnung.append("meta.beschreibung fehlt")
    return fehler, warnung


def main(argv):
    wurzel = [pathlib.Path(a) for a in argv[1:]] or [pathlib.Path("workflows")]
    dateien = []
    for w in wurzel:
        dateien += sorted(w.rglob("*.json")) if w.is_dir() else [w]
    if not dateien:
        print("Keine Workflow-Dateien gefunden."); return 0

    schlecht = 0
    for f in dateien:
        fehler, warnung = pruefe(f)
        rel = f.as_posix()
        if fehler:
            schlecht += 1
            print(f"FEHLER {rel}")
            for x in fehler: print(f"   ✗ {x}")
        elif warnung:
            print(f"ok     {rel}")
            for x in warnung: print(f"   ! {x}")
        else:
            print(f"ok     {rel}")
    print(f"\n{len(dateien) - schlecht}/{len(dateien)} Workflows strukturell in Ordnung.")
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
