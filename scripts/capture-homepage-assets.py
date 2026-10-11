from pathlib import Path
import importlib.util,json,re,concurrent.futures
p=Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
urls=set()
def walk(d):
 if isinstance(d,dict):
  for k,v in d.items():
   if k=='formats':continue
   if k=='url' and isinstance(v,str) and v.startswith('https://'):urls.add(v)
   else:walk(v)
 elif isinstance(d,list):
  for x in d:walk(x)
for a in ['homepage-tiles','featured-launch-tiles','launches-page-tiles/upcoming','pad-photos']:walk(json.loads((m.C/'content.spacex.com/api/spacex-website'/a/'index.html').read_text()))
for f in re.findall(r'url\(([^)]+)\)',(m.C/'home.html').read_text()+(m.C/'styles.1a4bd8588c6ea618.css').read_text()):
 f=f.strip('\x27"')
 if not f.startswith(('data:','http')):urls.add('https://www.spacex.com/'+f)
urls.add('https://content.spacex.com/cms-assets/future_missions.json');urls.add('https://www.spacex.com/assets/favicon-spacex.ico')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(m.capture,sorted(urls)))
(m.R/'homepage-assets.json').write_text(json.dumps(rows,indent=2)+'\n');print('homepage assets',len(rows),'bytes',sum(x['bytes'] for x in rows))
