"""Explicit migration: preserve literal public gallery captions on their slides."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import json
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent'
config=json.loads((H/'investigation/evidence/media-config.json').read_text());rows=[]
for project in (H,A):
 for path in (project/'content').rglob('index.html'):
  source=path.read_text();dom=BeautifulSoup(source,'html.parser');changed=False
  for slide in dom.select('.sx-carousel > .swiper-wrapper > .swiper-slide'):
   match=next((x for x in config['captions'] if x.get('image') and x['image'] in str(slide)),None)
   if not match:continue
   old=str(slide)
   if old not in source:raise RuntimeError(path)
   slide['data-caption']=match['caption'];source=source.replace(old,str(slide),1);changed=True
   rows.append({'project':project.name,'page':str(path.relative_to(project)),'image':match['image'],'caption':match['caption']})
  if changed:path.write_text(source)
for project in (H,A):(project/'investigation/evidence/gallery-caption-recovery.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Maintained slide captions:',len(rows))
