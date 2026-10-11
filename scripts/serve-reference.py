"""Reference only: offline SPA replay with outbound network denied by CSP."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json,hashlib,re,argparse
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[2]/'spacex-baseline/replay'
options=argparse.ArgumentParser()
options.add_argument('--service-fixtures',action='store_true',help='Explicit unavailable-service UI reference, never a CAPTCHA success fixture')
options.add_argument('--port',type=int,default=4201)
args=options.parse_args()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def end_headers(self):
  self.send_header('Cache-Control','no-store')
  self.send_header('Content-Security-Policy',"default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; frame-src 'none'; form-action 'none'")
  super().end_headers()
 def do_POST(self):
  if self.path!='/__reference-capture__':self.send_error(405);return
  length=int(self.headers.get('Content-Length','0'))
  if length<=0 or length>2000000:self.send_error(413);return
  payload=self.rfile.read(length)
  try:
   record=json.loads(payload);route=urlsplit(record['referenceUrl']).path
   if not isinstance(record.get('html'),str) or not record['html'].startswith('<app-root'):raise ValueError('expected public rendered app root')
   width=int(record['viewport']['width']);height=int(record['viewport']['height'])
   slug=re.sub('[^A-Za-z0-9_-]','-',route).strip('-') or 'home'
   digest=hashlib.sha256(payload).hexdigest()[:12]
   target=R.parent/'browser-captures'/f'{slug}.{width}x{height}.{digest}.json';target.parent.mkdir(exist_ok=True);target.write_bytes(payload)
   body=json.dumps({'path':str(target.relative_to(R.parent))}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  except (ValueError,KeyError,TypeError):self.send_error(400,'Invalid reference capture')
 def do_GET(self):
  request_path=urlsplit(self.path).path
  if args.service_fixtures and request_path=='/_reference/challenges.cloudflare.com/turnstile/v0/api.js':
   content=Path(__file__).with_name('turnstile-unavailable.js').read_bytes()
   self.send_response(200);self.send_header('Content-Type','application/javascript');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
  if 'capture=1' in urlsplit(self.path).query and not request_path.startswith('/_reference/'):
   target=R/request_path.lstrip('/')
   if target.is_dir():target=target/'index.html'
   if not target.is_file():target=R/'index.html'
   html=target.read_text().replace('</body>','<script src="/__reference-export.js"></script></body>')
   html=html.replace('<html ', '<html data-reference-service-mode="'+('unavailable-fixture' if args.service_fixtures else 'captured-public-loader')+'" ',1)
   content=html.encode()
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
  if request_path=='/__reference-export.js':
   content=Path(__file__).with_name('reference-export.js').read_bytes()
   self.send_response(200);self.send_header('Content-Type','application/javascript');self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content);return
  target=R/request_path.lstrip('/')
  if request_path.startswith('/_reference/'):
   metadata=R.parent/'download-metadata-ranges.json'
   original='https://'+request_path.removeprefix('/_reference/')
   if metadata.exists():
    item=next((row for row in json.loads(metadata.read_text()) if row['url']==original),None)
    if item:
     requested=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range','bytes=0-'))
     if not requested:self.send_error(416);return
     start=int(requested[1]);end=int(requested[2]) if requested[2] else item['contentLength']-1
     # Prefer the longest available interval when approved metadata overlaps a probe.
     part=max((part for part in item['ranges'] if part['complete'] and part['start']<=start<=part['end']),key=lambda part:part['end'],default=None)
     if not part:self.send_error(503,'Unpreserved download payload range');return
     end=min(end,part['end']);source=R.parent/part['path']
     with source.open('rb') as stream:stream.seek(start-part['start']);body=stream.read(end-start+1)
     self.send_response(206);self.send_header('Content-Type',item['contentType'])
     self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f"bytes {start}-{end}/{item['contentLength']}")
     self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
   source=R.parent/'capture'/request_path.removeprefix('/_reference/')
   if target.is_dir():
    target=target/'index.html';source=source/'index.html'
   receipt=Path(str(source)+'.receipt.json')
   if receipt.exists():
    record=json.loads(receipt.read_text())
    if not record.get('transferComplete'):
     self.send_error(503,'Reference transfer incomplete');return
    if int(record.get('status') or 200)>=400:
     body=target.read_bytes() if target.is_file() else source.read_bytes()
     self.send_response(int(record['status']))
     self.send_header('Content-Type','application/json' if '/api/' in request_path else self.guess_type(str(source)))
     self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
   if not target.is_file():
    self.send_error(404,'Uncaptured reference input');return
   if request_path.endswith('/') or (R/request_path.lstrip('/')).is_dir():
    self.path=request_path.rstrip('/')+'/index.html'
  elif target.is_dir():
   self.path=request_path.rstrip('/')+'/index.html'
  elif not target.exists() and '.' not in request_path.split('/')[-1]:
   self.path='/index.html' 
  super().do_GET()
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
