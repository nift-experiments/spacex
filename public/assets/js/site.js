/* Recovered observable navigation and responsive media; no framework runtime. */
const header = document.querySelector('#spacex-header');
const toggle = header.querySelector('.header-button');
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  header.classList.toggle('menu-open', open);
  document.body.classList.toggle('menu-open', open);
});
for (const trigger of header.querySelectorAll('.sub-menu-header')) {
  const change = () => {
    const open = trigger.getAttribute('aria-expanded') !== 'true';
    trigger.setAttribute('aria-expanded', String(open));
    trigger.parentElement.classList.toggle('submenu-open', open);
  };
  trigger.addEventListener('click', change);
  trigger.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); change(); }
  });
}
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
    toggle.click(); toggle.focus();
  }
});
if (matchMedia('(max-width:961px)').matches) {
  for (const video of document.querySelectorAll('video[data-mobile]')) {
    video.querySelector('source').src = video.dataset.mobile;
    video.load();
  }
}

// Public CMS statistics are maintained build inputs, not runtime API requests.
const counters = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    counters.unobserve(entry.target);
    const target = Number(entry.target.dataset.countTarget);
    const duration = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 1500;
    let start;
    const tick = now => {
      start ??= now;
      const progress = duration ? Math.min((now - start) / duration, 1) : 1;
      entry.target.textContent = String(Math.round(target * progress));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
});
for (const counter of document.querySelectorAll('[data-count-target]')) {
  counter.textContent = '0';
  counters.observe(counter);
}

// Native carousel boundary; no Angular or Swiper runtime is retained.
for (const carousel of document.querySelectorAll('.sx-carousel')) {
  const wrapper = carousel.querySelector(':scope > .swiper-wrapper');
  const slides = Array.from(wrapper.children);
  const family = carousel.closest('[data-sx-host]');
  const previous = family?.querySelector('.swiper-previous');
  const next = family?.querySelector('.swiper-next');
  let index = 0;
  const gap = Number(carousel.dataset.carouselGap) || 0;
  carousel.style.setProperty('--sx-carousel-gap', gap + 'px');
  const show = nextIndex => {
    index = Math.max(0, Math.min(slides.length - 1, nextIndex));
    wrapper.style.transform = `translateX(${-index * (carousel.clientWidth + gap)}px)`;
    slides.forEach((slide, position) => {
      slide.classList.toggle('swiper-slide-active', position === index);
      slide.setAttribute('aria-hidden', String(position !== index));
      slide.inert = position !== index;
    });
    if (previous) { previous.disabled = index === 0; previous.setAttribute('aria-label', 'Previous slide'); }
    if (next) { next.disabled = index === slides.length - 1; next.setAttribute('aria-label', 'Next slide'); }
  };
  wrapper.style.transition = 'transform 300ms ease';
  previous?.addEventListener('click', () => show(index - 1));
  next?.addEventListener('click', () => show(index + 1));
  carousel.tabIndex = 0;
  carousel.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  let startX;
  carousel.addEventListener('pointerdown', event => { startX = event.clientX; });
  carousel.addEventListener('pointerup', event => {
    if (startX !== undefined && Math.abs(event.clientX - startX) > 50) show(index + (event.clientX < startX ? 1 : -1));
    startX = undefined;
  });
  new ResizeObserver(() => show(index)).observe(carousel);
  show(0);
}
