from pathlib import Path
import re
root=Path("docs/tickets")
changed=0
for p in sorted(root.glob("*.html")):
    h=p.read_text(encoding="utf-8")
    if "data-ticket-search" in h:
        continue
    m=re.match(r"(mm|sd|fi|fico|pp|basis)(?:-|\.html)",p.name)
    module=m.group(1) if m else "all"
    if module=="fi": module="fico"
    # Search the whole current module, not merely the current level.
    panel=f'<section class="ticket-search" data-ticket-search data-module="{module}"></section>'
    if "</h1>" not in h or "</body>" not in h: raise ValueError(p)
    h=h.replace("</h1>","</h1>"+panel,1).replace("</body>",'<script src="./search.js" defer></script></body>',1)
    p.write_text(h,encoding="utf-8")
    changed+=1
print(f"Updated {changed} ticket pages")
assert all("data-ticket-search" in p.read_text(encoding="utf-8") and "search.js" in p.read_text(encoding="utf-8") for p in root.glob("*.html"))
