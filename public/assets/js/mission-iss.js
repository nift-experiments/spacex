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

// Public launch-detail mobile branch: six steps; change image after step three.
document.querySelectorAll('[data-iss-controller]').forEach(root => {
  const mobile = root.querySelector('[data-iss-mobile]');
  const steps = JSON.parse(root.querySelector('.iss-step-data').textContent);
  const image = mobile.querySelector('[data-iss-flight-image]');
  const controls = [...mobile.querySelectorAll('[data-iss-direction]')];
  let index = 0;
  const show = () => {
    mobile.querySelector('[data-iss-progress]').textContent = `${index + 1} / ${steps.length}`;
    mobile.querySelector('.iss-infographic-text h2').textContent = `${index + 1}. ${steps[index].header}`;
    mobile.querySelector('.iss-infographic-text p').textContent = steps[index].text;
    image.src = index < 3 ? image.dataset.initialSrc : image.dataset.noseconeSrc;
    controls.forEach(control => {
      const disabled = Number(control.dataset.issDirection) < 0 ? index === 0 : index === steps.length - 1;
      control.classList.toggle('disabled', disabled);
      control.setAttribute('aria-disabled', String(disabled));
    });
  };
  controls.forEach(control => {
    const change = () => { index = Math.max(0, Math.min(steps.length - 1, index + Number(control.dataset.issDirection))); show(); };
    control.addEventListener('click', change);
    control.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); change(); } });
  });
  show();
});
