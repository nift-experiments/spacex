"""Recover the delivered vanilla 3D renderer with native paths and frozen test inputs."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import copy, datetime, hashlib, json, re, shutil
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';B=W/'spacex-baseline';records=[]
if (H/'templates/trackers/vehicle-tracker.html').exists():raise SystemExit('Tracker recovery already applied; maintain sources directly')
probes=json.loads((B/'tracker-api-probes/probes.json').read_text())
for row in probes:
 assert row['status']=='200' and row['exit']==0,row['url']
 name=Path(urlsplit(row['url']).path).name;source=B/'tracker-api-probes'/name;assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
 frozen=B/'capture/content.spacex.com/cms-assets'/name;frozen.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,frozen);shutil.copyfile(B/'tracker-api-probes'/(name+'.headers'),Path(str(frozen)+'.headers'))
 receipt={**row,'path':str(frozen.relative_to(B)),'transferComplete':True,'expectedBytes':row['bytes'],'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':''};Path(str(frozen)+'.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 for root in (H,A):
  dest=root/'public/assets/data/trackers'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
textures=json.loads((B/'tracker-texture-capture.json').read_text());lookup={r['url']:r for r in textures}
for family in ['vehicle-tracker','follow-dragon']:
 original=B/'capture/www.spacex.com/assets/js'/family/'threed.js';js=original.read_text();urls=sorted(set(re.findall(r'"(assets/[^"\n]+)"',js)));mapping={}
 for url in urls:
  receipt=lookup['https://www.spacex.com/'+url];frozen=B/receipt['path'];assert receipt['transferComplete'] and hashlib.sha256(frozen.read_bytes()).hexdigest()==receipt['sha256']
  target='public/assets/images/tracker/'+receipt['sha256']+frozen.suffix;mapping[url]="@path('"+target+"')"
  for root in (H,A):
   dest=root/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(frozen,dest)
 source=H/'content'/family/'index.html';text=source.read_text();dom=BeautifulSoup(text,'html.parser');host=dom.find(family);assert host
 nested=host.find('html');head=nested.find('head');body=nested.find('body');assert body
 scripts=[copy.deepcopy(tag) for tag in head.find_all('script',recursive=False)]
 wrapper=dom.new_tag('div');wrapper.attrs={key:value for key,value in body.attrs.items() if key!='class'};wrapper['data-tracker-root']=family;wrapper['style']='position:relative;width:100%;height:100%'
 for node in list(body.contents):
  if getattr(node,'name',None)=='script':continue
  wrapper.append(copy.deepcopy(node))
 for canvas in wrapper.find_all('canvas'):canvas.decompose()
 host.clear()
 for script in scripts:host.append(script)
 host.append(wrapper)
 serviceNames=['dragon_tracker_public.json','starship_tracker_public.json'] if family=='vehicle-tracker' else ['dragon_public.json']
 config=dom.new_tag('script',attrs={'type':'application/json','class':'tracker-path-map'});config.string=json.dumps({'assets':mapping,'snapshots':{name:"@path('public/assets/data/trackers/"+name+"')" for name in serviceNames},'live':{name:'https://content.spacex.com/cms-assets/'+name for name in serviceNames}},separators=(',',':'));host.append(config)
 var='vehicleTrackerElement' if family=='vehicle-tracker' else 'followDragonElement'
 needle='var '+var+' = document.querySelector("'+family+'");';assert needle in js
 js=js.replace(needle,needle+'\nvar serviceUrls = JSON.parse('+var+'.querySelector(".tracker-path-map").textContent);\nvar assetUrls = serviceUrls.assets;\nvar frozenServices = document.querySelector(\'meta[name="spacex-service-mode"]\')?.content === "frozen" || new URLSearchParams(location.search).get("referenceServices") === "frozen";')
 js=js.replace(var+'.querySelector("body")',var+'.querySelector("[data-tracker-root]")')
 for url in urls:js=js.replace(json.dumps(url),'assetUrls['+json.dumps(url)+']')
 for name in serviceNames:
  needle="assetsBaseUrl + '/"+name+"?'";assert needle in js
  js=js.replace(needle,'(frozenServices ? serviceUrls.snapshots['+json.dumps(name)+'] : serviceUrls.live['+json.dumps(name)+']) + "?"')
 js=js.replace('window.updateAngular','window.onTrackerUpdate')
 engine='public/assets/js/'+family+'-renderer.js'
 for root in (H,A):(root/engine).write_text('/* Delivered public vanilla renderer; native wrapper/path adapter. Source SHA256: '+hashlib.sha256(original.read_bytes()).hexdigest()+' */\n'+js)
 if family=='vehicle-tracker':
  script=dom.new_tag('script',attrs={'src':"@path('public/assets/js/tracker-controls.js')",'defer':''});host.append(script)
 script=dom.new_tag('script',attrs={'src':"@path('"+engine+"')?v="+hashlib.sha256(js.encode()).hexdigest()[:12],'type':'text/javascript'});host.append(script)
 fragment=str(host)
 partial=H/'templates/trackers'/ (family+'.html');partial.parent.mkdir(parents=True,exist_ok=True);partial.write_text(fragment+'\n')
 # Preserve each standalone page wrapper while replacing only the invalid nested-document host.
 old=str(BeautifulSoup(text,'html.parser').find(family));assert old in text,source
 source.write_text(text.replace(old,"@input('templates/trackers/"+family+".html')",1))
 agent=A/'content'/family/'index.html';agentText=agent.read_text();old=str(BeautifulSoup(agentText,'html.parser').find(family));assert old in agentText,agent;agent.write_text(agentText.replace(old,fragment,1))
 records.append({'family':family,'sourceSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'textures':len(urls),'snapshotEndpoints':serviceNames,'productionTelemetry':'Original public URLs','offlineTelemetry':'Explicit frozen public JSON snapshots'})
for root in (H,A):(root/'investigation/evidence/tracker-runtime-recovery.json').write_text(json.dumps({'families':records,'sourceWrapperCorrection':'nested body becomes a scoped div','browserParityAccepted':False},indent=2)+'\n')
print('Recovered standalone tracker renderer families:',len(records))
