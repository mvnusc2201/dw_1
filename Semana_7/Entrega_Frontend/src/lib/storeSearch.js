/**
 * Client side filtering for the store locator.
 * Filters the rendered store cards by name / address / comuna.
 */

export function initStoreSearch({
  formSelector = '#storeSearchForm',
  inputSelector = '#storeSearchInput',
  listSelector = '#storeList',
  emptySelector = '#storeEmptyState',
} = {}) {
  const form = document.querySelector(formSelector);
  const input = document.querySelector(inputSelector);
  const list = document.querySelector(listSelector);
  const emptyState = document.querySelector(emptySelector);

  if (!form || !input || !list) return;

  const cards = Array.from(list.querySelectorAll('[data-store-card]'));

  const applyFilter = () => {
    const query = input.value.trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const matches = !query || (card.dataset.search ?? '').includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });

    if (emptyState) emptyState.hidden = visible > 0;
  };

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    applyFilter();
  });

  input.addEventListener('input', applyFilter);
  applyFilter();
}
