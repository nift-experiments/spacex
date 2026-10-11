"""Freeze HLS manifest closure and an explicit initial three-segment playback window.
This is representative playback evidence, not a complete video archive.
"""
from pathlib import Path
from urllib.parse import urljoin
import importlib.util,json,concurrent.futures
p=Path(__file__).with_name('capture-reference.py');spec=importlib.util.spec_from_file_location('capture',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
policy=json.loads((m.R/'media-preservation-manifest.json').read_text());urls={x['url'] for x in policy if x['url'].endswith('.m3u8')}; seen=set();records=[]
while urls:
 batch=sorted(urls-seen)
 if not batch:break
 seen.update(batch);urls=set()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for row in pool.map(m.capture,batch):
   records.append(row)
   if not row['transferComplete'] or row['status'] not in ('200','206','cached'):continue
   text=(m.R/row['path']).read_text();references=[urljoin(row['url'],line.strip()) for line in text.splitlines() if line.strip() and not line.startswith('#')]
   urls.update(u for u in references if '.m3u8' in u)
   segments=[u for u in references if '.m3u8' not in u][:3]
   for segment in segments:records.append(m.capture(segment))
   # Initialization fragments and encryption keys are necessary even in a bounded window.
   import re
   for uri in re.findall(r'URI="([^"]+)"',text):
    target=urljoin(row['url'],uri)
    if '.m3u8' in target:urls.add(target)
    else:records.append(m.capture(target))
   (m.R/'playback-window-progress.json').write_text(json.dumps({'scope':'first three segments per rendition; remaining stream not offline preserved','inputs':records},indent=2)+'\n')
   print('manifest',len(seen),'records',len(records),flush=True)
(m.R/'playback-window.json').write_text(json.dumps({'scope':'initial three segments per rendition only; no complete stream preservation claim','inputs':records},indent=2)+'\n')
print('Playback capture complete',len(records),flush=True)
