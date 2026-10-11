import json,subprocess,re,concurrent.futures
from pathlib import Path
B=Path(__file__).resolve().parents[2]/'spacex-baseline';p=B/'media-preservation-manifest.json';rows=json.loads(p.read_text());out=B/'media-heads';out.mkdir(exist_ok=True)
def inspect(row):
 import hashlib
 path=out/(hashlib.sha256(row['url'].encode()).hexdigest()+'.headers')
 result=subprocess.run(['curl','-sSLI','--max-time','25','--retry','1',row['url']],capture_output=True,text=True)
 path.write_text(result.stdout)
 blocks=re.split(r'\r?\n\r?\n',result.stdout.strip());block=next((b for b in reversed(blocks) if b.startswith('HTTP/')),'');headers={}
 for line in block.splitlines()[1:]:
  if ':' in line:
   k,v=line.split(':',1);headers[k.lower()]=v.strip()
 codes=re.findall(r'HTTP/\S+\s+(\d+)',result.stdout)
 row.update({'contentType':headers.get('content-type'),'contentTypeBasis':'captured HEAD response','contentLength':int(headers['content-length']) if headers.get('content-length','').isdigit() else row['contentLength'],'etag':headers.get('etag'),'lastModified':headers.get('last-modified'),'capturedStatus':codes[-1] if codes else None,'responseHeaders':headers,'headError':result.stderr[:200]})
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for n,row in enumerate(pool.map(inspect,rows),1):
  if n%20==0:print('HEAD metadata',n,flush=True)
p.write_text(json.dumps(rows,indent=2)+'\n'); print('Metadata complete',len(rows),flush=True)
