"""Explicit migration repair: tracked route names and native responsive-asset paths."""
from pathlib import Path
from urllib.parse import urlsplit,unquote,quote
from bs4 import BeautifulSoup
import json,re,hashlib,shutil
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';records=[]
for name in ('spacex','spacex-agent'):
 P=W/name;tracked={x['name'] for x in json.loads((P/'.nift/tracked.json').read_text())['tracked']};repaired=0
 def route(match):
  global repaired
  quote,value=match.group(1),match.group(2)
  if not value.startswith('public/') or value.startswith('public/assets/'):return match.group()
  target=value[len('public/'):]
  suffix=''
  if target.endswith('/index.html'):target=target[:-len('index.html')];suffix='index.html'
  if target=='index.html':target='/';suffix='index.html'
  if target=='undefined/':return '@path('+quote+'/'+quote+')undefined/'
  if target not in tracked:raise RuntimeError('Untracked route '+target)
  repaired+=1;return '@path('+quote+target+quote+')'+suffix
 for folder in ('content','templates','data','prose'):
  for path in (P/folder).rglob('*'):
   if path.suffix not in ('.html','.json'):continue
   original=path.read_text();source=re.sub(r'@path\(([\x27\"])([^\x27\"]+)\1\)',route,original)
   if path.suffix=='.json':
    # Only exact tracked output references; maintained asset filenames are untouched.
    for target in sorted(tracked,key=len,reverse=True):
     if target=='/':continue
     source=source.replace('"public/'+target+'"','"'+target+'"')
   if path.suffix=='.html':
    dom=BeautifulSoup(source,'html.parser')
    for tag in dom.select('[srcset]'):
     value=tag['srcset']
     if '@path(' in value or value.startswith('data:'):continue
     entries=[]
     for entry in value.split(','):
      parts=entry.strip().rsplit(None,1);descriptor=parts[-1] if len(parts)>1 and re.fullmatch(r'[0-9.]+[wx]',parts[-1]) else '';url=parts[0] if descriptor else entry.strip();u=urlsplit(url);raw=unquote(u.path);host=u.netloc or 'www.spacex.com'
      if '/_reference/' in raw:host,raw=raw.split('/_reference/',1)[1].split('/',1);raw='/'+raw
      if host.startswith('127.0.0.1:'):host='www.spacex.com'
      if not raw.startswith(('/assets/','assets/','/cms-assets/','/site-media/')):raise RuntimeError('Unclassified srcset '+url)
      rel=host+'/'+raw.lstrip('/');target='public/assets/recovered/'+rel
      if not (P/target).is_file():
       frozen=B/'capture'/rel
       if not frozen.is_file():frozen=B/'capture'/quote(rel,safe='/+')
       receipt=Path(str(frozen)+'.receipt.json')
       if not frozen.is_file() or not receipt.is_file():raise RuntimeError('Missing responsive reference '+rel)
       r=json.loads(receipt.read_text());key=hashlib.sha256(frozen.read_bytes()).hexdigest();assert r['transferComplete'] and r['status'] in ('200','206') and key==r['sha256']
       if frozen.stat().st_size<=2*1024*1024:target='public/assets/images/responsive/'+key+frozen.suffix
       dest=P/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frozen,dest)
      entries.append("@path('"+target+"')"+(' '+descriptor if descriptor else ''))
     old=str(tag);assert old in source,path;tag['srcset']=', '.join(entries);source=source.replace(old,str(tag),1);records.append({'project':name,'source':str(path.relative_to(P)),'previous':value,'maintained':tag['srcset']})
   if source!=original:path.write_text(source)
 print(name,'tracked route bindings repaired:',repaired)
for name in ('spacex','spacex-agent'):(W/name/'investigation/evidence/native-path-repair.json').write_text(json.dumps({'scope':'Fresh-checkout route @path corrections and captured srcset assets; final browser parity remains open','srcsets':records},indent=2)+'\n')
