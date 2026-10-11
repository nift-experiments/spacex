// Native bounded adaptation of public infographic-tile highlight/unhighlight behavior.
(() => {
  document.querySelectorAll('[data-iss-diagram]').forEach(root => {
    root.querySelectorAll('.node-marker,.node-text').forEach(node => {
      const match = node.id.match(/^node-(\d+)-(marker|text)$/);
      if (!match) return;
      const highlight = () => {
        root.querySelectorAll(`[id="node-${match[1]}-marker"]`).forEach(e => e.classList.add('highlight'));
        root.querySelectorAll('.node-text').forEach(e => e.classList.add(e.id === `node-${match[1]}-text` ? 'highlight' : 'dim'));
      };
      const clear = () => root.querySelectorAll('.node-marker,.node-text').forEach(e => e.classList.remove('highlight','dim'));
      node.addEventListener('mouseenter', highlight);
      node.addEventListener('mouseleave', clear);
      node.addEventListener('focus', highlight);
      node.addEventListener('blur', clear);
      node.tabIndex = 0;
    });
  });
})();
