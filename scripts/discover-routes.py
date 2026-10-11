"""Reconcile delivered lazy router literals and public CMS route instances."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[2]/'spacex-baseline';C=R/'capture';routes={}
def add(route,family,source):
 if not route.startswith('/') or any(x in route for x in ['${','{','}','\\',' ']):return
 routes.setdefault(route,{'route':route,'family':family,'discoveredFrom':[],'status':'unverified','migrationStatus':'not started'})['discoveredFrom'].append(source)
main=(C/'main.38aaaafc31bc4ec8.js').read_text()
for x in re.findall(r'path:"([^":*]+)"',main):add('/'+x,'shell','main lazy-router')
add('/','homepage','main lazy-router')
for n,parent in [('6969','/vehicles'),('3973','/humanspaceflight'),('7428','/careers'),('8832','/supplier'),('6543','/sites')]:
 p=next((C/'www.spacex.com').glob(n+'.*.js'));s=p.read_text()
 for x in re.findall(r'path:"([^":*]+)"',s):add(parent+'/'+x,'page or form',p.name)
for p in (C/'www.spacex.com').glob('*.js'):
 for x in re.findall(r'["\x27](/(?:vehicles|humanspaceflight|careers|sites|supplier|launches|content|updates|mission|rideshare|starshield|spacexai)[^"\x27<>\s]*)["\x27]',p.read_text()):add(x,'linked',p.name)
def load(a):return json.loads((C/'content.spacex.com/api/spacex-website'/a/'index.html').read_text())
for x in load('launches-page-tiles'):add('/launches/'+x['link'],'mission','CMS launch tiles')
for x in load('media-playlist'):
 add('/content/'+x['link'],'playlist','CMS media playlist')
 for y in x['media']:add('/content/'+x['link']+'/'+y['link'],'media','CMS media playlist')
(R/'route-discovery.json').write_text(json.dumps({'status':'provisional; route responses/redirects and browser reconciliation pending','routes':sorted(routes.values(),key=lambda x:x['route'])},indent=2)+'\n')
from collections import Counter
print('provisional routes',len(routes),dict(Counter(x['family'] for x in routes.values())))
