"""Capture route responses and mission-instance data; explicit acquisition only."""
from pathlib import Path
import importlib.util,json,concurrent.futures,datetime
p=Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
routes=json.loads((m.R/'route-discovery.json').read_text())['routes'];urls=[]
for row in routes:
 urls.append('https://www.spacex.com'+row['route'])
 if row['family']=='mission':urls.append('https://content.spacex.com/api/spacex-website/missions/'+row['route'].split('/')[-1])
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for i,x in enumerate(pool.map(m.capture,sorted(set(urls)))):
  rows.append(x)
  if i%20==0:
   (m.R/'route-acquisition-progress.json').write_text(json.dumps({'complete':False,'inputs':rows},indent=2)+'\n');print('route inputs captured',len(rows),flush=True)
(m.R/'route-acquisition.json').write_text(json.dumps({'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'complete':True,'inputs':rows},indent=2)+'\n');print('done',len(rows),flush=True)
