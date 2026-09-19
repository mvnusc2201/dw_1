/**
 * Scroll reveal for every `.reveal` element.
 * Mirrors the design's GSAP ScrollTrigger behaviour (start: "top 88%", once)
 * using an IntersectionObserver so no animation library is needed.
 */

const REVEAL_STEP_MS = 90;
const MAX_STAGGER_STEPS = 4;

export function initReveal(root = document) {
  const targets = Array.from(root.querySelectorAll('.reveal'));
  if (!targets.length) return;

  if (!('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  // Stagger siblings inside the same parent for a softer cascade.
  const seen = new Map();
  targets.forEach((el) => {
    const parent = el.parentElement;
    const index = seen.get(parent) ?? 0;
    seen.set(parent, index + 1);
    const step = Math.min(index, MAX_STAGGER_STEPS);
    el.style.setProperty('--reveal-delay', `${step * REVEAL_STEP_MS}ms`);
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -12% 0px', threshold: 0.05 },
  );

  targets.forEach((el) => observer.observe(el));
}
