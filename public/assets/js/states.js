/* Public component variants are maintained HTML, composed by Nift at build time. */
const applyState = (root, value, focus = true) => {
  const key = root.dataset.nativeStateKey;
  const source = [...document.querySelectorAll('template[data-native-state-template]')].find(item => item.dataset.nativeStateTemplate === key && item.dataset.nativeStateValue === value);
  if (!source) return;
  const next = source.content.firstElementChild.cloneNode(true);
  root.querySelectorAll('video').forEach(video=>video.pause());
  root.querySelectorAll('.sx-reveal,.la-year').forEach(element=>revealFamilies.forEach(family=>family.observer.unobserve(element)));
  root.replaceWith(next);
  observeReveals(next);
  selectMobileMedia(next);
  if (focus) next.querySelector(`[data-native-state-value="${CSS.escape(value)}"]`)?.focus();
};
document.addEventListener('click', event => {
  const trigger = event.target.closest('[data-native-state-value][role="tab"]');
  const root = trigger?.closest('[data-native-state-key]');
  if (!root) return;
  if (root.dataset.nativeStateKey === 'Mid-South-environment') {
    environmentClickLock = trigger.dataset.nativeStateValue;
    selectEnvironment(root, environmentClickLock);
  } else applyState(root, trigger.dataset.nativeStateValue);
});
document.addEventListener('keydown', event => {
  const trigger = event.target.closest('[data-native-state-value][role="tab"]');
  const root = trigger?.closest('[data-native-state-key]');
  if (!root || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
  event.preventDefault(); event.stopPropagation();
  const choices = [...root.querySelectorAll('[data-native-state-value][role="tab"]')];
  const index = choices.indexOf(trigger);
  const target = event.key === 'Home' ? 0 : event.key === 'End' ? choices.length-1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + choices.length) % choices.length;
  if (root.dataset.nativeStateKey === 'Mid-South-environment') {
    environmentClickLock = choices[target].dataset.nativeStateValue;
    selectEnvironment(root, environmentClickLock);
  } else applyState(root, choices[target].dataset.nativeStateValue);
},true);

// Mid-South's public scroll chapters use hysteresis and a temporary click lock.
const environmentValues = ['Water', 'Power', 'Air'];
let environmentLastIndex = 0;
let environmentClickLock = null;
let environmentTimer;
const selectEnvironment = (root, value, focus = true) => {
  const current = root.querySelector('[role="tab"][aria-selected="true"]')?.dataset.nativeStateValue;
  if (current === value) return;
  clearTimeout(environmentTimer);
  const replace = () => {
    const revealed = root.querySelector('.memphis-steward__pin')?.classList.contains('sx-reveal--in');
    applyState(root, value, focus);
    const next = document.querySelector('[data-native-state-key="Mid-South-environment"]');
    if (revealed) next?.querySelector('.memphis-steward__pin')?.classList.add('sx-reveal--in');
  };
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) replace();
  else {
    root.querySelector('.memphis-steward__chapter')?.classList.add('is-out');
    environmentTimer = setTimeout(replace, 340);
  }
};
const updateEnvironment = () => {
  if (environmentClickLock !== null || matchMedia('(max-width: 900px)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const root = document.querySelector('[data-native-state-key="Mid-South-environment"]');
  const section = root?.querySelector('.memphis-steward');
  if (!section) return;
  const progress = Math.min(1, Math.max(0, -section.getBoundingClientRect().top / Math.max(1, section.offsetHeight - innerHeight)));
  const index = environmentLastIndex <= 0 ? (progress > .4 ? 1 : 0) : environmentLastIndex === 1 ? (progress > .74 ? 2 : progress < .26 ? 0 : 1) : (progress < .6 ? 1 : 2);
  if (index !== environmentLastIndex) {
    environmentLastIndex = index;
    selectEnvironment(root, environmentValues[index], false);
  }
};
const releaseEnvironmentLock = () => { environmentClickLock = null; };
window.addEventListener('scroll', updateEnvironment, {passive: true});
window.addEventListener('resize', updateEnvironment);
window.addEventListener('wheel', releaseEnvironmentLock, {passive: true});
window.addEventListener('touchmove', releaseEnvironmentLock, {passive: true});
updateEnvironment();
