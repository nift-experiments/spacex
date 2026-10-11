"""Explicit freeze of runtime media still referenced remotely; never a build step."""
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,quote
import importlib.util,json,concurrent.futures
p=Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
urls=json.loads((m.R/'remaining-runtime-assets.json').read_text())
def acquire(original):
 u=urlsplit(original);encoded=urlunsplit((u.scheme,u.netloc,quote(u.path,safe='/+%'),u.query,u.fragment));row=m.capture(encoded);row['originalMaintainedUrl']=original;row['relationships']=urls[original];return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(acquire,urls))
(m.R/'remaining-runtime-capture.json').write_text(json.dumps(rows,indent=2)+'\n');print('Captured',len(rows),'runtime references;',sum(r['status']=='200' and r['transferComplete'] for r in rows),'complete HTTP 200',flush=True)
