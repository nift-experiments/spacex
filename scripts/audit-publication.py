from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
import json,re
W=Path(__file__).resolve().parents[2];result={}
project=Path(__file__).resolve().parents[1];expected=set(json.loads((project/'investigation/evidence/reference-routes.json').read_text())['paths'])
for name in (project.name,):
 p=W/name;tracked=json.loads((p/'.nift/tracked.json').read_text())['tracked'];pages=[x for x in tracked if x.get('output-ext')!='.m3u8'];actual={('/'+x['name'].strip('/')).rstrip('/') or '/' for x in pages};missing=[];count=0
 for page in pages:
  output=p/'public'/page['name'].strip('/')/'index.html';assert output.is_file(),output
  text=output.read_text();assert '@path(' not in text and '@input(' not in text,output
  dom=BeautifulSoup(text,'html.parser');urls=[]
  for node in dom.find_all(True):
   for attr in ('href','src','poster','data-mobile','data-media-stream','data-hls-runtime','data-route'):
    if node.has_attr(attr):urls.append((attr,node[attr]))
   if node.has_attr('srcset'):
    urls.extend(('srcset',entry.strip().split()[0]) for entry in node['srcset'].split(',') if entry.strip() and not entry.strip().startswith('data:'))
   if node.has_attr('style'):urls.extend(('style',x) for x in re.findall(r'url\(["\']?([^\)"\']+)',node['style']))
  for style in dom.select('style'):urls.extend(('css',x) for x in re.findall(r'url\(["\']?([^\)"\']+)',style.get_text()))
  for role,url in urls:
   parsed=urlsplit(url)
   if parsed.netloc.startswith(('127.0.0.1:', 'localhost:')):
    missing.append({'route':page['name'],'role':role,'url':url,'reason':'local reference-server dependency'});continue
   if not parsed.path or parsed.scheme or parsed.netloc:continue
   target=(p/'public'/unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else output.parent/unquote(parsed.path)
   target=target.resolve();count+=1
   if not target.exists() or (target.is_dir() and not (target/'index.html').exists()):missing.append({'route':page['name'],'role':role,'url':url})
 inherited=[row for row in missing if (row['route']=='launches/demosat/' and row['role']=='href' and row['url'].startswith('“https://')) or (row['route']=='humanspaceflight/earth/' and row['role']=='src' and row['url'].endswith('undefined/'))]
 report={'documentedInheritedSourceDefects':inherited,'unclassifiedMissingReferences':[row for row in missing if row not in inherited],'sourceBackedPagesAndRedirects':len(pages),'hlsManifests':len(tracked)-len(pages),'uniqueReferenceRoutes':len(expected),'missingRoutes':sorted(expected-actual),'additionalRoutes':sorted(actual-expected),'localReferencesChecked':count,'missingLocalReferences':missing,'browserParityAccepted':False}
 (p/'investigation/evidence/publication-audit.json').write_text(json.dumps(report,indent=2)+'\n');result[name]={k:v for k,v in report.items() if k!='missingLocalReferences'};result[name]['missingLocalReferenceCount']=len(missing);result[name]['firstMissingReferences']=missing[:8]
print(json.dumps(result,indent=2))

if any(r['missingRoutes'] or r['unclassifiedMissingReferences'] for r in result.values()):raise SystemExit('Unclassified publication route or reference defects')
