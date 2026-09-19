import { escapeHtml, renderList } from '../lib/dom.js';
import { socialIcons } from '../lib/icons.js';
import { footerColumns, footerSocials, railSocials } from '../data/navigation.js';

const footerLink = (link) =>
  link.static
    ? `<li class="leading-snug">${escapeHtml(link.label)}</li>`
    : `<li><a href="${link.href}" class="footer-link">${escapeHtml(link.label)}</a></li>`;

const footerColumn = (column) => `
  <div>
    <h4 class="text-[15px] font-semibold text-doggis-red">${escapeHtml(column.title)}</h4>
    <ul class="mt-4 space-y-2 text-[13px] text-doggis-red">
      ${renderList(column.links, footerLink)}
    </ul>
  </div>`;

export const renderFooterColumns = () => renderList(footerColumns, footerColumn);

export const renderFooterSocials = () =>
  renderList(
    footerSocials,
    ({ id, label, href }) => `
      <a href="${href}" aria-label="${escapeHtml(label)}" class="social-bubble">
        ${socialIcons[id]({ color: 'var(--color-doggis-red)' })}
      </a>`,
  );

export const renderSocialRail = () =>
  renderList(
    railSocials,
    ({ id, label, href, className }) => `
      <a href="${href}" aria-label="${escapeHtml(label)}" class="social-rail-bubble ${className}">
        ${socialIcons[id]({ color: '#fff', size: 18 })}
      </a>`,
  );
