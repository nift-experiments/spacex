/* Reference-only capture UI. Never shipped by either Nift project. */
const exportControl = document.createElement('button');
exportControl.id = 'reference-export';
exportControl.textContent = 'Export rendered reference';
exportControl.style.cssText = 'position:fixed;right:8px;bottom:8px;z-index:10000;padding:8px;background:#fff;color:#000';
exportControl.addEventListener('click', async () => {
  await document.fonts.ready;
  const root = document.querySelector('app-root');
  const shadowRoots = [];
  const collectShadow = node => {
    for (const host of node.querySelectorAll('*')) {
      if (!host.shadowRoot) continue;
      shadowRoots.push({tag: host.localName, html: host.shadowRoot.innerHTML});
      collectShadow(host.shadowRoot);
    }
  };
  collectShadow(root);
  const data = {
    shadowRoots,
    referenceUrl: location.origin + location.pathname,
    capturedAt: new Date().toISOString(),
    referenceServiceMode: document.documentElement.dataset.referenceServiceMode || 'captured-public-loader',
    title: document.title,
    viewport: { width: innerWidth, height: innerHeight },
    html: root.outerHTML,
    overlaysHtml: document.querySelector('.cdk-overlay-container')?.outerHTML || '',
    styles: Array.from(document.querySelectorAll('style')).map(node => node.textContent),
    headings: Array.from(root.querySelectorAll('h1,h2,h3')).map(node => {
      const rect = node.getBoundingClientRect();
      return { text: node.textContent, level: node.tagName, x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    }),
    media: Array.from(root.querySelectorAll('video')).map(node => ({ src: node.currentSrc, muted: node.muted, autoplay: node.autoplay, loop: node.loop, paused: node.paused, readyState: node.readyState })),
    links: Array.from(root.querySelectorAll('a')).map(node => ({ href: node.getAttribute('href'), text: node.textContent, target: node.getAttribute('target'), download: node.getAttribute('download') }))
  };
  const response = await fetch('/__reference-capture__', {
    method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)
  });
  const result = await response.json();
  let status = document.querySelector('#reference-export-status');
  if (!status) { status = document.createElement('div'); status.id = 'reference-export-status'; status.setAttribute('role','status'); status.style.cssText = exportControl.style.cssText + ';bottom:50px'; document.body.append(status); }
  status.textContent = response.ok ? 'Reference saved: ' + result.path : 'Reference export failed: ' + result.error;
});
document.body.append(exportControl);
