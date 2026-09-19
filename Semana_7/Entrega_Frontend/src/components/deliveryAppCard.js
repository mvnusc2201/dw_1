import { escapeHtml, renderList } from '../lib/dom.js';

const deliveryAppCard = ({ name, image, href }) => `
  <a href="${href}" target="_blank" rel="noopener noreferrer"
     class="reveal block overflow-hidden rounded-md transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
    <img src="${image}" alt="Pide Doggis en ${escapeHtml(name)}" loading="lazy" decoding="async"
         class="w-full h-[290px] object-cover" />
  </a>`;

export const renderDeliveryApps = (apps) => renderList(apps, deliveryAppCard);
