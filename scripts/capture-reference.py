"""Explicit public GET acquisition, with completion receipts. Never a build stage."""
from pathlib import Path
from urllib.parse import urlsplit
import re,json,subprocess,hashlib,datetime,concurrent.futures
R=Path(__file__).resolve().parents[2]/'spacex-baseline'; C=R/'capture';C.mkdir(parents=True,exist_ok=True)
def expected_bytes(headers):
 ranges=re.findall(r'content-range:\s*bytes \d+-\d+/(\d+)',headers,re.I)
 if ranges:return int(ranges[-1])
 lengths=re.findall(r'content-length:\s*(\d+)',headers,re.I)
 return int(lengths[-1]) if lengths else None

def capture(url):
 u=urlsplit(url);p=C/u.netloc/u.path.lstrip('/');p=p/'index.html' if not Path(u.path).suffix else p;p.parent.mkdir(parents=True,exist_ok=True)
 h=Path(str(p)+'.headers'); receipt=Path(str(p)+'.receipt.json');oldh=h.read_text() if h.exists() else '';expected=expected_bytes(oldh);valid=False
 if receipt.exists():
  prior=json.loads(receipt.read_text());expected=expected or prior.get('expectedBytes')
 if p.is_file() and receipt.exists():
  prior=json.loads(receipt.read_text());valid=prior.get('transferComplete') and prior['bytes']==p.stat().st_size and prior['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
 elif p.is_file() and expected is not None and p.stat().st_size==expected:valid=True
 status='cached';err='';complete=valid
 if not valid:
  if p.is_file() and p.stat().st_size and expected is None:
   head=subprocess.run(['curl','-sSI','--max-time','30',url],capture_output=True,text=True)
   if head.returncode==0 and expected_bytes(head.stdout) is not None:
    oldh=head.stdout;expected=expected_bytes(oldh);h.write_text(oldh)
  resume=p.is_file() and p.stat().st_size>0 and expected is not None and p.stat().st_size<expected and ('accept-ranges: bytes' in oldh.lower() or 'content-range:' in oldh.lower())
  for attempt in range(6):
   args=['curl','-sSL','--max-time','45','-D',str(h),'-w','%{http_code}',url,'-o',str(p)]
   if resume:args[1:1]=['-C','-']
   x=subprocess.run(args,capture_output=True,text=True);status=x.stdout;err=x.stderr
   headers=h.read_text() if h.exists() else ''
   new_expected=expected_bytes(headers)
   if new_expected is not None:expected=new_expected
   if not re.search(r'HTTP/\S+\s+(?:200|206)',headers):
    headers=oldh
    h.write_text(headers)
   else:oldh=headers
   complete=x.returncode==0 and p.is_file() and (expected is None or p.stat().st_size==expected)
   if complete:break
   resume=p.is_file() and p.stat().st_size>0 and expected is not None and p.stat().st_size<expected and ('accept-ranges: bytes' in headers.lower() or 'content-range:' in headers.lower())
   if status not in ['000','200','206']:break
 b=p.read_bytes() if p.is_file() else b''
 headers=h.read_text() if h.exists() else oldh
 responseStatus=re.findall(r'HTTP/\S+\s+(\d+)',headers)
 row={'url':url,'path':str(p.relative_to(R)),'status':responseStatus[-1] if responseStatus else status,'transferComplete':complete,'expectedBytes':expected,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':err[:160]}
 receipt.write_text(json.dumps(row,indent=2)+'\n');return row

def discover_initial():
 runtime=(C/'runtime.56febfaf067bbae1.js').read_text();chunks=re.findall(r'(\d+):"([a-f0-9]{16})"',runtime)
 urls=['https://www.spacex.com/'+('common' if n=='8592' else n)+'.'+h+'.js' for n,h in chunks]
 main=(C/'main.38aaaafc31bc4ec8.js').read_text();apis=set(re.findall(r'"(api/spacex-website/[^"+]+)"',main));urls+=['https://content.spacex.com/'+a for a in apis if not a.endswith('/')]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(capture,sorted(set(urls))))
 (R/'initial-discovery.json').write_text(json.dumps({'inputs':rows},indent=2)+'\n');print('Initial inputs:',len(rows),'incomplete:',sum(not x['transferComplete'] for x in rows),flush=True)
if __name__=='__main__':discover_initial()
