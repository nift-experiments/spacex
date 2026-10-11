"""Explicit corpus recovery of public crew cards; never a normal build stage."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib, html, json, shutil
W=Path(__file__).resolve().parents[2]; H=W/'spacex'; A=W/'spacex-agent'; B=W/'spacex-baseline'
partial='''@if(mission.astronauts){<div class="astronauts-wrapper"><div><h4 class="astronaut-title">Mission Crew</h4></div><div class="astronaut-cards-wrapper">@for(person : mission.astronauts){<div class="astronaut-card">@if(person.bioDisplayLink){<a href="$[person.bioDisplayLink]" target="_blank">}@if(person.portraitPath){<img class="astronaut-image" loading="lazy" src="@path('$[person.portraitPath]')">}@if(person.bioDisplayLink){</a><a href="$[person.bioDisplayLink]" target="_blank">}<span class="astronaut-name">$[person.name]</span>@if(person.bioDisplayLink){</a>}<span class="astronaut-description">@if(person.description){$[person.description]}</span></div>}</div></div>}\n'''
if (H/'templates/mission-crew.html').exists():raise SystemExit('Crew recovery already applied; edit maintained sources directly')
files=set();records=[]
for path in sorted((H/'data/missions').glob('*.json')):
 model=json.loads(path.read_text()); crew=model.get('astronauts') or []
 if not crew:continue
 cards=[]
 for person in crew:
  portrait=person.get('portrait'); target=''
  if portrait:
   u=urlsplit(portrait['url']); frozen=B/'capture'/u.netloc/u.path.lstrip('/'); receipt=json.loads(Path(str(frozen)+'.receipt.json').read_text())
   assert receipt['transferComplete'] and str(receipt['status']) in ('200','206'),frozen
   digest=hashlib.sha256(frozen.read_bytes()).hexdigest();assert digest==receipt['sha256'],frozen
   target='public/assets/recovered/crew/'+digest+frozen.suffix;files.add(target)
   for root in (H,A):
    dest=root/target;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest,dest
    else:shutil.copyfile(frozen,dest)
  bio=person.get('bioLink') or ''
  # Preserve the delivered Angular sanitizer defect for whitespace-prefixed URLs.
  display='unsafe:'+bio if bio and bio!=bio.strip() else bio
  person['portraitPath']=target;person['bioDisplayLink']=display
  image='<img class="astronaut-image" loading="lazy" src="@path(\''+target+'\')">' if target else ''
  anchor='<a href="'+html.escape(display,quote=True)+'" target="_blank">' if display else ''
  close='</a>' if display else ''
  cards.append('<div class="astronaut-card">'+anchor+image+close+anchor+'<span class="astronaut-name">'+html.escape(person['name'])+'</span>'+close+'<span class="astronaut-description">'+html.escape(person.get('description') or '')+'</span></div>')
 path.write_text(json.dumps(model,indent=2)+'\n')
 agent=A/'content/launches'/path.stem/'index.html';text=agent.read_text()
 marker='<div class="bottom">';start=text.index(marker);end=text.index('</div></div>',start)+len('</div></div>')
 fragment='<div class="astronauts-wrapper"><div><h4 class="astronaut-title">Mission Crew</h4></div><div class="astronaut-cards-wrapper">'+''.join(cards)+'</div></div>'
 if 'astronauts-wrapper' not in text:agent.write_text(text[:end]+'\n'+fragment+'\n'+text[end:])
 records.append({'mission':path.stem,'people':len(crew),'model':'Authored structured crew records; agent maintained HTML','whitespaceSanitizerDefectsRetained':sum(bool(p['bioDisplayLink'].startswith('unsafe:')) for p in crew)})
(H/'templates/mission-crew.html').write_text(partial)
p=H/'templates/mission.html';text=p.read_text();marker='@if(mission.preTimeline)';assert marker in text;p.write_text(text.replace(marker,"@input('templates/mission-crew.html')\n"+marker,1))
for root in (H,A):(root/'investigation/evidence/mission-crew-recovery.json').write_text(json.dumps({'missions':records,'uniquePortraits':len(files),'browserParityAccepted':False},indent=2)+'\n')
(B/'crew-extra-files.json').write_text(json.dumps(sorted(files),indent=2)+'\n')
print('Recovered crew:',len(records),'missions;',len(files),'unique portraits')
