/** Store locator results. `status` maps to a badge tone. */
export const stores = [
  {
    id: 'costanera-center',
    name: 'Doggis Costanera Center',
    address: 'Av. Andrés Bello 2447, Providencia · Nivel -1',
    comuna: 'Providencia',
    hours: 'Hoy 10:00 – 22:00',
    status: 'open',
  },
  {
    id: 'mall-plaza-vespucio',
    name: 'Doggis Mall Plaza Vespucio',
    address: 'Froilán Roa 7205, La Florida · Patio de comidas',
    comuna: 'La Florida',
    hours: 'Hoy 10:30 – 21:30',
    status: 'open',
  },
  {
    id: 'vina-centro',
    name: 'Doggis Viña Centro',
    address: 'Av. 15 Norte 961, Viña del Mar · Local 118',
    comuna: 'Viña del Mar',
    hours: 'Hoy 11:00 – 20:00',
    status: 'closing-soon',
  },
];

export const storeStatus = {
  open: { label: 'Abierto', className: 'bg-status-open-bg text-status-open-fg' },
  'closing-soon': { label: 'Cierra pronto', className: 'bg-status-soon-bg text-status-soon-fg' },
};
