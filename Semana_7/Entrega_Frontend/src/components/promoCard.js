import { escapeHtml, renderList } from '../lib/dom.js';
import { badgeToneClass } from '../data/promos.js';

const promoCard = (promo) => {
  const { title, description, price, compareAt, note, badge, badgeTone, image, alt } = promo;
  const secondary = compareAt
    ? `<span class="text-[13px] text-muted line-through">${escapeHtml(compareAt)}</span>`
    : `<span class="text-[13px] text-muted">${escapeHtml(note ?? '')}</span>`;

  return `
  <article class="reveal group card-surface">
    <div class="relative h-[168px] overflow-hidden">
      <img src="${image}" alt="${escapeHtml(alt)}" loading="lazy" decoding="async"
           class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
      <span class="badge-pill absolute top-3 left-3 ${badgeToneClass[badgeTone] ?? 'bg-doggis-red'}">
        ${escapeHtml(badge)}
      </span>
    </div>
    <div class="p-5">
      <h3 class="font-display text-[19px] leading-none">${escapeHtml(title)}</h3>
      <p class="mt-2 text-[13px] text-muted">${escapeHtml(description)}</p>
      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-baseline gap-2">
          <span class="text-[20px] font-bold text-doggis-red">${escapeHtml(price)}</span>
          ${secondary}
        </div>
        <button type="button"
                class="text-[12px] font-semibold text-ink transition-colors group-hover:text-doggis-red cursor-pointer">
          Pedir →
        </button>
      </div>
    </div>
  </article>`;
};

export const renderPromos = (promos) => renderList(promos, promoCard);
