#!/usr/bin/env python3
"""Thumbnails fuer jeden Workflow: fal.ai erzeugt die Illustration, PIL legt die
Typografie darueber. Der Text wird bewusst NICHT vom Bildmodell gesetzt — nur so
sitzen Umlaute, Zeilenumbruch und Markenfarbe auf jedem Motiv identisch.

WICHTIG: laeuft strikt sequenziell. Zwei parallele fal-Laeufe ueberschreiben sich
gegenseitig die Zustandsdatei (Lehre aus frueheren Bildwellen).

    python3 scripts/thumbnails.py [--neu]     # --neu: auch vorhandene neu bauen
"""
import json, pathlib, subprocess, sys, textwrap, time

from PIL import Image, ImageDraw, ImageFont

FAL_KEY = "ecc8ae0e-ba62-41ca-a0f1-1d7a2de1fd0d:51ea793e54b3d4b063ac4104ccdfa8b5"
MODEL = "fal-ai/nano-banana-pro"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "thumbnails"
FONT_DIR = pathlib.Path.home() / "Library" / "Fonts"

BREITE, HOEHE = 1280, 720
NAVY, BLAU, WEISS = (14, 30, 74), (29, 78, 216), (255, 255, 255)

# Bildwelt je Kategorie — abstrakt-technisch, keine Menschen, kein Text im Bild.
MOTIVE = {
    "01": "abstract flowing data pipelines converging into a funnel, sales pipeline concept",
    "02": "abstract stacked documents and ledger sheets transforming into structured data grids",
    "03": "abstract envelope shapes dissolving into sorted streams of light",
    "04": "abstract neural network mesh with glowing document nodes, knowledge retrieval",
    "05": "abstract content blocks radiating outward into social feed cards",
    "06": "abstract speech bubbles connected by flowing lines, support conversation routing",
    "07": "abstract dashboard charts and rising bar graphs in clean geometry",
    "08": "abstract shield and checklist geometry, compliance and data protection",
    "09": "abstract calendar grid merging with mechanical gear shapes, scheduling and maintenance",
    "10": "abstract organisational chart with connected person silhouettes as simple geometry",
}
STIL = ("minimalist 3D render, deep blue and white colour scheme, navy background, "
        "soft studio lighting, clean geometric abstraction, generous negative space on the left, "
        "no text, no letters, no numbers, no logos, no people's faces, corporate tech aesthetic")


def font(name, groesse):
    for kandidat in (FONT_DIR / name, pathlib.Path("/System/Library/Fonts/Supplemental") / name):
        if kandidat.exists():
            return ImageFont.truetype(str(kandidat), groesse)
    return ImageFont.load_default()


def generiere(prompt):
    payload = json.dumps({"prompt": prompt, "aspect_ratio": "16:9",
                          "resolution": "2K", "num_images": 1, "output_format": "jpeg"})
    for versuch in range(3):
        p = subprocess.run(["curl", "-sS", "--max-time", "240", "-X", "POST",
                            f"https://fal.run/{MODEL}",
                            "-H", f"Authorization: Key {FAL_KEY}",
                            "-H", "Content-Type: application/json", "-d", payload],
                           capture_output=True, text=True)
        try:
            d = json.loads(p.stdout)
            if d.get("images"):
                return d["images"][0]["url"]
            print(f"    ! {str(d)[:120]}")
        except Exception as e:
            print(f"    ! {e}")
        time.sleep(6)
    return None


def baue(url, titel, kategorie, ziel: pathlib.Path):
    roh = subprocess.run(["curl", "-sS", "--max-time", "180", "-L", url],
                         capture_output=True).stdout
    from io import BytesIO
    bild = Image.open(BytesIO(roh)).convert("RGB").resize((BREITE, HOEHE), Image.LANCZOS)

    # Navy-Verlauf von links: haelt die Textzone ruhig, egal wie unruhig das Motiv ist.
    schleier = Image.new("RGBA", (BREITE, HOEHE), (0, 0, 0, 0))
    zeichner = ImageDraw.Draw(schleier)
    for x in range(BREITE):
        anteil = max(0.0, 1.0 - (x / (BREITE * 0.72)))
        zeichner.line([(x, 0), (x, HOEHE)], fill=(*NAVY, int(248 * anteil)))
    bild = Image.alpha_composite(bild.convert("RGBA"), schleier).convert("RGB")

    d = ImageDraw.Draw(bild)
    d.rectangle([0, HOEHE - 10, BREITE, HOEHE], fill=BLAU)          # Markenkante
    d.text((72, 74), kategorie.upper(), font=font("Poppins-SemiBold.ttf", 25),
           fill=(147, 197, 253))

    zeilen = textwrap.wrap(titel, width=22)[:4]
    y = 150
    for zeile in zeilen:
        d.text((72, y), zeile, font=font("Poppins-Bold.ttf", 58), fill=WEISS)
        y += 72

    d.text((72, HOEHE - 118), "n8n-Workflow · sofort importierbar",
           font=font("Poppins-Regular.ttf", 26), fill=(191, 219, 254))
    marke = font("Poppins-SemiBold.ttf", 30)
    d.text((72, HOEHE - 74), "die-ki-agentur", font=marke, fill=WEISS)
    breite_marke = d.textlength("die-ki-agentur", font=marke)
    d.text((72 + breite_marke, HOEHE - 74), ".de", font=marke, fill=(96, 165, 250))

    ziel.parent.mkdir(parents=True, exist_ok=True)
    bild.save(ziel, quality=88, optimize=True)
    return ziel.stat().st_size // 1024


def main(argv):
    neu = "--neu" in argv
    dateien = sorted((ROOT / "workflows").rglob("*.json"))
    ok = fehler = uebersprungen = 0
    for f in dateien:
        kat_ordner = f.parent.name
        ziel = OUT / kat_ordner / (f.stem + ".jpg")
        if ziel.exists() and not neu:
            uebersprungen += 1
            continue
        wf = json.loads(f.read_text(encoding="utf-8"))
        titel = wf.get("name", f.stem)
        kategorie = (wf.get("meta") or {}).get("kategorie", kat_ordner.split("-", 1)[-1].replace("-", " "))
        motiv = MOTIVE.get(kat_ordner[:2], "abstract automation flow geometry")
        print(f"-> {f.parent.name}/{f.name}", flush=True)
        url = generiere(f"{motiv}. {STIL}")
        if not url:
            print("   ! Generierung fehlgeschlagen"); fehler += 1; continue
        kb = baue(url, titel, kategorie, ziel)
        print(f"   ok {ziel.relative_to(ROOT)} ({kb} KB)", flush=True)
        ok += 1
    print(f"\nFertig: {ok} neu, {uebersprungen} vorhanden, {fehler} Fehler")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
