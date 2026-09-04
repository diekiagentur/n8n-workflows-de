#!/usr/bin/env python3
"""Baut aus den Repo-Workflows eine statische Uebersichtsseite fuer GitHub Pages.

Ergebnis landet in build/ und wird von scripts/pages_deploy.sh in den
gh-pages-Branch gespiegelt. Die Metadaten kommen aus der Website
(src/data/n8n-workflows.json) — dort werden sie ohnehin gepflegt, eine zweite
Quelle waere sofort auseinandergelaufen.
"""
import html
import json
import pathlib
import shutil

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = pathlib.Path.home() / "projects" / "die-ki-agentur"
META = SITE / "src" / "data" / "n8n-workflows.json"
BUILD = REPO / "build"

WEB = "https://die-ki-agentur.de"
GH = "https://github.com/diekiagentur/n8n-workflows-de"
RAW = "https://raw.githubusercontent.com/diekiagentur/n8n-workflows-de/main"

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{--blau:#2563EB;--blau-d:#1D4ED8;--tinte:#0F172A;--grau:#475569;
      --linie:#E2E8F0;--flaeche:#F8FAFC;--weiss:#fff}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--weiss);color:var(--tinte);
     font:400 17px/1.65 Poppins,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
a{color:var(--blau-d)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header{background:var(--flaeche);border-bottom:1px solid var(--linie);padding:56px 0 44px}
h1{font-size:clamp(28px,4.2vw,42px);line-height:1.2;margin:0 0 14px;letter-spacing:-.02em}
.lead{font-size:19px;color:var(--grau);margin:0 0 22px;max-width:62ch}
.marken{display:flex;flex-wrap:wrap;gap:10px;align-items:center;font-size:14px;color:var(--grau)}
.knopf{display:inline-block;background:var(--blau);color:#fff;text-decoration:none;
       padding:11px 20px;border-radius:8px;font-weight:600;font-size:15px}
.knopf:hover{background:var(--blau-d)}
.knopf.leer{background:transparent;color:var(--blau-d);border:1px solid var(--linie)}
.werkzeug{display:flex;flex-wrap:wrap;gap:10px;margin:32px 0 8px}
#suche{flex:1 1 260px;min-width:0;padding:11px 14px;border:1px solid var(--linie);
       border-radius:8px;font:inherit;font-size:15px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 34px}
.chip{border:1px solid var(--linie);background:var(--weiss);color:var(--grau);
      padding:7px 13px;border-radius:999px;font:inherit;font-size:14px;cursor:pointer}
.chip[aria-pressed=true]{background:var(--blau);border-color:var(--blau);color:#fff}
.gitter{display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));
        padding-bottom:56px;margin:0;list-style:none}
.karte{border:1px solid var(--linie);border-radius:12px;overflow:hidden;
       display:flex;flex-direction:column;background:var(--weiss)}
.karte img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;background:var(--flaeche)}
.karte .inhalt{padding:18px 20px 20px;display:flex;flex-direction:column;flex:1}
.kat{font-size:13px;color:var(--blau-d);font-weight:600;margin:0 0 6px}
.karte h2{font-size:19px;line-height:1.35;margin:0 0 10px;letter-spacing:-.01em}
.karte p{font-size:15px;color:var(--grau);margin:0 0 14px}
.meta{font-size:13px;color:var(--grau);margin:0 0 16px}
.aktionen{margin-top:auto;display:flex;flex-wrap:wrap;gap:9px}
.aktionen a{font-size:14px;text-decoration:none;padding:8px 14px;border-radius:7px;
            border:1px solid var(--linie);color:var(--blau-d);font-weight:500}
.aktionen a.haupt{background:var(--blau);border-color:var(--blau);color:#fff}
.leerzustand{color:var(--grau);padding:24px 0}
footer{border-top:1px solid var(--linie);background:var(--flaeche);padding:36px 0;
       font-size:15px;color:var(--grau)}
footer p{margin:0 0 10px;max-width:70ch}
@media (max-width:600px){header{padding:38px 0 30px}body{font-size:16px}}
"""

JS = """
(function(){
  var suche=document.getElementById('suche');
  var chips=Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var karten=Array.prototype.slice.call(document.querySelectorAll('.karte'));
  var leer=document.getElementById('leer');
  var kat='';
  function filtern(){
    var q=suche.value.toLowerCase().trim(), sichtbar=0;
    karten.forEach(function(k){
      var passt=(!kat||k.dataset.kat===kat)&&(!q||k.dataset.text.indexOf(q)>-1);
      k.hidden=!passt; if(passt)sichtbar++;
    });
    leer.hidden=sichtbar>0;
  }
  suche.addEventListener('input',filtern);
  chips.forEach(function(c){c.addEventListener('click',function(){
    var an=c.getAttribute('aria-pressed')==='true';
    chips.forEach(function(x){x.setAttribute('aria-pressed','false')});
    kat=an?'':c.dataset.kat;
    if(!an)c.setAttribute('aria-pressed','true');
    filtern();
  })});
})();
"""


def e(s):
    return html.escape(str(s), quote=True)


def karte(w):
    bild = f"thumbnails/{w['slug']}.jpg"
    kurz = w["beschreibung"].split(" DSGVO/EU-AI-Act-Hinweis:")[0]
    if len(kurz) > 230:
        kurz = kurz[:227].rsplit(" ", 1)[0] + " …"
    text = f"{w['titel']} {w['beschreibung']} {' '.join(w['benoetigt'])}".lower()
    ordner = w["ordner"]
    return f"""    <li class="karte" data-kat="{e(w['kategorie'])}" data-text="{e(text)}">
      <img src="{e(bild)}" alt="{e(w['titel'])}" loading="lazy" width="1200" height="675">
      <div class="inhalt">
        <p class="kat">{e(w['kategorie'])}</p>
        <h2>{e(w['titel'])}</h2>
        <p>{e(kurz)}</p>
        <p class="meta">{w['nodes']} Nodes · {e(w['schwierigkeit'])} · benötigt: {e(', '.join(w['benoetigt']))}</p>
        <div class="aktionen">
          <a class="haupt" href="{RAW}/workflows/{e(ordner)}/{e(w['slug'])}.json" download>JSON laden</a>
          <a href="{WEB}/n8n-workflows/{e(w['slug'])}/">Anleitung</a>
          <a href="{GH}/blob/main/workflows/{e(ordner)}/{e(w['slug'])}.json">Auf GitHub</a>
        </div>
      </div>
    </li>"""


def main():
    wfs = json.loads(META.read_text(encoding="utf-8"))
    kategorien = sorted({w["kategorie"] for w in wfs})

    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "thumbnails").mkdir(parents=True)
    for w in wfs:
        quelle = REPO / "assets" / "thumbnails" / w["ordner"] / f"{w['slug']}.jpg"
        if quelle.exists():
            shutil.copy2(quelle, BUILD / "thumbnails" / f"{w['slug']}.jpg")

    chips = "\n".join(
        f'      <button class="chip" type="button" aria-pressed="false" data-kat="{e(k)}">{e(k)}</button>'
        for k in kategorien
    )
    karten = "\n".join(karte(w) for w in wfs)

    titel = "n8n-Workflows auf Deutsch — 25 fertige Vorlagen zum Import"
    beschreibung = (
        f"{len(wfs)} einsatzfertige n8n-Workflows auf Deutsch: Vertrieb, Buchhaltung, "
        "Kundenservice, DSGVO und EU AI Act. Jede Vorlage mit Prüflogik, Kommentaren "
        "und Hinweis auf die rechtlichen Fallstricke. Kostenlos, MIT-Lizenz."
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": titel,
        "description": beschreibung,
        "url": "https://diekiagentur.github.io/n8n-workflows-de/",
        "license": "https://opensource.org/licenses/MIT",
        "isBasedOn": GH,
        "creator": {"@type": "Organization", "name": "die-ki-agentur.de", "url": WEB},
        "hasPart": [
            {
                "@type": "SoftwareSourceCode",
                "name": w["titel"],
                "programmingLanguage": "n8n",
                "codeRepository": GH,
                "url": f"{WEB}/n8n-workflows/{w['slug']}/",
            }
            for w in wfs
        ],
    }

    seite = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschreibung)}">
<link rel="canonical" href="https://diekiagentur.github.io/n8n-workflows-de/">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschreibung)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://diekiagentur.github.io/n8n-workflows-de/social-preview.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body>
<header>
  <div class="wrap">
    <h1>{len(wfs)} n8n-Workflows auf Deutsch</h1>
    <p class="lead">Fertige Vorlagen zum Import in n8n — Vertrieb, Buchhaltung, Kundenservice,
      DSGVO und EU AI Act. Jeder Workflow ist auf Importierbarkeit geprüft, im Klartext
      kommentiert und benennt die Stellen, an denen ein Mensch entscheiden muss.
      Kostenlos unter MIT-Lizenz.</p>
    <div class="marken">
      <a class="knopf" href="{GH}">Repository auf GitHub</a>
      <a class="knopf leer" href="{WEB}/n8n-workflows/">Anleitungen auf die-ki-agentur.de</a>
    </div>
  </div>
</header>
<main class="wrap">
  <div class="werkzeug">
    <label class="visually-hidden" for="suche" hidden>Workflows durchsuchen</label>
    <input id="suche" type="search" placeholder="Suchen — z. B. Rechnung, DSGVO, Ollama"
           autocomplete="off">
  </div>
  <div class="chips">
{chips}
  </div>
  <ul class="gitter">
{karten}
  </ul>
  <p class="leerzustand" id="leer" hidden>Kein Workflow passt zu dieser Suche.</p>
</main>
<footer>
  <div class="wrap">
    <p>Zusammengestellt und gepflegt von
      <a href="{WEB}/">die-ki-agentur.de</a> — KI-Beratung, Automatisierung und
      Schulung für den Mittelstand, aus Hechingen in Baden-Württemberg.
      Wer die Workflows nicht selbst einrichten möchte:
      <a href="{WEB}/n8n-agentur/">n8n-Agentur</a> ·
      <a href="{WEB}/kontakt/">Kontakt</a> ·
      <a href="{WEB}/impressum/">Impressum</a>.</p>
    <p>Code unter MIT-Lizenz. Die Vorlagen enthalten keine Zugangsdaten — Credentials
      werden nach dem Import in n8n hinterlegt. Vor dem Scharfschalten prüfen, welche
      Daten an welchen Anbieter gehen; die Hinweise dazu stehen in jedem Workflow.</p>
  </div>
</footer>
<script>{JS}</script>
</body>
</html>
"""
    (BUILD / "index.html").write_text(seite, encoding="utf-8")
    vorschau = REPO / "assets" / "social-preview.jpg"
    if vorschau.exists():
        shutil.copy2(vorschau, BUILD / "social-preview.jpg")
    # Jekyll aus dem Weg raeumen — sonst schluckt es Dateien mit Unterstrich.
    (BUILD / ".nojekyll").write_text("", encoding="utf-8")
    bilder = len(list((BUILD / "thumbnails").glob("*.jpg")))
    print(f"=> build/ erzeugt: {len(wfs)} Workflows, {bilder} Thumbnails")


if __name__ == "__main__":
    main()
