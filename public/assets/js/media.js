/* Media controls recovered from the public player and download contract. */
const player = document.querySelector('content-hub-video-tile');
const mediaOptions = [...document.querySelectorAll('[data-media-quality]')];
if (player && mediaOptions.length) {
  const video = player.querySelector('video');
  const poster = player.querySelector('[role="button"]');
  const qualityButton = document.querySelector('.filter-button[data-sx="filter"]');
  const qualityMenu = qualityButton?.parentElement.querySelector('.filter-content');
  const choices = [...(qualityMenu?.querySelectorAll('button') || [])];
  const dialog = document.querySelector('#media-download-dialog');
  const downloadTrigger = document.querySelector('spx-button[text="Download"] a');
  let lastFocus;
  let stream = video.getAttribute('src');
  let hls;
  let library;
  let generation = 0;
  const nativeHls = !!video.canPlayType('application/vnd.apple.mpegurl');
  if (!nativeHls) video.removeAttribute('src');
  const setStream = async (source, time = 0, resume = false) => {
    const current = ++generation;
    stream = source;
    if (!nativeHls && !window.Hls) {
      library ??= new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = document.querySelector('.native-quality-options').dataset.hlsRuntime;
        script.onload = resolve; script.onerror = reject; document.head.append(script);
      });
      await library;
    }
    if (current !== generation) return;
    hls?.destroy();
    video.addEventListener('loadedmetadata', () => {
      video.currentTime = Math.min(time, Number.isFinite(video.duration) ? video.duration : time);
      if (resume) video.play().catch(() => {});
    }, { once: true });
    if (nativeHls) { video.src = source; video.load(); }
    else if (window.Hls.isSupported()) {
      hls = new window.Hls(); hls.loadSource(source); hls.attachMedia(video);
    } else { video.src = source; video.load(); }
  };
  const play = async () => {
    poster.hidden = true;
    video.hidden = false;
    if (!nativeHls && !hls) await setStream(stream);
    video.play().catch(() => { /* Native controls remain available if autoplay is denied. */ });
  };
  poster.tabIndex = 0;
  poster.setAttribute('aria-label', 'Play video');
  poster.addEventListener('click', play);
  poster.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); play(); }
  });
  if (qualityButton && qualityMenu) {
    qualityMenu.hidden = true;
    qualityButton.setAttribute('aria-expanded', 'false');
    const closeQuality = () => {
      qualityMenu.hidden = true;
      qualityButton.setAttribute('aria-expanded', 'false');
    };
    qualityButton.addEventListener('click', () => {
      qualityMenu.hidden = !qualityMenu.hidden;
      qualityButton.setAttribute('aria-expanded', String(!qualityMenu.hidden));
    });
    choices.forEach(choice => {
      const option = mediaOptions.find(option => option.textContent.trim() === choice.textContent.trim());
      if (!option) { choice.hidden = true; return; }
      choice.addEventListener('click', () => {
        const time = video.currentTime;
        const resume = !video.paused;
        setStream(option.dataset.mediaStream, time, resume).catch(() => { /* Keep native controls and poster on failure. */ });
        choices.forEach(item => item.classList.toggle('selected', item === choice));
        closeQuality(); qualityButton.focus();
      });
    });
    document.addEventListener('click', event => {
      if (!qualityButton.parentElement.contains(event.target)) closeQuality();
    });
    qualityButton.parentElement.addEventListener('keydown', event => {
      if (event.key === 'Escape') { closeQuality(); qualityButton.focus(); }
    });
  }
  if (dialog && downloadTrigger) {
    const radios = [...dialog.querySelectorAll('input[type="radio"]')];
    const download = dialog.querySelector('[data-download-action="download"]');
    const cancel = dialog.querySelector('[data-download-action="cancel"]');
    const close = () => { dialog.hidden = true; lastFocus?.focus(); };
    const updateDownload = () => {
      const key = radios.find(radio => radio.checked)?.value;
      const option = mediaOptions.find(option => option.dataset.mediaQuality === key);
      if (!option?.dataset.mediaDownload) { download.removeAttribute('href'); return; }
      const url = new URL(option.dataset.mediaDownload);
      url.searchParams.append('download', 'true');
      download.href = url.href;
      download.download = url.pathname.split('/').pop() || 'download';
    };
    downloadTrigger.setAttribute('role', 'button');
    downloadTrigger.setAttribute('aria-haspopup', 'dialog');
    const open = () => {
      lastFocus = document.activeElement;
      const available = mediaOptions.filter(option => option.dataset.mediaDownload);
      const preferred = available.find(option => option.dataset.mediaQuality === 'fhd') ||
        available.find(option => option.dataset.mediaQuality === 'hd') || available[0];
      radios.forEach(radio => {
        radio.closest('.checkbox-container').hidden = !available.some(option => option.dataset.mediaQuality === radio.value);
        radio.checked = preferred?.dataset.mediaQuality === radio.value;
      });
      updateDownload(); dialog.hidden = false;
      radios.find(radio => radio.checked)?.focus();
    };
    downloadTrigger.addEventListener('click', event => { event.preventDefault(); open(); });
    downloadTrigger.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); open(); }
    });
    radios.forEach(radio => radio.addEventListener('change', updateDownload));
    cancel.addEventListener('click', event => { event.preventDefault(); close(); });
    dialog.querySelector('.cdk-overlay-backdrop').addEventListener('click', close);
    download.addEventListener('click', () => { if (download.hasAttribute('href')) close(); });
    dialog.addEventListener('keydown', event => {
      if (event.key === 'Escape') { event.preventDefault(); close(); }
      if (event.key === 'Tab') {
        const focusable = [...dialog.querySelectorAll('input, a[href]')].filter(item => !item.closest('[hidden]'));
        const first = focusable[0], last = focusable.at(-1);
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
  }
}

for (const link of document.querySelectorAll('.native-playlist-link')) {
  if (new URL(link.href).pathname.replace(/\/$/, '') === location.pathname.replace(/\/$/, '')) {
    link.classList.add('current'); link.setAttribute('aria-current', 'page');
  }
}
