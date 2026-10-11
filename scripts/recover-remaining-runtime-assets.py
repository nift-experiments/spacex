"""Convert only inventoried runtime payloads to maintained assets and native paths."""
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import json,hashlib,shutil
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';rows=json.loads((B/'remaining-runtime-capture.json').read_text());mapping={};files=[];evidence=[]
for row in rows:
 frozen=B/row['path'];assert row['status']=='200' and row['transferComplete'];assert frozen.stat().st_size==row['bytes'] and hashlib.sha256(frozen.read_bytes()).hexdigest()==row['sha256']
 target='public/assets/recovered/runtime/'+row['sha256']+frozen.suffix;mapping[row['originalMaintainedUrl']]=target;files.append(target);evidence.append({'url':row['url'],'rolesAndRoutes':row['relationships'],'bytes':row['bytes'],'sha256':row['sha256'],'maintainedPath':target,'preservationMode':'offline-preserved'})
 for name in ['spacex','spacex-agent']:
  destination=W/name/target;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frozen,destination)
for name in ['spacex','spacex-agent']:
 project=W/name;count=0
 for folder in ['content','prose','templates']:
  for path in (project/folder).rglob('*.html'):
   source=path.read_text();dom=BeautifulSoup(source,'html.parser');new=source
   for tag in dom.select('img[src],video[src],source[src],audio[src],video[poster]'):
    for attribute in ['src', 'poster']:
     old=str(tag);url=tag.get(attribute)
     if url not in mapping:continue
     assert old in new,path;tag[attribute]="@path('"+mapping[url]+"')";new=new.replace(old,str(tag),1);count+=1
   if new!=source:path.write_text(new)
 (project/'investigation/evidence/runtime-asset-completion.json').write_text(json.dumps({'scope':'Captured runtime images/audio/video only; downloadable archive remains remote','assets':evidence,'sourceBindingsUpdated':count,'browserParityAccepted':False},indent=2)+'\n')
 print(name,count,'native runtime bindings')
(B/'runtime-extra-files.json').write_text(json.dumps(sorted(set(files)),indent=2)+'\n')
