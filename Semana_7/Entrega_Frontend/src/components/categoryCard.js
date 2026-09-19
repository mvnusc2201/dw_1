import { escapeHtml, renderList } from '../lib/dom.js';

const categoryCard = ({ title, image, alt, href = '#' }) => `
  <a href="${href}" class="reveal group block">
    <h3 class="text-[19px] font-medium mb-3 transition-colors group-hover:text-doggis-red">
      ${escapeHtml(title)}
    </h3>
    <div class="overflow-hidden rounded-sm bg-line">
      <img src="${image}" alt="${escapeHtml(alt)}" loading="lazy" decoding="async"
           class="w-full h-[210px] object-cover transition-transform duration-500 group-hover:scale-[1.06]" />
    </div>
  </a>`;

export const renderCategories = (categories) => renderList(categories, categoryCard);
