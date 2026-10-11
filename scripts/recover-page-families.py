"""One-time public DOM recovery. Not called by production builds.

Recover readable, maintained HTML and semantic component-scoped CSS. This
does not implement Angular or accept captured interactions as working parity.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib, json, re, shutil, argparse, posixpath
from bs4 import BeautifulSoup, Comment

W = Path(__file__).resolve().parents[2]
R = W / 'spacex-baseline'
projects = [W / 'spacex', W / 'spacex-agent']
options = argparse.ArgumentParser(description=__doc__)
options.add_argument('--routes', nargs='+', help='Recover only named routes without overwriting other maintained pages')
args = options.parse_args()
selected = {route.strip('/') for route in args.routes} if args.routes else None
records = []
latest = {}
for candidate in (R / 'browser-captures').glob('*.json'):
    data = json.loads(candidate.read_text())
    route = urlsplit(data['referenceUrl']).path
    if data.get('viewport', {}).get('width') != 1280:
        continue
    if selected is not None and route.strip('/') not in selected:
        continue
    if route not in latest or data['capturedAt'] > latest[route][0]:
        latest[route] = (data['capturedAt'], candidate)

for capture in sorted(value[1] for value in latest.values()):
    record = json.loads(capture.read_text())
    route = urlsplit(record['referenceUrl']).path.strip('/')
    if not route or route.startswith('launches/'):
        continue
    dom = BeautifulSoup(record['html'], 'html.parser')
    videos = dom.select('video')
    if len(videos) == len(record.get('media', [])):
        for video, properties in zip(videos, record['media']):
            if properties.get('autoplay') and properties.get('muted'):
                video['muted'] = ''
    container = dom.select_one('.page-content-inner')
    if not container:
        continue
    pages = [tag for tag in container.children if getattr(tag, 'name', None)
             and tag.name not in ('header', 'footer', 'router-outlet')]
    if len(pages) != 1:
        raise ValueError(f'Unexpected page structure: {route}')
    page = pages[0]
    if not page.find(True):
        shadow = next((item for item in record.get('shadowRoots', []) if item['tag'] == page.name), None)
        if shadow:
            boundary = dom.new_tag('template', attrs={'shadowrootmode': 'open'})
            recovered_shadow = BeautifulSoup(shadow['html'], 'html.parser')
            for child in list(recovered_shadow.contents):
                boundary.append(child.extract())
            page.append(boundary)
    if not page.find(True):
        # Direct-entry submit routes can require navigation state. An empty
        # Angular host is not a recovered page or an acceptable fixture.
        continue
    if route.startswith('content/') and route.count('/') >= 2 and not page.select_one('.video-details'):
        continue
    statistics = {
        'vehicles/falcon-9': ('falcon-nine-stats', ['totalLaunches', 'totalLandings', 'totalReflights']),
        'vehicles/falcon-heavy': ('falcon-heavy-stats', ['totalLaunches', 'totalLandings', 'totalReflights']),
        'vehicles/dragon': ('dragon-stats', ['totalLaunches', 'totalIssVisits', 'totalReflights']),
    }
    statistics['vehicles'] = statistics['vehicles/dragon']
    statistic_source = statistics.get(route)
    statistics_data = None
    if statistic_source:
        api, fields = statistic_source
        statistics_data = json.loads((R / 'capture/content.spacex.com/api/spacex-website' / api / 'index.html').read_text())
        counters = page.select('.stat-number')
        if len(counters) != len(fields):
            raise ValueError(f'Unexpected statistics structure: {route}')
        for counter, field in zip(counters, fields):
            counter.string = str(statistics_data[field])
            counter['data-count-target'] = str(statistics_data[field])
    owners = {}
    for tag in dom.find_all(True):
        for attribute in tag.attrs:
            if attribute.startswith('_nghost-'):
                owners[attribute.removeprefix('_nghost-')] = tag.name
    used = set()
    for tag in [page, *page.find_all(True)]:
        for attribute in list(tag.attrs):
            if attribute.startswith(('_nghost-', '_ngcontent-')):
                prefix, identity = attribute.split('-', 1)
                role = owners.get(identity)
                if not role:
                    raise ValueError(f'Unknown CSS owner {identity}')
                tag['data-sx-host' if prefix == '_nghost' else 'data-sx'] = role
                used.add(identity)
                del tag[attribute]
            elif attribute in ('ng-version', 'routerlink', 'routerlinkactive'):
                del tag[attribute]
    for comment in page.find_all(string=lambda item: isinstance(item, Comment)):
        comment.extract()
    # Public Swiper custom elements put their wrapper in a shadow root.
    # Reconstruct that small presentation boundary as ordinary maintained DOM.
    for carousel in page.find_all('swiper-container'):
        carousel.name = 'div'
        carousel['class'] = ['sx-carousel']
        carousel['data-carousel-gap'] = carousel.get('space-between', '0')
        carousel.attrs.pop('slides-per-view', None)
        carousel.attrs.pop('space-between', None)
        wrapper = dom.new_tag('div', attrs={'class': 'swiper-wrapper'})
        for slide in list(carousel.children):
            if getattr(slide, 'name', None) == 'swiper-slide':
                slide.name = 'div'
                slide['class'] = ['swiper-slide']
                slide.attrs.pop('style', None)
                wrapper.append(slide.extract())
        carousel.append(wrapper)
    assets = set()

    def path_expression(value):
        parsed = urlsplit(value)
        if not value or value.startswith(('#', 'data:', 'blob:')):
            return value
        host = parsed.netloc
        path = unquote(parsed.path)
        if host in ('127.0.0.1:4201', 'localhost:4201'):
            if path.startswith('/_reference/'):
                host, path = path.removeprefix('/_reference/').split('/', 1)
                path = '/' + path
            else:
                host = 'www.spacex.com'
        elif host and host not in ('www.spacex.com', 'content.spacex.com', 'sxcontent9668.azureedge.us'):
            return value
        if not host:
            if parsed.scheme:
                return value
            host = 'www.spacex.com'
            path = posixpath.normpath('/' + path.lstrip('/'))
        source = R / 'capture' / host / path.lstrip('/')
        if source.is_file() and (path.startswith(('/assets/', '/cms-assets/', '/site-media/')) or Path(path).suffix.lower() in ('.woff', '.woff2', '.ttf', '.otf', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico', '.pdf', '.mp4', '.m3u8', '.ts', '.m4s', '.aac', '.mp3')):
            receipt = Path(str(source) + '.receipt.json')
            if receipt.exists() and not json.loads(receipt.read_text()).get('transferComplete'):
                raise ValueError(f'Incomplete runtime input {source}')
            destination = 'public/assets/recovered/' + host + path
            assets.add((str(source), destination))
            for project in projects:
                target = project / destination
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(source, target)
        elif host == 'www.spacex.com' and not Path(path).suffix:
            destination = path.strip('/') + '/' if path.strip('/') else '/'
            if destination == 'undefined/':return "@path('/')undefined/"
        else:
            # Preserve uncertain or downloadable URLs; classify before parity.
            return 'https://' + host + path + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
        suffix = ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
        binding = destination.removeprefix('public/').removesuffix('.m3u8') if destination.endswith('.m3u8') else destination
        return "@path('" + binding + "')" + suffix

    for tag in [page, *page.find_all(True)]:
        for attribute in ('href', 'src', 'poster'):
            if tag.has_attr(attribute):
                tag[attribute] = path_expression(tag[attribute])
        if tag.has_attr('style'):
            tag['style'] = re.sub(r'url\([\"\']?([^\)\"\']+)[\"\']?\)',
                                  lambda match: 'url(' + path_expression(match[1]) + ')', tag['style'])
    # Open form shadow DOM is a native encapsulation boundary, not Angular runtime.
    for embedded_style in page.find_all('style'):
        css = embedded_style.get_text()
        for identity, role in owners.items():
            css = css.replace('[_nghost-' + identity + ']', '[data-sx-host=\"' + role + '\"]')
            css = css.replace('[_ngcontent-' + identity + ']', '[data-sx=\"' + role + '\"]')
        css = re.sub(r'url\([\"\']?([^\)\"\']+)[\"\']?\)',
                     lambda match: 'url(' + path_expression(match[1]) + ')', css)
        embedded_style.string = css.replace('@', '\\@').replace('\\@path(', '@path(')
    styles = []
    for css in record['styles']:
        ids = set(re.findall(r'_ng(?:host|content)-([\w-]+)', css))
        if not ids or not ids.intersection(used):
            continue
        for identity in ids:
            role = owners.get(identity, 'unused-' + identity)
            css = css.replace('[_nghost-' + identity + ']', '[data-sx-host="' + role + '"]')
            css = css.replace('[_ngcontent-' + identity + ']', '[data-sx="' + role + '"]')
        css = css.replace('@', '\\@')
        css = re.sub(r'url\([\"\']?([^\)\"\']+)[\"\']?\)',
                     lambda match: 'url(' + path_expression(match[1]) + ')', css)
        styles.append(css)
    style_name = route.replace('/', '-') + '.html'
    swiper_css = next((css for css in record['styles'] if '.swiper-wrapper' in css and '_ngcontent-' not in css and '_nghost-' not in css), None)
    shared_styles = "@input('templates/swiper-styles.html')\n" if page.select_one('.sx-carousel') and swiper_css else ''
    html = shared_styles + "@input('templates/families/" + style_name + "')\n" + str(page) + '\n'
    for project in projects:
        target = project / 'content' / route / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        if shared_styles:
            structure = '\n.sx-carousel{position:relative;display:block;overflow:hidden;width:100%}.sx-carousel>.swiper-wrapper{display:flex;height:auto;gap:var(--sx-carousel-gap,0px)}.sx-carousel .swiper-slide{position:relative;display:block;width:100%;flex:0 0 100%}\n'
            (project / 'templates/swiper-styles.html').write_text('<style>\n' + swiper_css.replace('@', '\\@') + structure + '\n</style>\n')
        maintained_html = html
        if statistics_data and project.name == 'spacex':
            model = project / 'data/statistics' / (statistic_source[0] + '.json')
            model.parent.mkdir(parents=True, exist_ok=True)
            model.write_text(json.dumps(statistics_data, indent=2) + '\n')
            maintained = BeautifulSoup(str(page), 'html.parser')
            for counter, field in zip(maintained.select('.stat-number'), statistic_source[1]):
                counter.string = '$[statistics.' + field + ']'
                counter['data-count-target'] = '$[statistics.' + field + ']'
            maintained_html = "@json(statistics, 'data/statistics/" + statistic_source[0] + ".json')\n" + shared_styles + "@input('templates/families/" + style_name + "')\n" + str(maintained) + '\n'
        target.write_text(maintained_html)
        style = project / 'templates/families' / style_name
        style.parent.mkdir(parents=True, exist_ok=True)
        style.write_text('<style>\n' + '\n'.join(styles) + '\n</style>\n')
        tracking = project / '.nift/tracked.json'
        registry = json.loads(tracking.read_text())
        name = route + '/'
        registry['tracked'] = [item for item in registry['tracked'] if item['name'] != name]
        registry['tracked'].append({'name': name, 'title': record['title'], 'template': 'templates/template.html'})
        tracking.write_text(json.dumps(registry, indent=2) + '\n')
    records.append({'route': '/' + route, 'capture': capture.name,
                    'captureSha256': hashlib.sha256(capture.read_bytes()).hexdigest(),
                    'ownedAssets': len(assets), 'parityAccepted': False,
                    'openItems': ['responsive geometry', 'carousels and tabs', 'media controls',
                                  'animated statistics', 'link and asset closure']})
for project in projects:
    ledger = project / 'investigation/evidence/page-family-recovery.json'
    retained = json.loads(ledger.read_text()) if selected is not None and ledger.exists() else []
    recovered = {record['route'] for record in records}
    ledger.write_text(json.dumps([row for row in retained if row['route'] not in recovered] + records, indent=2) + '\n')
print('Recovered maintained family pages:', len(records))
