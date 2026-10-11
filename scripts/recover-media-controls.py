"""One-time media controls recovery from public DOM and frozen playlist data."""
from pathlib import Path
from urllib.parse import urlsplit
import json, re
from bs4 import BeautifulSoup, Comment
W = Path(__file__).resolve().parents[2]
R = W / 'spacex-baseline'
captures = [json.loads(path.read_text()) for path in (R / 'browser-captures').glob('*.json')]
modal_capture = max((row for row in captures if row.get('overlaysHtml') and 'DOWNLOAD THIS VIDEO' in row['overlaysHtml']), key=lambda row: row['capturedAt'])
overlay = BeautifulSoup(modal_capture['overlaysHtml'], 'html.parser')
container = overlay.select_one('.cdk-overlay-container')
container['hidden'] = ''
container['id'] = 'media-download-dialog'
container['role'] = 'dialog'
container['aria-modal'] = 'true'
container['aria-label'] = 'Download this video'
owners = {}
for tag in container.find_all(True):
    for attribute in tag.attrs:
        if attribute.startswith('_nghost-'): owners[attribute.removeprefix('_nghost-')] = tag.name
for tag in container.find_all(True):
    for attribute in list(tag.attrs):
        if attribute.startswith(('_nghost-', '_ngcontent-')):
            prefix, identity = attribute.split('-', 1)
            tag['data-sx-host' if prefix == '_nghost' else 'data-sx'] = owners[identity]
            del tag[attribute]
for comment in container.find_all(string=lambda node: isinstance(node, Comment)): comment.extract()
for link in container.find_all('a'):
    text = link.get_text(' ', strip=True).lower()
    if text in ('download', 'cancel'):
        link['data-download-action'] = text
        link['href'] = '#'
css = []
for style in modal_capture['styles']:
    ids = set(re.findall(r'_ng(?:host|content)-([\w-]+)', style))
    if not ids.intersection(owners): continue
    for identity in ids:
        role = owners.get(identity, 'unused-' + identity)
        style = style.replace('[_nghost-' + identity + ']', '[data-sx-host="' + role + '"]')
        style = style.replace('[_ngcontent-' + identity + ']', '[data-sx="' + role + '"]')
    css.append(style.replace('@', '\\@'))
modal_source = '<style>\n' + '\n'.join(css) + '\n[hidden]{display:none!important}\n</style>\n' + str(container) + '\n'

for project in [W / 'spacex', W / 'spacex-agent']:
    (project / 'templates/download-dialog.html').write_text(modal_source)
    quality_template = ('<div class="native-quality-options" hidden>\n'
                        '@for(quality : media.qualities){<button type="button" data-media-quality="$[quality.key]" '
                        'data-media-stream="@path(\'$[quality.stream]\')" '
                        'data-media-download="$[quality.download]">$[quality.label]</button>}\n</div>\n')
    if project.name == 'spacex':
        (project / 'templates/media-qualities.html').write_text(quality_template)
    for playlist_name in ('starship', 'starship-flight-tests', 'starship-talks'):
        playlist = json.loads((R / 'capture/content.spacex.com/api/spacex-website/media-playlist' / playlist_name / 'index.html').read_text())
        for media in playlist['media']:
            route = 'content/' + playlist_name + '/' + media['link']
            source = project / 'content' / route / 'index.html'
            if not source.exists(): continue
            qualities = []
            for key, label in [('hd', '720p'), ('fhd', '1080p'), ('uhd', '4k')]:
                stream = media.get(key + 'StreamingLink')
                if not stream: continue
                parsed = urlsplit(stream)
                stream_name = ('assets/recovered/' + parsed.netloc + parsed.path).removesuffix('.m3u8')
                qualities.append({'key': key, 'label': label, 'stream': stream_name,
                                  'download': media.get(key + 'Link') or ''})
            if not qualities: continue
            text = source.read_text()
            # Recovery is intentionally idempotent; never duplicate maintained controls.
            text = re.sub(r"^@json\(media, '[^']+'\)\n", '', text)
            text = re.sub(r"\n@input\('templates/media-qualities.html'\)\n", '\n', text)
            text = re.sub(r"\n@input\('templates/download-dialog.html'\)\n", '\n', text)
            text = re.sub(r'<div class="native-quality-options".*?</div>\n', '', text, flags=re.S)
            if project.name == 'spacex':
                model = project / 'data/media' / playlist_name / (media['link'] + '.json')
                model.parent.mkdir(parents=True, exist_ok=True)
                model.write_text(json.dumps({'title': media['title'], 'qualities': qualities,
                                             'description': media.get('description'), 'chapters': media.get('chapters')}, indent=2) + '\n')
                text = "@json(media, '" + str(model.relative_to(project)) + "')\n" + text
                text += "\n@input('templates/media-qualities.html')\n"
            else:
                controls = '<div class="native-quality-options" hidden>\n'
                for quality in qualities:
                    controls += ('<button type="button" data-media-quality="' + quality['key'] + '" '
                                 'data-media-stream="@path(\'' + quality['stream'] + '\')" '
                                 'data-media-download="' + quality['download'] + '">' + quality['label'] + '</button>\n')
                text += controls + '</div>\n'
            text += "\n@input('templates/download-dialog.html')\n"
            source.write_text(text)
print('Recovered shared download modal and maintained quality controls')
