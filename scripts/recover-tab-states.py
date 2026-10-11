"""Recover bounded public component states into maintained Nift sources.
No framework runtime is interpreted or shipped. This is explicit migration tooling.
"""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup,Comment
import json,re,hashlib,argparse,shutil
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';H=W/'spacex';A=W/'spacex-agent'
plans=json.loads((H/'investigation/evidence/tab-state-plan.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--routes',nargs='*');args=parser.parse_args()
existing=json.loads((H/'investigation/evidence/tab-state-recovery.json').read_text()) if (H/'investigation/evidence/tab-state-recovery.json').exists() else []
records=[row for row in existing if args.routes and row['route'] not in args.routes]
for plan in plans:
 if args.routes and plan['route'] not in args.routes:continue
 key=plan['route'].replace('/','-')+'-'+plan['key'];fragments=[]
 for label,ending in zip(plan['labels'],plan['captures']):
  capture=next((B/'browser-captures').glob(plan['route'].replace('/','-')+'.1280x720.'+ending+'.json'));record=json.loads(capture.read_text());dom=BeautifulSoup(record['html'],'html.parser')
  videos=dom.select('video')
  if len(videos)==len(record.get('media',[])):
   for video,properties in zip(videos,record['media']):
    if properties.get('autoplay') and properties.get('muted'):video['muted']=''
  root=next(tag for tag in dom.select(plan.get('rootSelector','metric-tile')) if [e.get_text(' ',strip=True) for e in tag.select('[role="tab"]')]==plan['labels'])
  selected=[e.get_text(' ',strip=True) for e in root.select('[role="tab"]') if e.get('aria-selected')=='true' or e.select_one('[aria-selected="true"]')];assert selected==[label],(capture,label,selected)
  owners={attribute.removeprefix('_nghost-'):tag.name for tag in dom.find_all(True) for attribute in tag.attrs if attribute.startswith('_nghost-')}
  def path(value):
   if not value or value.startswith(('data:','#','mailto:','tel:')):return value
   parsed=urlsplit(value);host=parsed.netloc or 'www.spacex.com';raw=unquote(parsed.path)
   if '/_reference/' in raw:host,raw=raw.split('/_reference/',1)[1].split('/',1);raw='/'+raw
   if host.startswith('127.0.0.1:'):host='www.spacex.com'
   if raw.startswith(('assets/','/assets/','/cms-assets/','/site-media/')):
    target='public/assets/recovered/'+host+'/'+raw.lstrip('/')
    if not (H/target).is_file() or not (A/target).is_file():
     frozen=B/'capture'/host/raw.lstrip('/');receipt=Path(str(frozen)+'.receipt.json')
     assert frozen.is_file() and receipt.is_file(),target
     info=json.loads(receipt.read_text());sha=hashlib.sha256(frozen.read_bytes()).hexdigest()
     assert info['transferComplete'] and info['status']=='200' and sha==info['sha256'] and frozen.stat().st_size<2*1024*1024
     target='public/assets/images/states/'+sha+frozen.suffix
     for project in (H,A):
      destination=project/target;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frozen,destination)
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
  for button in root.select('[role="tab"]'):
   button['data-native-state-value']=button.get_text(' ',strip=True);button['aria-selected']=str(button.get_text(' ',strip=True)==label).lower();button['tabindex']='0' if button.get_text(' ',strip=True)==label else '-1'
  fragment=re.sub(r'[ \t]+\n','\n',str(root));fragments.append((label,fragment))
  records.append({'route':plan['route'],'family':key,'state':label,'capture':capture.name,'captureSha256':hashlib.sha256(capture.read_bytes()).hexdigest(),'browserParityAccepted':False})
 for project in (H,A):
  for target_route in [plan['route'], *plan.get('aliases', [])]:
   f=project/'content'/target_route/'index.html';source=f.read_text();source=re.sub(r'<template data-native-state-template="'+re.escape(key)+r'"[\s\S]*?</template>\s*','',source);dom=BeautifulSoup(source,'html.parser');current=next(tag for tag in dom.select(plan.get('rootSelector','metric-tile')) if [e.get_text(' ',strip=True) for e in tag.select('[role="tab"]')]==plan['labels']);old=str(current);assert old in source
   current['data-native-state-key']=key
   for button in current.select('[role="tab"]'):button['data-native-state-value']=button.get_text(' ',strip=True)
   source=source.replace(old,fragments[0][1],1)
   for index,(label,fragment) in enumerate(fragments):
    if project==H:
     relative='content/states/'+key+'/'+str(index)+'.html';out=project/relative;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(fragment+'\n');body="@input('"+relative+"')"
    else:body=fragment
    source+='\n<template data-native-state-template="'+key+'" data-native-state-value="'+label+'">'+body+'</template>\n'
   f.write_text(source)
for project in (H,A):
 (project/'investigation/evidence/tab-state-recovery.json').write_text(json.dumps(records,indent=2)+'\n')
print('Recovered tab-state fragments:',len(records))
