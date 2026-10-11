"""Classify frozen public media metadata without downloading catalogue payloads."""
from pathlib import Path
from urllib.parse import urlsplit
import json
B=Path(__file__).resolve().parents[2]/'spacex-baseline'
relations={}
def walk(value, route, field=''):
 if isinstance(value,dict):
  route='/content/'+value['link'] if value.get('hdLink') and value.get('link') else route
  for key,item in value.items():
   if key!='formats':walk(item,route,key)
 elif isinstance(value,list):
  for item in value:walk(item,route,field)
 elif isinstance(value,str) and value.startswith('https://') and value.endswith(('.mp4','.m3u8','.webm')):
  relations.setdefault(value,set()).add((route,field))
for path in (B/'capture/content.spacex.com/api').rglob('index.html'):
 try:walk(json.loads(path.read_text()),'/'+str(path.parent.relative_to(B/'capture/content.spacex.com/api')))
 except (ValueError,TypeError):pass
rows=[]
for item in json.loads((B/'media-size-inventory.json').read_text()):
 url=item['url']; download=set(item['fields']) <= {'hdLink','fhdLink','uhdLink','fourKLink'}
 rows.append({'url':url,'filename':Path(urlsplit(url).path).name,'relationships':[{'route':r,'mediaRole':f} for r,f in sorted(relations.get(url,set()))], 'contentType':'application/vnd.apple.mpegurl' if url.endswith('.m3u8') else 'video/mp4','contentTypeBasis':'filename inference; HEAD verification pending','contentLength':item['bytes'],'capturedStatus':item['status'],'etag':None,'lastModified':None,'preservationMode':'remote-reference' if download else 'playback-review-required','sha256':None})
(B/'media-preservation-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
for repo in ['spacex','spacex-agent']:
 root=B.parent/repo
 (root/'investigation/MEDIA-POLICY.md').write_text('''# Accepted media scope\n\nOffline-preserved: HTML, CSS, JS, images, SVG, fonts, and all media required for captured visual/playback states. Background video must remain video. HLS manifests and required segment subsets must be captured where practical; playback-only classification requires browser evidence.\n\nRemote-referenced: large download/archive-only MP4 renditions. Preserve canonical URLs, visible controls, target/download semantics, page relationships, and captured HEAD metadata. No offline byte preservation claim applies to this class.\n\nHeavy frozen-reference media lives outside both repositories. Routine builds do not fetch live assets. Local maintained asset references use @path.\n\nScope decision accepted by the user on 2026-10-11. The former full-catalogue storage gate is resolved. S1 remains incomplete pending runtime-media closure and interaction reconciliation.\n''')
 (root/'investigation/STORAGE-GATE.md').write_text('''# Storage gate resolved\n\nThe user authorized preserving runtime/playback-critical assets locally while retaining large download-only media at original canonical URLs. See MEDIA-POLICY.md. The 320.6+ GiB catalogue will not be mirrored. Full offline archival parity is not claimed.\n''')
print('Recorded',len(rows),'media records;',sum(r['preservationMode']=='remote-reference' for r in rows),'download-only candidates; streaming candidates require playback review.')
