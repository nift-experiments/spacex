/* Recovered observable navigation and responsive media; no framework runtime. */
const header = document.querySelector('#spacex-header');
const toggle = header.querySelector('.header-button');
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  header.classList.toggle('menu-open', open);
  header.querySelector('nav').classList.toggle('black-overlay', open);
});
const submenuTriggers = [...header.querySelectorAll('.sub-menu-header')];
const backdrop = header.querySelector('.menu-backdrop');
const setSubmenu = (trigger, open) => {
  trigger.setAttribute('aria-expanded', String(open));
  trigger.parentElement.classList.toggle('submenu-open', open);
  trigger.parentElement.querySelector('.sub-menu').classList.toggle('open', open);
  trigger.querySelector('.down-arrow-icon').classList.toggle('open', open);
  backdrop.classList.toggle('open', submenuTriggers.some(item => item.getAttribute('aria-expanded') === 'true'));
};
for (const trigger of submenuTriggers) {
  const change = () => setSubmenu(trigger, trigger.getAttribute('aria-expanded') !== 'true');
  trigger.addEventListener('click', change);
  trigger.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); change(); }
  });
  trigger.parentElement.addEventListener('mouseenter', () => {
    if (matchMedia('(min-width:1280px)').matches) setSubmenu(trigger, true);
  });
  trigger.parentElement.addEventListener('mouseleave', () => {
    if (matchMedia('(min-width:1280px)').matches) setSubmenu(trigger, false);
  });
}
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const expanded = submenuTriggers.find(item => item.getAttribute('aria-expanded') === 'true');
  submenuTriggers.forEach(item => setSubmenu(item, false));
  if (toggle.getAttribute('aria-expanded') === 'true') { toggle.click(); toggle.focus(); }
  else expanded?.focus();
});
// Frozen mobile variants are maintained assets, selected without service requests.
const mediaBreakpoint = matchMedia('(max-width:961px)');
function selectMobileMedia(root = document) {
  for (const element of root.querySelectorAll('img[data-mobile],video[data-mobile]')) {
    const source = element.tagName === 'VIDEO' ? (element.querySelector('source') || element) : element;
    element.dataset.desktop ??= source.getAttribute('src');
    const target = mediaBreakpoint.matches ? element.dataset.mobile : element.dataset.desktop;
    if (source.getAttribute('src') === target) continue;
    source.setAttribute('src', target);
    if (element.tagName === 'VIDEO') element.load();
  }
}
mediaBreakpoint.addEventListener('change', () => selectMobileMedia());
selectMobileMedia();

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
  // Delivered swiperControlsAtBottom adds the public bottom-padding class.
  carousel.classList.toggle('bottom-padding', carousel.nextElementSibling?.classList.contains('bottom-swiper-controls') === true);
  const wrapper = carousel.querySelector(':scope > .swiper-wrapper');
  const slides = Array.from(wrapper.children);
  const family = carousel.closest('[data-sx-host]');
  const previous = family?.querySelector('.swiper-previous') || family?.querySelector('.swiper-controls button:first-child');
  const next = family?.querySelector('.swiper-next') || family?.querySelector('.swiper-controls button:nth-child(2)');
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
    carousel.querySelectorAll('[data-carousel-index]').forEach(button => {
      const active = Number(button.dataset.carouselIndex) === index;
      button.classList.toggle('swiper-pagination-bullet-active',active); button.setAttribute('aria-current',String(active));
    });
    const caption = family?.querySelector('.caption');
    if (caption && slides[index].dataset.caption !== undefined) caption.textContent = slides[index].dataset.caption;
    if (previous) { previous.disabled = index === 0; previous.setAttribute('aria-label', 'Previous slide'); }
    if (next) { next.disabled = index === slides.length - 1; next.setAttribute('aria-label', 'Next slide'); }
  };
  wrapper.style.transition = 'transform 300ms ease';
  previous?.addEventListener('click', () => show(index - 1));
  next?.addEventListener('click', () => show(index + 1));
  for (const button of carousel.querySelectorAll('[data-carousel-index]')) {
    button.addEventListener('click', () => show(Number(button.dataset.carouselIndex)));
    button.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); show(Number(button.dataset.carouselIndex)); } });
  }
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

// Public homepage changes its text alignment at the mobile breakpoint.
const homepageBreakpoint = matchMedia('(max-width:961px)');
const alignHomepage = () => {
  for (const block of document.querySelectorAll('[data-desktop-alignment]')) {
    block.classList.remove(block.dataset.desktopAlignment, 'inner-left-bottom');
    block.classList.add(homepageBreakpoint.matches ? 'inner-left-bottom' : block.dataset.desktopAlignment);
  }
};
homepageBreakpoint.addEventListener('change', alignHomepage);
alignHomepage();

// Public Sites reveal behavior, including maintained component replacements.
const revealFamilies = [
  ['.sx-reveal', 'sx-reveal--in', '0px 0px -12% 0px', 0.12],
  ['.la-year', 'la-year--in', '0px 0px -8% 0px', 0.45],
].map(([selector, className, rootMargin, threshold]) => ({
  selector, className,
  observer: new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add(className);
      entry.target.dataset.nativeRevealObserved = 'complete';
      revealFamilies.find(family => family.className === className).observer.unobserve(entry.target);
    }
  }, {root: null, rootMargin, threshold}),
}));
const observeReveals = (root = document) => {
  for (const {selector, className, observer} of revealFamilies) {
    const elements = [...root.querySelectorAll(selector)];
    if (root.matches?.(selector)) elements.unshift(root);
    for (const element of elements) {
      if (element.dataset.nativeRevealObserved) continue;
      if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
        element.classList.add(className);
        element.dataset.nativeRevealObserved = 'complete';
      } else {
        element.classList.remove(className);
        element.dataset.nativeRevealObserved = 'pending';
        observer.observe(element);
      }
    }
  }
};
observeReveals();

// Public header onScroll: reveal upward/below 50px/or while mobile navigation is expanded.
let currentPageYOffset = 0;
window.addEventListener('scroll', () => {
  const offset = window.pageYOffset;
  const visible = offset < currentPageYOffset || offset < 50 || toggle.getAttribute('aria-expanded') === 'true';
  header.classList.toggle('header-hide', !visible);
  currentPageYOffset = offset;
}, {passive:true});
