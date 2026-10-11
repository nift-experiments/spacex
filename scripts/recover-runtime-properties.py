"""Recover observable media properties not serialized as HTML attributes."""
from pathlib import Path
from bs4 import BeautifulSoup
import json
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';changed=[]
for name in ('spacex','spacex-agent'):
 p=W/name
 for row in json.loads((p/'investigation/evidence/page-family-recovery.json').read_text()):
  f=p/'content'/row['route'].strip('/')/'index.html';record=json.loads((B/'browser-captures'/row['capture']).read_text());original=BeautifulSoup(record['html'],'html.parser');page=original.select_one('.page-content-inner');reference=page.select('video') if page else []
  properties=record.get('media',[])
  if len(reference)!=len(properties):continue
  dom=BeautifulSoup(f.read_text(),'html.parser');videos=[v for v in dom.select('video') if not v.find_parent('template')]
  if len(videos)!=len(properties):continue
  source=f.read_text();count=0
  for v,prop in zip(videos,properties):
   if prop.get('autoplay') and prop.get('muted') and not v.has_attr('muted'):
    old=str(v);assert old in source,(f,str(v)[:120]);v['muted']='';source=source.replace(old,str(v),1);count+=1
  if count:f.write_text(source);changed.append({'project':name,'route':row['route'],'mutedPropertiesRecovered':count,'referenceCapture':row['capture']})
for name in ('spacex','spacex-agent'):(W/name/'investigation/evidence/media-runtime-properties.json').write_text(json.dumps(changed,indent=2)+'\n')
print('Recovered media property assignments:',sum(v['mutedPropertiesRecovered'] for v in changed))
