"""One-time source recovery from frozen public CMS, not a normal build stage.
Authored pages retain compact structured data and editable prose partials.
"""
from pathlib import Path
from urllib.parse import urlsplit
from datetime import date
import json,shutil,hashlib,re,html,argparse
W=Path(__file__).resolve().parents[2];B=W/'spacex-baseline';H=W/'spacex';A=W/'spacex-agent';source=B/'capture/content.spacex.com/api/spacex-website'
launches=json.loads((source/'launches-page-tiles/index.html').read_text())+json.loads((source/'launches-page-tiles/upcoming/index.html').read_text());dates={x['link']:x.get('launchDate') for x in launches}
options=argparse.ArgumentParser(description=__doc__)
options.add_argument('--missions',nargs='+')
options.add_argument('--asset-dir',default='public/assets/media')
args=options.parse_args()
assets={};gaps=[];recovered=[]
def asset(value):
 if not value:return ''
 u=urlsplit(value['url']);p=B/'capture'/u.netloc/u.path.lstrip('/');receipt=Path(str(p)+'.receipt.json')
 if not p.is_file() or (receipt.exists() and not json.loads(receipt.read_text()).get('transferComplete')):raise FileNotFoundError(value['url'])
 target=args.asset_dir.rstrip('/')+'/'+Path(u.path).name
 for root in [H,A]:
  output=root/target;output.parent.mkdir(parents=True,exist_ok=True)
  if output.exists() and hashlib.sha256(output.read_bytes()).digest()!=hashlib.sha256(p.read_bytes()).digest():raise ValueError('asset filename collision '+target)
  if not output.exists():shutil.copyfile(p,output)
 assets[value['url']]={'path':target,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
 return target
# Paragraphs remain editable HTML. Internal authored links resolve through Nift.
def prose(text):
 def internal(m):
  url=m.group(2)
  parsed=urlsplit(url)
  if parsed.netloc in ('www.spacex.com','spacex.com'):url=parsed.path+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
  if not url.startswith('/') or url.startswith('//'):return m.group(0)
  target,sep,fragment=url.partition('#');name=target.strip('/')+'/' if target!='/' else '/'
  return m.group(1)+'="@path(\''+name+'\')'+(('#'+fragment) if sep else '')+'"'
 return re.sub(r'(href)="([^"]*)"',internal,text)
for path in sorted((source/'missions').glob('*/index.html')):
 if args.missions and path.parent.name not in args.missions:continue
 original=json.loads(path.read_text());key=original.get('missionId')
 if not key:
  gaps.append({'route':'/launches/'+path.parent.name,'class':'inherited API failure','status':404});continue
 try:
  model={'title':original['title'],'date':date.fromisoformat(dates[key]).strftime('%B %d, %Y') if dates.get(key) else '', 'imageDesktop':asset(original.get('imageDesktop')),'imageMobile':asset(original.get('imageMobile') or original.get('imageDesktop')), 'videoDesktop':asset(original.get('videoDesktop')),'videoMobile':asset(original.get('videoMobile') or original.get('videoDesktop')), 'cta':original.get('callToAction') or '', 'webcasts':original.get('webcasts') or [], 'preTimeline':original.get('preLaunchTimeline'),'postTimeline':original.get('postLaunchTimeline'),'infographicDesktop':asset(original.get('infographicDesktop')),'infographicMobile':asset(original.get('infographicMobile') or original.get('infographicDesktop')), 'gallery':[],'astronauts':original.get('astronauts') or [], 'followDragonEnabled':bool(original.get('followDragonEnabled')),'vehicleTrackerEnabled':bool(original.get('vehicleTrackerEnabled'))}
  for item in (original.get('carousel') or {}).get('carouselItems',[]):
   model['gallery'].append({'caption':item.get('caption') or '', 'desktop':asset(item.get('imageDesktop')),'mobile':asset(item.get('imageMobile') or item.get('imageDesktop'))})
 except (FileNotFoundError,ValueError) as exc:
  gaps.append({'route':'/launches/'+key,'class':'uncaptured required asset','detail':str(exc)});continue
 paragraphs=original.get('paragraphs') or [];split=(len(paragraphs)+1)//2
 for side,items in [('left',paragraphs[:split]),('right',paragraphs[split:])]:
  p=H/'prose/missions'/key/(side+'.html');p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text('\n'.join('<p class="innerhtml-from-cms-underline mb-1">'+prose(x['content'])+'</p>' for x in items)+'\n');model[side+'Prose']=str(p.relative_to(H))
 p=H/'data/missions'/ (key+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(model,indent=2)+'\n')
 p=H/'content/launches'/key/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('@json(mission, "data/missions/'+key+'.json")\n@input("templates/mission.html")\n')
 recovered.append({'route':'/launches/'+key,'name':'launches/'+key+'/','title':'SpaceX - '+model['title'],'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'openFeatures':['webcast playback'] if model['webcasts'] else []})
 if model['astronauts']:recovered[-1]['openFeatures'].append('astronaut cards')
 if model['followDragonEnabled'] or model['vehicleTrackerEnabled']:recovered[-1]['openFeatures'].append('flight tracking')
 if model['gallery']:recovered[-1]['openFeatures'].append('gallery interaction')
for root in [H,A]:
 p=root/'.nift/tracked.json';tracked=json.loads(p.read_text());lookup={x['name']:x for x in tracked['tracked']}
 for row in recovered:lookup.setdefault(row['name'],{'name':row['name'],'title':row['title'],'template':'templates/template.html'})['title']=row['title']
 tracked['tracked']=list(lookup.values());p.write_text(json.dumps(tracked,indent=2)+'\n')
 ledger=root/'investigation/evidence/mission-recovery.json'
 prior=json.loads(ledger.read_text()) if args.missions and ledger.exists() else {'recovered':[],'gaps':[]}
 replaced={'/launches/'+key for key in args.missions or []}
 ledger.write_text(json.dumps({'scope':'generated source coverage; not accepted browser parity','recovered':[x for x in prior['recovered'] if x['route'] not in replaced]+recovered,'gaps':[x for x in prior['gaps'] if x['route'] not in replaced]+gaps},indent=2)+'\n')
asset_ledger=B/'mission-owned-assets.json'
prior_assets=json.loads(asset_ledger.read_text()) if args.missions and asset_ledger.exists() else {}
asset_ledger.write_text(json.dumps({**prior_assets,**assets},indent=2)+'\n')
print('Authored mission source recovered',len(recovered),'gaps',len(gaps),'distinct maintained assets',len(assets),flush=True)
