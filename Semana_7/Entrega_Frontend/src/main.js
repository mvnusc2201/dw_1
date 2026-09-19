import './style.css';

import { images } from './data/images.js';
import { categories } from './data/categories.js';
import { promos } from './data/promos.js';
import { deliveryApps } from './data/deliveryApps.js';
import { stores } from './data/stores.js';

import { mount } from './lib/dom.js';
import {
  iconApple,
  iconCart,
  iconGooglePlay,
  iconLogin,
  iconMenu,
  iconPin,
} from './lib/icons.js';
import { initReveal } from './lib/reveal.js';
import { initHeroParallax } from './lib/heroParallax.js';
import { initStoreSearch } from './lib/storeSearch.js';

import { renderCategories } from './components/categoryCard.js';
import { renderPromos } from './components/promoCard.js';
import { renderDeliveryApps } from './components/deliveryAppCard.js';
import { renderStores } from './components/storeCard.js';
import { renderClubPerks } from './components/clubPerks.js';
import {
  renderFooterColumns,
  renderFooterSocials,
  renderSocialRail,
} from './components/footer.js';

/** Applies the local image sources declared in data/images.js. */
const applyImages = () => {
  const map = {
    '#logoImg': images.logo,
    '#footerLogoImg': images.logo,
    '#flagImg': images.flagChile,
    '#heroImg': images.hero,
    '#clubPreviewImg': images.chickenBurger,
  };

  Object.entries(map).forEach(([selector, src]) => {
    const el = document.querySelector(selector);
    if (el) el.src = src;
  });
};

/** Injects the inline SVG icons used by static markup. */
const applyIcons = () => {
  const map = {
    '#iconMenu': iconMenu({ color: 'var(--color-doggis-red)' }),
    '#iconCart': iconCart({ color: 'var(--color-ink)' }),
    '#iconLogin': iconLogin(),
    '#iconSearchPin': iconPin({ color: 'var(--color-muted)' }),
    '#iconAppStore': iconApple({ color: 'var(--color-ink)' }),
    '#iconGooglePlay': iconGooglePlay({ color: 'var(--color-ink)' }),
  };

  Object.entries(map).forEach(([selector, svg]) => {
    const el = document.querySelector(selector);
    if (el) el.innerHTML = svg;
  });
};

const renderPage = () => {
  applyImages();
  applyIcons();

  mount('#categoryGrid', renderCategories(categories));
  mount('#promoGrid', renderPromos(promos));
  mount('#deliveryAppGrid', renderDeliveryApps(deliveryApps));
  mount('#storeList', renderStores(stores));
  mount('#clubPerksList', renderClubPerks());
  mount('#footerColumns', renderFooterColumns());
  mount('#footerSocials', renderFooterSocials());
  mount('#socialRail', renderSocialRail());
};

renderPage();
initStoreSearch();
initReveal();
initHeroParallax();
