/**
 * Hero parallax: scales the hero image from 1 -> 1.08 while the hero scrolls
 * out of the viewport. Uses rAF-throttled scroll handling for performance.
 */

const MAX_SCALE = 1.08;

export function initHeroParallax(selector = '#heroImg') {
  const image = document.querySelector(selector);
  if (!image) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const hero = image.closest('section') ?? image.parentElement;
  let frame = null;

  const update = () => {
    frame = null;
    const { height } = hero.getBoundingClientRect();
    const scrolled = Math.min(Math.max(window.scrollY / height, 0), 1);
    image.style.transform = `scale(${1 + (MAX_SCALE - 1) * scrolled})`;
  };

  const onScroll = () => {
    if (frame !== null) return;
    frame = window.requestAnimationFrame(update);
  };

  update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
}
