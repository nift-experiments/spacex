"""Capture URLs embedded in the frozen public component CSS, including fonts."""
from pathlib import Path
import json,re,importlib.util,concurrent.futures
p=Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
urls=set()
for component in json.loads((m.R/'component-inventory.json').read_text())['components']:
 for style in component['styles']:
  for url in re.findall(r'url\(([^)]+)\)',style):
   url=url.strip('\x27"')
   if not url.startswith('data:'):urls.add(url if url.startswith('https://') else 'https://www.spacex.com/'+url.lstrip('/'))
print('Component CSS inputs',len(urls),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(m.capture,sorted(urls)))
(m.R/'component-assets.json').write_text(json.dumps(rows,indent=2)+'\n');print('Component capture complete',len(rows),sum(x['bytes'] for x in rows),flush=True)
