import { escapeHtml, renderList } from '../lib/dom.js';
import { storeStatus } from '../data/stores.js';

const storeCard = (store) => {
  const status = storeStatus[store.status] ?? storeStatus.open;
  const haystack = `${store.name} ${store.address} ${store.comuna}`.toLowerCase();

  return `
  <article class="reveal bg-white rounded-xl border border-line p-5 transition-all duration-300 hover:border-doggis-yellow hover:shadow-md"
           data-store-card data-search="${escapeHtml(haystack)}">
    <div class="flex items-start justify-between gap-3">
      <h3 class="text-[16px] font-semibold">${escapeHtml(store.name)}</h3>
      <span class="shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold ${status.className}">
        ${status.label}
      </span>
    </div>
    <p class="mt-2 text-[13px] text-muted">${escapeHtml(store.address)}</p>
    <p class="mt-3 text-[12px] font-semibold text-ink">${escapeHtml(store.hours)}</p>
    <div class="mt-4 flex gap-4 text-[12px] font-semibold">
      <a href="#" class="text-doggis-red hover:underline">Pedir aquí</a>
      <a href="#" class="text-ink hover:underline">Cómo llegar</a>
    </div>
  </article>`;
};

export const renderStores = (stores) => renderList(stores, storeCard);
