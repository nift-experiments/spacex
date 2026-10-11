"""Recover only visible public Swiper pagination presentation, without its runtime."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,hashlib,copy
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';B=W/'spacex-baseline';records=json.loads((H/'investigation/evidence/carousel-pagination-recovery.json').read_text()) if (H/'investigation/evidence/carousel-pagination-recovery.json').exists() else [];styles=set(BeautifulSoup((H/'templates/carousel-pagination.html').read_text(),'html.parser').style.get_text().strip().splitlines()) if (H/'templates/carousel-pagination.html').exists() else set()
plans=json.loads((H/'investigation/evidence/page-family-recovery.json').read_text())
for plan in plans:
 route=plan['route'].strip('/');capture=B/'browser-captures'/plan['capture']
 if route=='vehicles/starship':capture=B/'browser-captures/vehicles-starship.1280x720.10903ce02148.json'
 if route=='humanspaceflight':capture=B/'browser-captures/humanspaceflight.1280x720.706104c70828.json'
 if route=='mission':capture=B/'browser-captures/mission.1280x720.0032eeec494c.json'
 record=json.loads(capture.read_text());shadows=[BeautifulSoup(x['html'],'html.parser') for x in record.get('shadowRoots',[]) if x['tag']=='swiper-container']
 if not shadows:continue
 for project in (H,A):
  path=project/'content'/route/'index.html'
  if not path.is_file():continue
  source=path.read_text();dom=BeautifulSoup(source,'html.parser');carousels=dom.select('.sx-carousel')
  if len(carousels)!=len(shadows):continue
  for index,(carousel,shadow) in enumerate(zip(carousels,shadows)):
   pagination=copy.deepcopy(shadow.select_one('.swiper-pagination:not(.swiper-pagination-hidden)'))
   if not pagination or not pagination.select('[role=button]'):continue
   old=str(carousel);assert old in source,path
   if carousel.select_one('.swiper-pagination'):continue
   for button in pagination.select('[role=button]'):button['data-carousel-index']=str(len(button.find_previous_siblings()));button['aria-current']='true' if button['data-carousel-index']=='0' else 'false';button['class']=['swiper-pagination-bullet']+(['swiper-pagination-bullet-active'] if button['data-carousel-index']=='0' else [])
   carousel.append(pagination);source=source.replace(old,str(carousel),1)
   for style in shadow.select('style'):
    for rule in re.findall(r'([^{}]+)\{([^{}]*)\}',style.get_text()):
     selector,body=rule
     if '.swiper-pagination' in selector and not selector.lstrip().startswith('@'):
      styles.add(','.join('.sx-carousel '+part.strip().replace(':host','.sx-carousel') for part in selector.split(','))+'{'+body+'}')
   records.append({'project':project.name,'route':plan['route'],'carousel':index,'buttons':len(pagination.select('[role=button]')),'capture':capture.name,'captureSha256':hashlib.sha256(capture.read_bytes()).hexdigest()})
  if source!=path.read_text():path.write_text(source)
for project in (H,A):
 path=project/'templates/carousel-pagination.html';path.write_text('<style>\n'+ '\n'.join(sorted(styles))+'\n</style>\n')
 template=project/'templates/styles.html';source=template.read_text()
 if "templates/carousel-pagination.html" not in source:template.write_text(source+"\n@input('templates/carousel-pagination.html')\n")
 (project/'investigation/evidence/carousel-pagination-recovery.json').write_text(json.dumps(records,indent=2)+'\n')
print('Recovered pagination groups:',len(records))
