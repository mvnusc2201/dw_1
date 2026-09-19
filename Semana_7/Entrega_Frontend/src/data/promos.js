import { images } from './images.js';

/** "¡Promos del mes!" cards. `badgeTone` maps to a background token. */
export const promos = [
  {
    id: 'doggonazo-2x1',
    title: 'SÚPER DOGGONAZO 2x1',
    description: 'Todos los martes, pide uno y llévate dos. Solo con retiro en tienda.',
    price: '$5.990',
    compareAt: '$9.990',
    badge: '2x1',
    badgeTone: 'red',
    image: images.hotDogs,
    alt: 'Promoción Doggonazo 2x1',
  },
  {
    id: 'snackbox-mesa',
    title: 'SNACKBOX PARA LA MESA',
    description: 'Papas, doggis y bebidas para cuatro. Ideal para compartir... o no.',
    price: '$14.490',
    compareAt: '$20.690',
    badge: '-30%',
    badgeTone: 'ink',
    image: images.sharing,
    alt: 'Snackbox familiar Doggis',
  },
  {
    id: 'huracan-regalo',
    title: 'HURACÁN DE REGALO',
    description: 'En compras sobre $12.000 te apañamos con un Huracón mediano.',
    price: '$0',
    note: 'con tu pedido',
    badge: 'Gratis',
    badgeTone: 'coral',
    image: images.iceCream,
    alt: 'Huracán de regalo Doggis',
  },
];

export const badgeToneClass = {
  red: 'bg-doggis-red',
  ink: 'bg-ink',
  coral: 'bg-doggis-coral',
};
