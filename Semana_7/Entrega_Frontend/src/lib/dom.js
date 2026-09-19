/** Tiny DOM helpers shared by the render modules. */

/** Escapes text that is injected into markup templates. */
export const escapeHtml = (value = '') =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

/**
 * Renders an HTML string into the element matching `selector`.
 * Returns the container (or null when the mount point is missing).
 */
export const mount = (selector, html) => {
  const host = document.querySelector(selector);
  if (!host) {
    console.warn(`[doggis] mount point not found: ${selector}`);
    return null;
  }
  host.innerHTML = html;
  return host;
};

/** Joins a list through a render function. */
export const renderList = (items, renderItem) => items.map(renderItem).join('');
