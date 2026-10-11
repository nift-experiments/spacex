"""Explicit recovery of the frozen launch table; not a routine build step."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
import json,html,hashlib
W=Path(__file__).resolve().parents[2];H=W/'spacex';A=W/'spacex-agent';B=W/'spacex-baseline'
source=B/'capture/content.spacex.com/api/spacex-website/launches-page-tiles/index.html'
items=json.loads(source.read_text());local=ZoneInfo('Australia/Melbourne')
types={'starship':'Starship Flight Tests','hsf':'Human Spaceflight','resupply':'Space Station Resupply','science':'Science','commercialSatellite':'Commercial / International','rideshare':'Rideshare Program','nssl':'National Security','starlink':'Starlink','starman':'Starman'}
standard={'LC-39A, FLORIDA':-5,'SLC-40, FLORIDA':-5,'SLC-4E, CALIFORNIA':-8,'STARBSE, TEXAS':-6,'PAD 1, STARBASE':-6,'PAD 2, STARBASE':-6,'STARBASE PAD 1':-6,'STARBASE PAD 2':-6,'OMELEK ISLAND':12}
rows=[]
for v in items:
 if v['missionStatus']!='final':continue
 over=v.get('override') or {};date=over.get('date') or over.get('windowOpenDate') or v['launchDate'];time=over.get('time') or over.get('windowOpenTime') or v['launchTime'] or '00:00:00'
 stamp=datetime.fromisoformat(date+'T'+time).replace(tzinfo=local)
 if over.get('date') or over.get('windowOpenDate'):
  site=v['launchSite'].upper();offset=standard.get(site)
  if offset is not None:
   dst=bool(stamp.astimezone(ZoneInfo('America/New_York')).dst());offset+=int(dst and site!='OMELEK ISLAND');stamp=stamp.replace(tzinfo=timezone(timedelta(hours=offset))).astimezone(local)
 key='launches/'+v['link']+'/'
 rows.append({'title':v['title'],'vehicle':v['vehicle'] or '', 'launchSite':v['launchSite'] or '', 'returnSite':v['returnSite'] or '', 'missionType':types.get(v['missionType'],'') or '', 'directToCell':'true' if v['directToCell'] else 'false','year':str(stamp.year),'date':stamp.strftime('%B %d, %Y').replace(' 0',' '),'timestamp':stamp.timestamp(),'route':key})
rows.sort(key=lambda r:r['timestamp'],reverse=True)
for index,r in enumerate(rows):r['position']=index
tracked={x['name'] for x in json.loads((H/'.nift/tracked.json').read_text())['tracked']};missing=[r['route'] for r in rows if r['route'] not in tracked];assert not missing,missing
(H/'data/launches.json').write_text(json.dumps({'items':rows,'captureTimezone':'Australia/Melbourne'},indent=2)+'\n')
partial='''<tr data-sx="upcoming-launches-page" tabindex="0" data-route="@path('$[row.route]')" data-title="$[row.title]" data-mission-type="$[row.missionType]" data-direct-to-cell="$[row.directToCell]" data-vehicle="$[row.vehicle]" data-launch-site="$[row.launchSite]" data-return-site="$[row.returnSite]" data-year="$[row.year]" @if(row.position >= 10){hidden}>
<td class="mission-name" data-sx="upcoming-launches-page"><p data-sx="upcoming-launches-page">$[row.title]</p></td><td class="vehicle-name" data-sx="upcoming-launches-page">$[row.vehicle]</td><td class="launch-site" data-sx="upcoming-launches-page">$[row.launchSite]</td><td class="return-site" data-sx="upcoming-launches-page">$[row.returnSite]</td><td class="launch-date" data-sx="upcoming-launches-page">$[row.date]</td></tr>\n'''
(H/'templates/launch-row.html').write_text(partial)
for p in (H,A):
 f=p/'content/launches/index.html';s=f.read_text();d=BeautifulSoup(s,'html.parser');table=d.select('table.missions-table')[-1];body=table.select_one('tbody');header='';old=str(body)
 if p==H:
  replacement='<tbody data-sx="upcoming-launches-page" data-completed-launches>'+header+"@json(launches, 'data/launches.json')\n@for(row : launches.items){@input('templates/launch-row.html')}\n</tbody>"
 else:
  replacement='<tbody data-sx="upcoming-launches-page" data-completed-launches>'+header
  for r in rows:
   text=partial
   import re
   text=re.sub(r'@if\(row.position >= 10\)\{hidden\}','hidden' if r['position']>=10 else '',text)
   text=text.replace("@path('$[row.route]')","@path('"+r['route']+"')")
   for k,val in r.items():text=text.replace('$[row.'+k+']',html.escape(str(val),quote=True))
   replacement+=text
  replacement+='</tbody>'
 # Replace serialized body from the original maintained DOM, leaving surrounding source intact.
 assert old in s,'Unexpected serialized body differs from maintained source; do not overwrite blindly'
 f.write_text(s.replace(old,replacement,1))
 evidence={'rows':len(rows),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'captureTimezone':'Australia/Melbourne','firstTen':[{'title':r['title'],'date':r['date'],'route':r['route']} for r in rows[:10]],'sourceModel':'JSON and Nift row template' if p==H else 'Maintained HTML rows','browserParityAccepted':False}
 (p/'investigation/evidence/launch-list-recovery.json').write_text(json.dumps(evidence,indent=2)+'\n')
print('Recovered completed launches:',len(rows))
