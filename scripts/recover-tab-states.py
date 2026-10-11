"""Recover bounded public component states into maintained Nift sources.
No framework runtime is interpreted or shipped. This is explicit migration tooling.
"""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup,Comment
import json,re,hashlib
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';H=W/'spacex';A=W/'spacex-agent'
plans=json.loads((H/'investigation/evidence/tab-state-plan.json').read_text())
records=[]
for plan in plans:
 key=plan['route'].replace('/','-')+'-'+plan['key'];fragments=[]
 for label,ending in zip(plan['labels'],plan['captures']):
  capture=next((B/'browser-captures').glob(plan['route'].replace('/','-')+'.1280x720.'+ending+'.json'));record=json.loads(capture.read_text());dom=BeautifulSoup(record['html'],'html.parser')
  videos=dom.select('video')
  if len(videos)==len(record.get('media',[])):
   for video,properties in zip(videos,record['media']):
    if properties.get('autoplay') and properties.get('muted'):video['muted']=''
  root=next(tag for tag in dom.select('metric-tile') if [e.get_text(' ',strip=True) for e in tag.select('[role="tab"]')]==plan['labels'])
  selected=[e.get_text(' ',strip=True) for e in root.select('[role="tab"][aria-selected="true"]')];assert selected==[label],(capture,label,selected)
  owners={attribute.removeprefix('_nghost-'):tag.name for tag in dom.find_all(True) for attribute in tag.attrs if attribute.startswith('_nghost-')}
  def path(value):
   if not value or value.startswith(('data:','#','mailto:','tel:')):return value
   parsed=urlsplit(value);host=parsed.netloc or 'www.spacex.com';raw=unquote(parsed.path)
   if '/_reference/' in raw:host,raw=raw.split('/_reference/',1)[1].split('/',1);raw='/'+raw
   if host.startswith('127.0.0.1:'):host='www.spacex.com'
   if raw.startswith(('assets/','/assets/','/cms-assets/','/site-media/')):
    target='public/assets/recovered/'+host+'/'+raw.lstrip('/')
    assert (H/target).is_file() and (A/target).is_file(),target
   elif host=='www.spacex.com' and not Path(raw).suffix:target=raw.strip('/')+'/' if raw.strip('/') else '/'
   else:return value
   return "@path('"+target+"')"+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
  for tag in [root,*root.find_all(True)]:
   for attr in list(tag.attrs):
    if attr.startswith(('_nghost-','_ngcontent-')):
     prefix,identity=attr.split('-',1);tag['data-sx-host' if prefix=='_nghost' else 'data-sx']=owners[identity];del tag[attr]
   for attr in ('src','href','poster'):
    if tag.has_attr(attr):tag[attr]=path(tag[attr])
  for comment in root.find_all(string=lambda value:isinstance(value,Comment)):comment.extract()
  root['data-native-state-key']=key
  for button in root.select('[role="tab"]'):button['data-native-state-value']=button.get_text(' ',strip=True)
  fragment=str(root);fragments.append((label,fragment))
  records.append({'route':plan['route'],'family':key,'state':label,'capture':capture.name,'captureSha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'browserParityAccepted':False})
 for project in (H,A):
  for target_route in [plan['route'], *plan.get('aliases', [])]:
   f=project/'content'/target_route/'index.html';source=f.read_text();source=re.sub(r'<template data-native-state-template="'+re.escape(key)+r'"[\s\S]*?</template>\s*','',source);dom=BeautifulSoup(source,'html.parser');current=next(tag for tag in dom.select('metric-tile') if [e.get_text(' ',strip=True) for e in tag.select('[role="tab"]')]==plan['labels']);old=str(current);assert old in source
   current['data-native-state-key']=key
   for button in current.select('[role="tab"]'):button['data-native-state-value']=button.get_text(' ',strip=True)
   source=source.replace(old,str(current),1)
   for index,(label,fragment) in enumerate(fragments):
    if project==H:
     relative='content/states/'+key+'/'+str(index)+'.html';out=project/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(fragment+'\n');body="@input('"+relative+"')"
    else:body=fragment
    source+='\n<template data-native-state-template="'+key+'" data-native-state-value="'+label+'">'+body+'</template>\n'
   f.write_text(source)
for project in (H,A):
 (project/'investigation/evidence/tab-state-recovery.json').write_text(json.dumps(records,indent=2)+'\n')
print('Recovered tab-state fragments:',len(records))
