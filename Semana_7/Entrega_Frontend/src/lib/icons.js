/**
 * Inline SVG icon set used across the page.
 * Every icon is a function so stroke/fill colours and size can be overridden
 * at the call site (monochrome icons always receive an explicit colour).
 */

const stroke = (paths, { size = 20, color = 'currentColor', width = 1.8 }) => `
  <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none"
       stroke="${color}" stroke-width="${width}" stroke-linecap="round"
       stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;

const filled = (paths, { size = 18, color = 'currentColor' }) => `
  <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" aria-hidden="true">${paths}</svg>`;

export const iconMenu = (o = {}) =>
  stroke('<path d="M4 7h16M4 12h16M4 17h16" />', { size: 18, width: 2.4, ...o });

export const iconCart = (o = {}) =>
  stroke(
    `<path d="M6 2 4 6v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6l-2-4z" />
     <path d="M4 6h16" /><path d="M16 10a4 4 0 0 1-8 0" />`,
    { size: 20, ...o },
  );

export const iconLogin = (o = {}) =>
  stroke(
    `<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
     <path d="M10 17l5-5-5-5" /><path d="M15 12H3" />`,
    { size: 20, ...o },
  );

export const iconPin = (o = {}) =>
  stroke(
    `<path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0Z" />
     <circle cx="12" cy="10" r="3" />`,
    { size: 18, width: 1.9, ...o },
  );

export const iconCheck = (o = {}) =>
  stroke('<path d="M20 6 9 17l-5-5" />', { size: 12, width: 3.2, ...o });

export const iconInstagram = ({ size = 17, color = 'currentColor' } = {}) => `
  <svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none"
       stroke="${color}" stroke-width="1.9" aria-hidden="true">
    <rect x="3" y="3" width="18" height="18" rx="5" />
    <circle cx="12" cy="12" r="4" />
    <circle cx="17.2" cy="6.8" r="1.1" fill="${color}" stroke="none" />
  </svg>`;

export const iconFacebook = (o = {}) =>
  filled(
    '<path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h2.5l.5-3H13v-2c0-.6.4-1 1-1Z" />',
    { size: 17, ...o },
  );

export const iconTiktok = (o = {}) =>
  filled(
    '<path d="M16 3h-3v11.2a2.6 2.6 0 1 1-2.2-2.57V8.4A5.9 5.9 0 1 0 16.3 14.2V9.6A6 6 0 0 0 20 10.8V7.6A3.7 3.7 0 0 1 16 3Z" />',
    { size: 17, ...o },
  );

export const iconWhatsapp = (o = {}) =>
  filled(
    `<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l4.9-1.3A10 10 0 1 0 12 2Zm5.1 14.1c-.2.6-1.2 1.2-1.7 1.2-.5.1-1 .1-1.7-.1-1-.3-2.4-1-3.7-2.4-1-1.1-1.7-2.4-1.9-3.1-.2-.7-.1-1.3.1-1.7.2-.4.7-.8 1-.9.2-.1.6-.1.8.3l.7 1.3c.1.2.1.4 0 .6l-.4.6c-.1.2-.1.3 0 .5.3.5.7 1 1.2 1.4.5.4 1 .7 1.4.9.2.1.4 0 .5-.1l.5-.6c.2-.2.4-.2.6-.1l1.3.7c.4.2.4.6.3.8Z" />`,
    { size: 19, ...o },
  );

export const iconApple = (o = {}) =>
  filled(
    `<path d="M16.365 1.43c0 1.14-.42 2.2-1.12 2.99-.85.96-2.24 1.7-3.37 1.61-.13-1.1.43-2.24 1.12-3 .8-.87 2.18-1.53 3.37-1.6ZM20.8 17.1c-.55 1.27-.82 1.83-1.53 2.95-.98 1.56-2.37 3.5-4.09 3.51-1.53.02-1.93-1-4-.99-2.07.01-2.5 1.01-4.04.99-1.72-.02-3.03-1.77-4.01-3.33C-1.6 15.9-.9 9.62 2.26 8.06c1.5-.75 2.9-.6 3.9-.58 1.26.03 2.44.62 3.32.62.87 0 2.36-.76 3.94-.62 2.02.18 3.4 1.3 4.14 2.7-2.4 1.45-2.9 4.8-1.75 6.92Z" />`,
    { size: 20, ...o },
  );

export const iconGooglePlay = (o = {}) =>
  filled(
    `<path d="M3.6 1.8a1.7 1.7 0 0 0-.5 1.2v18a1.7 1.7 0 0 0 .5 1.2l9.3-10.2L3.6 1.8Zm11 8.1 3-3.1L5.9 1.2l8.7 8.7Zm0 4.2-8.7 8.7 11.7-5.6-3-3.1Zm5.8-3.2-2.4-1.3-3.2 3.3 3.2 3.3 2.4-1.3c1.2-.7 1.2-2.6 0-4Z" />`,
    { size: 20, ...o },
  );

/** Map of social network id -> icon renderer, used by footer + floating rail. */
export const socialIcons = {
  instagram: iconInstagram,
  facebook: iconFacebook,
  tiktok: iconTiktok,
  whatsapp: iconWhatsapp,
};
