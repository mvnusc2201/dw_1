/**
 * Local image assets. Files live in `public/img/` so the site is self-hosted.
 * Food photography is AI generated (seedream 4) to avoid using brand-owned
 * pictures; only the logo and the country flag remain as original assets.
 * Raw JPEG renders are converted to resized WebP by `npm run optimize:images`.
 */
const img = (file) => `/img/${file}`;

export const images = {
  logo: img('logo.webp'),
  flagChile: img('flag-chile.png'),
  hero: img('hero.webp'),
  hotDogs: img('hot-dogs.webp'),
  snacks: img('snacks.webp'),
  sharing: img('sharing.webp'),
  wraps: img('wraps.webp'),
  iceCream: img('ice-cream.webp'),
  chickenBurger: img('chicken-burger.webp'),
  pedidosYa: img('pedidosya.webp'),
  uberEats: img('uber-eats.webp'),
  rappi: img('rappi.webp'),
};
