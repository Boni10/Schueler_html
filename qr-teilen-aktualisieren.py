#!/usr/bin/env python3
"""Aktualisiert die Dateiliste in qr-teilen.html (alle *.html in den Unterordnern), jeweils mit Kapitel.
Aufruf im Repo-Hauptordner:  python3 qr-teilen-aktualisieren.py

Das Kapitel kommt aus dem Kapitelordner im Unterrichtsassistenten (zwei Ordner über diesem Repo,
z. B. Mathematik/M7A/Kap2_Termumformungen). Fehlt der Unterrichtsassistent (z. B. in einer Cloud-Session),
bleibt das bisher eingetragene Kapitel; neue Dateien bekommen es aus der Nummer im Namen ("M7 2.1a …" -> Kapitel 2).
"""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent
tool = root / "qr-teilen.html"
BASIS = root.parent.parent
# Ordner im Schueler-Repo -> Klassenordner im Unterrichtsassistenten (wie Tools/schueler_sync.py)
KLASSEN_ORDNER = {
    "mathe6": "Mathematik/M6B",
    "mathe7": "Mathematik/M7A",
    "physik9": "Physik/P9A",
    "physik11": "Physik/P11B",
    "physik11_profil": "Physik/P11C",
}
# Anzeigenamen der Kapitelordner (Umlaute); neue Kapitel ohne Eintrag erscheinen mit dem Ordnernamen
KAPITEL_NAMEN = {
    "Kap1_Brueche_und_Dezimalbrueche": "1 Brüche und Dezimalbrüche",
    "Kap1_Terme": "1 Terme",
    "Kap2_Termumformungen": "2 Termumformungen",
    "Kap1_Mechanische_Energie": "1 Mechanische Energie",
    "Kap1_Kreisbewegungen": "1 Kreisbewegungen",
    "Kap4-1_Methode_der_kleinen_Schritte": "4.1 Methode der kleinen Schritte",
}
SONDER = {"seminar": "Seminar-Demo"}


def kapitel_name(ordner):
    if ordner in KAPITEL_NAMEN:
        return KAPITEL_NAMEN[ordner]
    m = re.match(r"Kap([\d-]+)_(.+)$", ordner)
    print(f"Hinweis: Kapitelordner {ordner} fehlt in KAPITEL_NAMEN")
    return f"{m.group(1).replace('-', '.')} {m.group(2).replace('_', ' ')}" if m else ordner


def kapitel_aus_ordnern():
    """Dateiname -> Kapitel, je Schueler-Ordner, aus den Kapitelordnern der Klassen."""
    karte = {}
    for ziel, rel in KLASSEN_ORDNER.items():
        quelle = BASIS / rel
        if not quelle.is_dir():
            continue
        for kap in sorted(quelle.glob("Kap*")):
            if not kap.is_dir():
                continue
            name = kapitel_name(kap.name)
            for p in kap.rglob("*.html"):
                if "Notfall" not in p.relative_to(kap).parts:
                    karte.setdefault((ziel, p.name), name)
    return karte


text = tool.read_text(encoding="utf-8")
alt_json = re.search(r'<script type="application/json" id="dateien">(.*?)</script>', text, flags=re.S)
alt = {}
if alt_json:
    for e in json.loads(alt_json.group(1)):
        if isinstance(e, list) and len(e) == 2:
            alt[e[0]] = e[1]

karte = kapitel_aus_ordnern()
pfade = sorted(
    p.relative_to(root).as_posix()
    for p in root.glob("*/*.html")
    if not p.parent.name.startswith(".")
)
eintraege, geraten = [], []
for pfad in pfade:
    ordner, name = pfad.split("/", 1)
    kap = karte.get((ordner, name)) or SONDER.get(ordner) or alt.get(pfad)
    if not kap:
        m = re.match(r"\S+ (\d+)\.", name)
        if m:   # gleiche Nummer wie ein bekanntes Kapitel dieser Klasse?
            bekannt = sorted({k for (o, _), k in karte.items() if o == ordner and k.split(" ")[0].split(".")[0] == m.group(1)})
            kap = bekannt[0] if bekannt else f"Kapitel {m.group(1)}"
        else:
            kap = "Weitere"
        geraten.append(f"{pfad} -> {kap}")
    eintraege.append([pfad, kap])

neu, n = re.subn(
    r'(<script type="application/json" id="dateien">).*?(</script>)',
    lambda m: m.group(1) + json.dumps(eintraege, ensure_ascii=False) + m.group(2),
    text, count=1, flags=re.S,
)
if n != 1:
    raise SystemExit("Dateiliste in qr-teilen.html nicht gefunden")
tool.write_text(neu, encoding="utf-8")
print(f"{len(eintraege)} Dateien eingetragen")
for g in geraten:
    print(f"  Kapitel geraten: {g}")
