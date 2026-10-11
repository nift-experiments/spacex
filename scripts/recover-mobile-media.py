"""Explicit migration: attach frozen literal mobile variants using native @path."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import json
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent'
config=json.loads((H/'investigation/evidence/media-config.json').read_text());records=[]
def asset(value):
 u=urlsplit(value);return 'public/assets/recovered/'+(u.netloc or 'www.spacex.com')+'/'+u.path.lstrip('/')
pairs={asset(x['desktop']):asset(x['mobile']) for x in config['pairs'] if x['desktop']!=x['mobile']}
for project in (H,A):
 for path in (project/'content').rglob('*.html'):
  source=path.read_text();dom=BeautifulSoup(source,'html.parser');changed=False
  for tag in dom.select('img[src],video'):
   origin=tag.get('src','') if tag.name=='img' else (tag.select_one('source[src]') or tag).get('src','')
   key=next((key for key in pairs if key in origin),None)
   if not key:continue
   target=pairs[key];assert (project/target).is_file(),target
   old=str(tag)
   if old not in source:continue
   tag['data-mobile']="@path('"+target+"')";source=source.replace(old,str(tag),1);changed=True
   records.append({'project':project.name,'source':str(path.relative_to(project)),'desktop':key,'mobile':target})
  if changed:path.write_text(source)
for project in (H,A):(project/'investigation/evidence/mobile-media-recovery.json').write_text(json.dumps(records,indent=2)+'\n')
print('Native mobile media bindings:',len(records))
