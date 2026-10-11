/* Native controller for the bounded public video-tile overlay/inline contract. */
for (const tile of document.querySelectorAll('video-tile')) {
  const trigger = tile.querySelector('.play-arrow');
  const overlay = tile.querySelector('.overlay,.inline');
  if (!trigger || !overlay) continue;
  const closeButton = overlay.querySelector('close-svg');
  const video = overlay.querySelector('video');
  const frame = overlay.querySelector('iframe');
  const frameSource = frame?.getAttribute('src');
  const poster = tile.querySelector('.responsive-image');
  const placeholder = overlay.querySelector('.poster-image-placeholder');
  let lastFocus;
  trigger.setAttribute('role','button');trigger.tabIndex=0;
  trigger.setAttribute('aria-label','Play '+(tile.querySelector('h2')?.textContent.trim() || 'video'));
  overlay.setAttribute('aria-hidden','true');
  if (closeButton) {closeButton.setAttribute('role','button');closeButton.tabIndex=0;closeButton.setAttribute('aria-label','Close video');}
  const close=()=>{
    overlay.classList.remove('open');overlay.classList.add('close');overlay.setAttribute('aria-hidden','true');
    poster?.classList.remove('hide');placeholder?.classList.remove('hide');video?.pause();
    if(frame)frame.src='about:blank';
    document.body.classList.remove('media-overlay-open');lastFocus?.focus();
  };
  const open=()=>{
    lastFocus=document.activeElement;overlay.classList.remove('close');overlay.classList.add('open');overlay.setAttribute('aria-hidden','false');
    if(overlay.classList.contains('inline')) {poster?.classList.add('hide');placeholder?.classList.add('hide');}
    else document.body.classList.add('media-overlay-open');
    if(frame && frameSource)frame.src=frameSource;
    if(video){video.controls=true;video.play().catch(close);}
    (closeButton || video)?.focus();
  };
  trigger.addEventListener('click',open);
  trigger.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open();}});
  closeButton?.addEventListener('click',close);
  closeButton?.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();close();}});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&overlay.classList.contains('open'))close();});
}
