/* Public component variants are maintained HTML, composed by Nift at build time. */
const applyState = (root, value) => {
  const key = root.dataset.nativeStateKey;
  const source = [...document.querySelectorAll('template[data-native-state-template]')].find(item => item.dataset.nativeStateTemplate === key && item.dataset.nativeStateValue === value);
  if (!source) return;
  const next = source.content.firstElementChild.cloneNode(true);
  root.querySelectorAll('video').forEach(video=>video.pause());
  root.replaceWith(next);
  selectMobileMedia(next);
  next.querySelector(`[data-native-state-value="${CSS.escape(value)}"]`)?.focus();
};
document.addEventListener('click', event => {
  const trigger = event.target.closest('[data-native-state-value][role="tab"]');
  const root = trigger?.closest('[data-native-state-key]');
  if (root) applyState(root, trigger.dataset.nativeStateValue);
});
document.addEventListener('keydown', event => {
  const trigger = event.target.closest('[data-native-state-value][role="tab"]');
  const root = trigger?.closest('[data-native-state-key]');
  if (!root || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
  event.preventDefault(); event.stopPropagation();
  const choices = [...root.querySelectorAll('[data-native-state-value][role="tab"]')];
  const index = choices.indexOf(trigger);
  const target = event.key === 'Home' ? 0 : event.key === 'End' ? choices.length-1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + choices.length) % choices.length;
  applyState(root, choices[target].dataset.nativeStateValue);
},true);
