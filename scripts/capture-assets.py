import importlib.util,re,json,pathlib,concurrent.futures
p=pathlib.Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.C;ss='\n'.join(p.read_text() for p in (r/'www.spacex.com').glob('*.js'));ss+='\n'+(r/'main.38aaaafc31bc4ec8.js').read_text()+'\n'+(r/'styles.1a4bd8588c6ea618.css').read_text()
urls=set('https://www.spacex.com/'+x for x in re.findall(r'["\x27](assets/[^"\x27<>\s]+)["\x27]',ss));urls.update(re.findall(r'https://(?:content.spacex.com|sxcontent9668.azureedge.us)/[^"\x27<>\s`]+',ss))
for x in re.findall(r'url\(([^"]+?)\)',(r/'styles.1a4bd8588c6ea618.css').read_text()):
 if not x.startswith(('data:','http')):urls.add('https://www.spacex.com/'+x.strip('\x27"'))
def walk(d):
 if isinstance(d,dict):
  for k,v in d.items():
   if k=='formats':continue
   if k=='url' and isinstance(v,str) and v.startswith(('https://content.spacex.com/','https://sxcontent9668.azureedge.us/')):urls.add(v)
   else:walk(v)
 elif isinstance(d,list):
  for v in d:walk(v)
for p in (r/'content.spacex.com').rglob('index.html'):
 try:walk(json.loads(p.read_text()))
 except:pass
# Lazy component CSS carries additional public fonts and image URLs.
components=json.loads((m.R/'component-inventory.json').read_text())['components']
for component in components:
 for style in component['styles']:
  for value in re.findall(r'url\(([^)]+)\)',style):
   value=value.strip('\x27"')
   if value.startswith('data:'):continue
   urls.add(value if value.startswith('https://') else 'https://www.spacex.com/'+value.lstrip('/'))

urls={u for u in urls if not any(x in u for x in ['${','\\','+','{','}'])}; print('asset URLs',len(urls),flush=True)
# Direct catalogue downloads are metadata-only; ordinary CMS background assets remain preserved.
policy=json.loads((m.R/'media-preservation-manifest.json').read_text())
remote={row['url'] for row in policy if row['preservationMode']=='remote-reference'}
urls-=remote
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for i,x in enumerate(pool.map(m.capture,sorted(urls,key=lambda u:(u.lower().endswith(('.mp4','.webm','.mov','.m3u8')),u)))):
  rows.append(x)
  (m.R/'asset-discovery-progress.json').write_text(json.dumps({'complete':False,'inputs':rows},indent=2)+'\n')
  if i%50==0:print('captured',i,'bytes',sum(x['bytes'] for x in rows),flush=True)
(m.R/'asset-discovery.json').write_text(json.dumps({'inputs':rows},indent=2)+'\n');print('done',len(rows),'bytes',sum(x['bytes'] for x in rows),'failures',sum(x['status'] not in ['200','cached'] for x in rows),flush=True)
