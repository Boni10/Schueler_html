#!/usr/bin/env python3
"""Aktualisiert die Dateiliste in qr-teilen.html (alle *.html in den Unterordnern).
Aufruf im Repo-Hauptordner:  python3 qr-teilen-aktualisieren.py
"""
import json, re, pathlib

root = pathlib.Path(__file__).resolve().parent
tool = root / "qr-teilen.html"
files = sorted(
    p.relative_to(root).as_posix()
    for p in root.glob("*/*.html")
    if not p.parent.name.startswith(".")
)
text = tool.read_text(encoding="utf-8")
neu, n = re.subn(
    r'(<script type="application/json" id="dateien">).*?(</script>)',
    lambda m: m.group(1) + json.dumps(files, ensure_ascii=False) + m.group(2),
    text, count=1, flags=re.S,
)
if n != 1:
    raise SystemExit("Dateiliste in qr-teilen.html nicht gefunden")
tool.write_text(neu, encoding="utf-8")
print(f"{len(files)} Dateien eingetragen")
