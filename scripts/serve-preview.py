#!/usr/bin/env python3
"""Local publication preview; explicit service isolation for parity tests."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse, io
p=argparse.ArgumentParser()
p.add_argument('--port',type=int,default=4173)
p.add_argument('--offline-services',action='store_true',help='Block external frames, connections and all form submission during parity verification')
a=p.parse_args()
class Preview(SimpleHTTPRequestHandler):
 def send_head(self):
  if a.offline_services:
   candidate=Path(self.translate_path(self.path))
   if candidate.is_dir():candidate=candidate/'index.html'
   if candidate.is_file() and candidate.suffix=='.html':
    content=candidate.read_text().replace('</head>','<meta name="spacex-service-mode" content="frozen"></head>',1).encode()
    self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.end_headers();return io.BytesIO(content)
  return super().send_head()
 def end_headers(self):
  if a.offline_services:
   self.send_header('Content-Security-Policy',"frame-src 'none'; connect-src 'self'; form-action 'none'")
  super().end_headers()
root=Path(__file__).resolve().parents[1]/'public'
ThreadingHTTPServer(('127.0.0.1',a.port),partial(Preview,directory=str(root))).serve_forever()
