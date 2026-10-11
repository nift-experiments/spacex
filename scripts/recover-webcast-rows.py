"""Recover the bounded public multi-webcast list from frozen CMS input."""
from pathlib import Path
from urllib.parse import urlsplit
from datetime import date
import hashlib, html, json, shutil
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';B=W/'spacex-baseline'
if (H/'templates/webcast-list.html').exists():raise SystemExit('Already recovered; maintain sources directly')
files=set();pending={};records=[]
def asset(value):
 if not value:return ''
 u=urlsplit(value['url']);f=B/'capture'/u.netloc/u.path.lstrip('/');r=json.loads(Path(str(f)+'.receipt.json').read_text());digest=hashlib.sha256(f.read_bytes()).hexdigest()
 assert r['transferComplete'] and r['sha256']==digest and f.stat().st_size==r['bytes'],f
 candidates=['public/assets/media/'+f.name,'public/assets/recovered/'+u.netloc+u.path]
 for target in candidates:
  if (H/target).is_file() and (A/target).is_file() and hashlib.sha256((H/target).read_bytes()).hexdigest()==digest and hashlib.sha256((A/target).read_bytes()).hexdigest()==digest:return target
 target='public/assets/recovered/webcasts/'+digest+f.suffix;files.add(target)
 for root in (H,A):
  p=root/target;p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,p
  else:shutil.copyfile(f,p)
 return target
row='''<div class="webcast-content"><img loading="lazy" @if(webcast.desktopPath){src="@path('$[webcast.desktopPath]')"} @if(webcast.mobilePath){data-mobile="@path('$[webcast.mobilePath]')"}><div class="webcast-info"><span class="webcast-title">$[webcast.title]</span>@if(webcast.dateLabel){<span class="webcast-date">$[webcast.dateLabel]</span>}</div>@if(webcast.supportedType){<span class="sx-button"><a class="spx-button primary" tabindex="0" role="button" aria-label="Watch $[webcast.title]" data-webcast-index="$[webcast.nativeIndex]" style="padding-left:20px;padding-right:20px;margin-top:0"><div class="arrow icon slide">@input('templates/arrow.html')</div></a></span>}</div>'''
for p in sorted((H/'data/missions').glob('*.json')):
 model=json.loads(p.read_text());webcasts=model.get('webcasts') or []
 if len(webcasts)<=1:continue
 rendered=[]
 for index,webcast in enumerate(webcasts):
  webcast['desktopPath']=asset(webcast.get('imageDesktop'));webcast['mobilePath']=asset(webcast.get('imageMobile'));webcast['nativeIndex']=index;webcast['supportedType']=webcast.get('streamingVideoType') in ('x.com','x-live-studio','youtube');webcast['dateLabel']=date.fromisoformat(webcast['date']).strftime('%b %-d, %Y') if webcast.get('date') else ''
  image='<img loading="lazy"'+(' src="@path(\''+webcast['desktopPath']+'\')"' if webcast['desktopPath'] else '')+(' data-mobile="@path(\''+webcast['mobilePath']+'\')"' if webcast['mobilePath'] else '')+'>'
  title=html.escape(webcast['title'] or '');stamp='<span class="webcast-date">'+webcast['dateLabel']+'</span>' if webcast['dateLabel'] else ''
  control='<span class="sx-button"><a class="spx-button primary" tabindex="0" role="button" aria-label="Watch '+html.escape(webcast['title'] or '',quote=True)+'" data-webcast-index="'+str(index)+'" style="padding-left:20px;padding-right:20px;margin-top:0"><div class="arrow icon slide">@input(\'templates/arrow.html\')</div></a></span>' if webcast['supportedType'] else ''
  rendered.append('<div class="webcast-content">'+image+'<div class="webcast-info"><span class="webcast-title">'+title+'</span>'+stamp+'</div>'+control+'</div>')
 pending[p]=json.dumps(model,indent=2)+'\n'
 a=A/'content/launches'/p.stem/'index.html';text=a.read_text();assert '<div class="webcast-wrapper">' not in text,a
 marker='<div class="bottom">';start=text.index(marker);end=text.index('</div></div>',start)+len('</div></div>')
 # Crew cards immediately follow prose, so the webcast list is inserted after them.
 if '<div class="astronauts-wrapper">' in text:
  end=text.index('<div class="astronauts-wrapper">',end);tail=text[end:];end+=tail.index('</div></div></div>')+len('</div></div></div>')
 pending[a]=text[:end]+'\n<div class="webcast-wrapper"><div class="webcast-header"><h2>Webcast</h2></div>'+''.join(rendered)+'</div>\n'+text[end:]
 records.append({'mission':p.stem,'rows':len(webcasts)})
for p,text in pending.items():p.write_text(text)
(H/'templates/webcast-list.html').write_text('@for(webcast : mission.webcasts){@if(loop.length > 1){@if(loop.first){<div class="webcast-wrapper"><div class="webcast-header"><h2>Webcast</h2></div>}'+row+'@if(loop.last){</div>}}}\n')
p=H/'templates/mission.html';s=p.read_text();marker="@input('templates/mission-crew.html')";assert marker in s;p.write_text(s.replace(marker,marker+"\n@input('templates/webcast-list.html')",1))
for root in (H,A):(root/'investigation/evidence/webcast-list-recovery.json').write_text(json.dumps({'missions':records,'newMaintainedAssets':len(files),'sourceModule':'8800.85e5c607ebe65b77.js','visibilityRule':'webcasts.length > 1','browserParityAccepted':False},indent=2)+'\n')
(B/'webcast-extra-files.json').write_text(json.dumps(sorted(files),indent=2)+'\n')
print('Multi-webcast lists:',len(records),'rows:',sum(x['rows'] for x in records),'new assets:',len(files))
