from pathlib import Path
import re
from html import unescape
from xml.etree import ElementTree as ET

root = Path("docs/tickets")
langs = ("", "-de", "-fr")
counts = {1:12, 2:55, 3:36, 4:7}
mapping = {}
order = {}
def read(path):
    return path.read_text(encoding="utf-8")
def write(path, content):
    path.write_text(content, encoding="utf-8")
def items(content):
    return re.findall(r'<li><a href="(mm-(\d{3})(?:-de|-fr)?\.html)">MM-\d{3} · (.*?)</a></li>', content)
for level, count in counts.items():
    rows = items(read(root / f"mm-l{level}.html"))
    assert len(rows) == count, (level, len(rows))
    rows.sort(key=lambda r: unescape(r[2]).casefold())
    order[level] = [r[1] for r in rows]
    for seq, (_, old, _) in enumerate(rows, 1):
        assert old not in mapping
        mapping[old] = f"MM-L{level}-{seq:03}"
assert set(mapping) == {f"{i:03}" for i in range(1,111)}
notes = {
    "": "Training case adapted from learning material; not independently validated in an SAP system. Production changes require authorization.",
    "-de": "Aufbereiteter Lernfall auf Basis von Schulungsmaterial; nicht unabhängig in einem SAP-System validiert. Produktivänderungen nur mit entsprechender Freigabe.",
    "-fr": "Cas pédagogique adapté de supports de formation, non validé indépendamment dans un système SAP. Toute modification en production nécessite une autorisation."
}
# Keep stable existing URLs, canonicals and language links; assign independent public IDs.
for suffix in langs:
    for level, count in counts.items():
        p = root / f"mm-l{level}{suffix}.html"
        h = read(p)
        rows = {old:(url,title) for url,old,title in items(h)}
        assert set(rows) == set(order[level]), (suffix,level)
        new = '<ul class="ticket-list">' + ''.join(
            f'<li><a href="{rows[old][0]}">{mapping[old]} · {rows[old][1]}</a></li>'
            for old in order[level]) + '</ul>'
        h,n = re.subn(r'<ul class="ticket-list">.*?</ul>',lambda _:new,h,flags=re.S)
        assert n == 1
        write(p,h)
    for old,new_id in mapping.items():
        p = root / f"mm-{old}{suffix}.html"
        h = read(p)
        h,n = re.subn(r'(<p class="eyebrow">)MM-\d{3}( · L[1-4]</p>)',lambda m:m[1]+new_id+m[2],h)
        assert n == 1, p
        h,n = re.subn(r'<section><h2>(?:Source|Quelle)</h2>.*?</section>', '', h, flags=re.S)
        assert n == 1, p
        assert 'Kandala Srinivasulu' not in h and 'PDF p.' not in h, p
        h,n = re.subn(r'</article></main>',lambda _:f'</article><p class="case-note">{notes[suffix]}</p></main>',h)
        assert n == 1
        assert new_id in h
        write(p,h)
# All 330 original pages remain reachable; sitemap URLs are unchanged.
sitemap = read(Path("docs/sitemap.xml"))
for old,new_id in mapping.items():
    for suffix in langs:
        assert f'/tickets/mm-{old}{suffix}.html</loc>' in sitemap
print("Validated 110 independent case IDs, 330 ticket pages and 12 level indexes.")
