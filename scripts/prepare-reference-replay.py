"""Build an offline replay from captured bytes; originals remain unchanged."""
from pathlib import Path
import shutil,json,re,hashlib
R=Path(__file__).resolve().parents[2]/'spacex-baseline';C=R/'capture';D=R/'replay';D.mkdir(exist_ok=True)
replay_version=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name("turnstile-unavailable.js").read_bytes()).hexdigest()[:12]
origins=['https://www.spacex.com','https://content.spacex.com','https://sxcontent9668.azureedge.us','https://challenges.cloudflare.com']
for p in C.rglob('*'):
 if not p.is_file() or p.name.endswith(('.headers','.receipt.json')):continue
 rel=p.relative_to(C)
 if rel.parts[0]=='www.spacex.com':rel=Path(*rel.parts[1:])
 elif rel.parts[0] in ['content.spacex.com','sxcontent9668.azureedge.us','challenges.cloudflare.com']:rel=Path('_reference')/rel
 elif len(rel.parts)==1 and p.suffix in ['.js','.css','.html']:pass
 else:continue
 dst=D/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if p.suffix in ['.js','.css','.html','.json']:
  try:s=p.read_text()
  except UnicodeDecodeError:shutil.copyfile(p,dst);continue
  for origin in origins[1:]:s=s.replace(origin,'http://127.0.0.1:4201/_reference/'+origin.removeprefix('https://'))
  s=s.replace(origins[0],'http://127.0.0.1:4201')
  s=s.replace('/turnstile/v0/api.js"','/turnstile/v0/api.js?replay='+replay_version+'"')
  
  if p.name=='environment.js':
   s=s.replace('content.spacex.com"','content.spacex.com/"')
  if p.name.startswith('runtime.') and p.suffix=='.js':
   s=s.replace('".js"','".js?replay='+replay_version+'"')
  if p.suffix=='.html':
   s=re.sub(r'(src="[^"]+\.js)(")',r'\1?replay='+replay_version+r'\2',s)
  dst.write_text(s)
 else:
  if dst.exists() or dst.is_symlink():dst.unlink()
  dst.symlink_to(p.resolve())
(D/'index.html').write_text((D/'home.html').read_text())
print('Offline replay prepared. CSP server blocks all outbound connections; root remains captured Angular shell.')
