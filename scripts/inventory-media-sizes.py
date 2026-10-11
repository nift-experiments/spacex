"""Read public media references and HEAD metadata; do not fetch stream payloads."""
from pathlib import Path
import json,subprocess,concurrent.futures,re
R=Path(__file__).resolve().parents[2]/'spacex-baseline';urls={}
def walk(d,key=''):
 if isinstance(d,dict):
  for k,v in d.items():
   if k!='formats':walk(v,k)
 elif isinstance(d,list):
  for v in d:walk(v,key)
 elif isinstance(d,str) and d.startswith(('https://content.spacex.com/','https://sxcontent9668.azureedge.us/')) and d.endswith(('.mp4','.m3u8','.webm')):urls.setdefault(d,set()).add(key)
for p in (R/'capture/content.spacex.com/api').rglob('index.html'):
 try:walk(json.loads(p.read_text()))
 except:pass
print('Referenced media URLs',len(urls),flush=True)
def head(u):
 x=subprocess.run(['curl','-sSLI','--max-time','20',u],capture_output=True,text=True);hs=x.stdout;lengths=re.findall(r'content-length:\s*(\d+)',hs,re.I);codes=re.findall(r'HTTP/\S+\s+(\d+)',hs)
 return {'url':u,'fields':sorted(urls[u]),'status':codes[-1] if codes else None,'bytes':int(lengths[-1]) if lengths else None,'error':x.stderr[:100]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(head,sorted(urls)))
(R/'media-size-inventory.json').write_text(json.dumps(rows,indent=2)+'\n');print('Known MP4 bytes',sum(x['bytes'] or 0 for x in rows if x['url'].endswith('.mp4')),'missing sizes',sum(x['bytes'] is None for x in rows),'MP4s',sum(x['url'].endswith('.mp4') for x in rows),flush=True)
