"""One-time corpus gallery recovery from an observed public mission family."""
from pathlib import Path
from bs4 import BeautifulSoup, Comment
import copy, hashlib, html, json, re
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';B=W/'spacex-baseline'
if "@input('templates/mission-gallery.html')" in (H/'templates/mission.html').read_text():raise SystemExit('Gallery recovery already applied; maintain sources directly')
capture=B/'browser-captures/launches-crew13.1280x720.1856dad92217.json';record=json.loads(capture.read_text());dom=BeautifulSoup(record['html'],'html.parser');prototype=dom.select_one('.carousel-wrapper');assert prototype
mapping={'c57':'launch-tile','c58':'launch-swiper','c40':'down-arrow-svg','c60':'mission-page'}
def normalize(node):
 for comment in node.find_all(string=lambda value:isinstance(value,Comment)):comment.extract()
 for tag in [node,*node.find_all(True)]:
  for attr in list(tag.attrs):
   match=re.fullmatch(r'_ng(content|host)-[^-]+-(c\d+)',attr)
   if match:tag['data-sx' if match[1]=='content' else 'data-sx-host']=mapping[match[2]];del tag[attr]
 return node
normalize(prototype)
container=prototype.find('swiper-container');slides=container.find_all('swiper-slide',recursive=False);assert len(slides)==4
slide=copy.deepcopy(slides[0]);slide.name='div';slide['class']=['swiper-slide'];slide.attrs.pop('style',None);slide.attrs.pop('aria-label',None)
for old in slide.select('launch-tile'):old.name='div'
image=slide.select_one('img');assert image;image['src']="@path('$[photo.desktop]')";image['data-mobile']="@path('$[photo.mobile]')"
slide['data-caption']='$[photo.caption]';slide['aria-label']='$[photo.position]'
slideText=str(slide).replace(str(image), '@if(photo.desktop){'+str(image)+'}')
container.clear();container.name='div';container['class']=['sx-carousel'];container['data-carousel-gap']='30'
for attr in ['centered-slides','pagination','space-between']:container.attrs.pop(attr,None)
wrapper=dom.new_tag('div');wrapper['class']=['swiper-wrapper'];container.append(wrapper)
placeholder=dom.new_tag('span');placeholder['id']='gallery-slide-placeholder';wrapper.append(placeholder)
root=prototype.find('launch-swiper');root.name='div';root['data-sx-host']='launch-swiper'
source=str(prototype).replace(str(placeholder),"@for(photo : mission.gallery){"+slideText+"}")
# Shared native pagination uses the observed public bullet presentation.
bullet='<span class="swiper-pagination-bullet" data-carousel-index="$[photo.index]" role="button" tabindex="0" aria-label="Go to slide $[photo.number]"></span>'
bulletLoop='@for(photo : mission.gallery){'+bullet+'}'
marker='</div></div><div class="swiper-controls-wrapper"'
assert source.count(marker)==1
source=source.replace(marker,'</div><div class="swiper-pagination swiper-pagination-clickable swiper-pagination-bullets swiper-pagination-horizontal">'+bulletLoop+'</div></div><div class="swiper-controls-wrapper"')
styles=[]
for style in record['styles']:
 if '_ngcontent-tcd-c57' not in style and '_ngcontent-tcd-c58' not in style:continue
 for key,value in mapping.items():
  style=style.replace('[_ngcontent-tcd-'+key+']','[data-sx="'+value+'"]').replace('[_nghost-tcd-'+key+']','[data-sx-host="'+value+'"]')
 style=style.replace('::part(pagination)',' .swiper-pagination').replace('@','\\@');styles.append(style)
for root in (H,A):(root/'templates/mission-gallery-styles.html').write_text("@input('templates/swiper-styles.html')\n<style>\n"+'\n'.join(styles)+'\n</style>\n')
(H/'templates/mission-gallery.html').write_text("@input('templates/mission-gallery-styles.html')\n"+source+'\n')
rows=[];pending={}
for path in sorted((H/'data/missions').glob('*.json')):
 model=json.loads(path.read_text());gallery=model.get('gallery') or []
 if not gallery:continue
 assert all(not photo['desktop'] or photo['mobile'] for photo in gallery),path
 for index,photo in enumerate(gallery):photo.update(position=str(index+1)+' / '+str(len(gallery)),index=index,number=index+1)
 pending[path]=json.dumps(model,indent=2)+'\n'
 rendered=source
 loop='@for(photo : mission.gallery){'+slideText+'}'
 photos=[]
 for photo in gallery:
  fragment=slideText
  if photo['desktop']:fragment=fragment.replace('@if(photo.desktop){'+str(image)+'}',str(image))
  else:fragment=fragment.replace('@if(photo.desktop){'+str(image)+'}','')
  for key,value in photo.items():fragment=fragment.replace('$[photo.'+key+']',html.escape(str(value),quote=True))
  photos.append(fragment)
 rendered=rendered.replace(loop,''.join(photos));rendered=rendered.replace(bulletLoop,''.join(bullet.replace('$[photo.index]',str(index)).replace('$[photo.number]',str(index+1)) for index in range(len(gallery))));assert '@for(' not in rendered
 p=A/'content/launches'/path.stem/'index.html';text=p.read_text();parsed=BeautifulSoup(text,'html.parser');old=parsed.select_one('.mission-gallery')
 # Existing rendered figures serialize exactly except optional HTML img closing syntax.
 if old:
  match=re.search(r'<div class="mission-gallery">.*?</div>',text,re.S);assert match,p
  original=match.group();assert original.count('<figure>')==sum(bool(x['desktop']) for x in gallery),p
  pending[p]=text.replace(original,"@input('templates/mission-gallery-styles.html')\n"+rendered,1)
 else:assert "@input('templates/mission-gallery-styles.html')" in text,p
 rows.append({'mission':path.stem,'slides':len(gallery)})
for path,text in pending.items():path.write_text(text)
p=H/'templates/mission.html';text=p.read_text();start=text.index('@if(mission.gallery)');end=text.index("@input('templates/mission-webcasts.html')",start);p.write_text(text[:start]+"@if(mission.gallery){@input('templates/mission-gallery.html')}\n"+text[end:])
for root in (H,A):(root/'investigation/evidence/mission-gallery-recovery.json').write_text(json.dumps({'capture':capture.name,'sha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'missions':rows,'browserParityAccepted':False},indent=2)+'\n')
print('Recovered galleries:',len(rows),'missions;',sum(x['slides'] for x in rows),'slides')
