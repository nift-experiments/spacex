/* Observable webcast URL contract recovered from the pinned public mission component. */
const mission = document.querySelector('.sx-mission');
const webcastTemplate = mission?.querySelector('template.mission-webcasts');
if (webcastTemplate) {
  const streams = [...webcastTemplate.content.querySelectorAll('[data-video-id]')];
  const featured = streams.length === 1 ? streams[0] : streams.find(stream => stream.dataset.featured === 'true');
  const overlay = mission.querySelector('.video-overlay');
  const closeButton = overlay.querySelector('.mission-video-close');
  const trigger = mission.querySelector('[data-watch]');
  let lastFocus;
  const close = () => {
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    overlay.querySelector('iframe')?.remove();
    document.body.classList.remove('webcast-open');
    lastFocus?.focus();
  };
  const open = () => {
    if (!featured) return;
    const {videoId, videoType} = featured.dataset;
    const url = videoType === 'x.com' ? `https://platform.twitter.com/embed/Tweet.html?id=${encodeURIComponent(videoId)}&maxWidth=${.6 * innerWidth}px` : videoType === 'x-live-studio' ? `https://studio.x.com/embed/broadcast/${encodeURIComponent(videoId)}` : videoType === 'youtube' ? `https://www.youtube.com/embed/${encodeURIComponent(videoId)}?enablejsapi=1&version=3` : null;
    if (!url) return; // Undefined upstream video types remain unavailable.
    lastFocus = document.activeElement;
    const frame = document.createElement('iframe');
    frame.title = 'Mission webcast'; frame.allow = 'autoplay; fullscreen'; frame.allowFullscreen = true;
    frame.width = videoType === 'x.com' ? '60%' : '80%'; frame.height = videoType === 'x-live-studio' ? 'auto' : '80%';
    frame.classList.toggle('widescreen', videoType === 'x-live-studio'); frame.src = url;
    overlay.append(frame); overlay.classList.add('open'); overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('webcast-open'); closeButton.focus();
  };
  trigger?.setAttribute('role', 'button');
  trigger?.addEventListener('click', open);
  trigger?.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); open();} });
  closeButton.addEventListener('click', close);
  document.addEventListener('keydown', event => {
    if (!overlay.classList.contains('open')) return;
    if (event.key === 'Escape') close();
    if (event.key === 'Tab' && (event.shiftKey || document.activeElement !== closeButton)) {event.preventDefault(); closeButton.focus();}
  });
}
