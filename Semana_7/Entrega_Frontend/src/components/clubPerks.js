import { escapeHtml, renderList } from '../lib/dom.js';
import { iconCheck } from '../lib/icons.js';
import { clubPerks } from '../data/navigation.js';

export const renderClubPerks = () =>
  renderList(
    clubPerks,
    (perk) => `
      <li class="flex items-center gap-3 text-[14px] text-white/85">
        <span class="w-5 h-5 shrink-0 rounded-full bg-doggis-yellow flex items-center justify-center">
          ${iconCheck({ color: 'var(--color-ink)' })}
        </span>
        ${escapeHtml(perk)}
      </li>`,
  );
