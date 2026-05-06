# Bento Grid - Sistema de Layout

> *"El arte japonés del orden: cada elemento en su lugar perfecto."*

## Referencia Visual

![Bento Grid Example](./images/bento-grid.png)

---

## Qué es Bento Grid

**Bento Grid** es un sistema de layout inspirado en las cajas bento japonesas. Cada elemento ocupa su propio compartimento en una cuadrícula organizada y visualmente armónica.

### Origen

- Popularizado por **Apple** en sus presentaciones de productos
- Evolucionó del Metro Design de Windows 8
- Perfecto para mostrar features, specs, o contenido variado

### Características Clave

| Característica | Descripción |
|----------------|-------------|
| Cuadrícula modular | Elementos en celdas definidas |
| Tamaños variados | Celdas de 1x1, 2x1, 1x2, 2x2, etc. |
| Espaciado uniforme | Gap consistente entre elementos |
| Responsive | Se reorganiza en diferentes breakpoints |
| Contenido mixto | Texto, imágenes, iconos, stats |

### Cuándo Usar

- Landing pages de productos (features section)
- Dashboards con métricas
- Portfolios creativos
- Páginas "About" con facts
- Showcases de características

---

## CSS Grid: El Fundamento

Bento Grid se construye principalmente con **CSS Grid**:

```css
/* CSS Vanilla */
.bento-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 200px;
  gap: 1rem;
}

.bento-item-wide {
  grid-column: span 2;
}

.bento-item-tall {
  grid-row: span 2;
}

.bento-item-large {
  grid-column: span 2;
  grid-row: span 2;
}
```

---

## Implementación con Tailwind CSS

### Contenedor Base

```html
<!-- Móvil: 1 col | Tablet: 4 cols | Desktop: 6 cols -->
<div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
  <!-- Items -->
</div>
```

### Clases de Grid Principales

| Clase | Descripción |
|-------|-------------|
| `grid` | Activa display: grid |
| `grid-cols-1` | 1 columna |
| `grid-cols-2` | 2 columnas |
| `grid-cols-3` | 3 columnas |
| `grid-cols-4` | 4 columnas |
| `grid-cols-6` | 6 columnas |
| `gap-4` | Espaciado de 1rem |
| `gap-6` | Espaciado de 1.5rem |

### Clases de Spanning

| Clase | Efecto |
|-------|--------|
| `col-span-1` | Ocupa 1 columna |
| `col-span-2` | Ocupa 2 columnas |
| `col-span-3` | Ocupa 3 columnas |
| `col-span-full` | Ocupa todas las columnas |
| `row-span-1` | Ocupa 1 fila |
| `row-span-2` | Ocupa 2 filas |
| `row-span-3` | Ocupa 3 filas |

### Altura de Filas

```html
<!-- Altura fija -->
<div class="grid auto-rows-[200px] grid-cols-3 gap-4">

<!-- Altura mínima -->
<div class="grid auto-rows-[minmax(200px,auto)] grid-cols-3 gap-4">

<!-- Con Tailwind arbitrary values -->
<div class="grid auto-rows-[192px] grid-cols-3 gap-4">
```

---

## Recetas Listas para Usar

### Layout Básico 3x3

```html
<div class="grid grid-cols-3 auto-rows-[200px] gap-4">
  <!-- Item grande (2x2) -->
  <div class="col-span-2 row-span-2 bg-blue-500 rounded-2xl p-6">
    <h3 class="text-white text-2xl font-bold">Feature Principal</h3>
  </div>

  <!-- Items normales (1x1) -->
  <div class="bg-gray-100 rounded-2xl p-6">Item 2</div>
  <div class="bg-gray-100 rounded-2xl p-6">Item 3</div>

  <!-- Item ancho (2x1) -->
  <div class="col-span-2 bg-yellow-400 rounded-2xl p-6">Item Ancho</div>

  <!-- Item normal -->
  <div class="bg-gray-100 rounded-2xl p-6">Item 5</div>
</div>
```

### Layout Responsivo Completo

```html
<div class="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-4">
  <!-- Hero (2x2 en md, 3x2 en lg) -->
  <div class="md:col-span-2 md:row-span-2 lg:col-span-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl p-8">
    <h2 class="text-white text-3xl font-bold mb-4">Main Feature</h2>
    <p class="text-white/80">Description of the main feature goes here.</p>
  </div>

  <!-- Stats (1x1) -->
  <div class="bg-white border border-gray-200 rounded-2xl p-6 flex flex-col justify-center">
    <span class="text-4xl font-bold text-gray-900">99%</span>
    <span class="text-gray-500">Uptime</span>
  </div>

  <!-- Tall item (1x2) -->
  <div class="md:row-span-2 bg-gray-900 text-white rounded-2xl p-6">
    <h3 class="font-bold text-xl mb-4">Security</h3>
    <ul class="space-y-2 text-gray-300">
      <li>• End-to-end encryption</li>
      <li>• SOC 2 compliant</li>
      <li>• GDPR ready</li>
    </ul>
  </div>

  <!-- Wide item (2x1) -->
  <div class="md:col-span-2 bg-emerald-500 rounded-2xl p-6 flex items-center gap-4">
    <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
      <span class="text-2xl">⚡</span>
    </div>
    <div class="text-white">
      <h3 class="font-bold">Lightning Fast</h3>
      <p class="text-white/70">Built for speed</p>
    </div>
  </div>

  <!-- Regular items -->
  <div class="bg-amber-100 rounded-2xl p-6">
    <span class="text-3xl">🎨</span>
    <h3 class="font-bold mt-2">Design</h3>
  </div>

  <div class="lg:col-span-2 bg-blue-100 rounded-2xl p-6">
    <span class="text-3xl">🔗</span>
    <h3 class="font-bold mt-2">Integrations</h3>
    <p class="text-gray-600 text-sm mt-1">Connect with 100+ apps</p>
  </div>

  <!-- Full width footer -->
  <div class="col-span-full bg-gray-50 rounded-2xl p-6 text-center">
    <p class="text-gray-500">And many more features...</p>
  </div>
</div>
```

### Features Grid (Estilo Apple)

```html
<section class="py-20 px-8 bg-white">
  <div class="max-w-6xl mx-auto">
    <h2 class="text-4xl font-bold text-center mb-12">Why Choose Us</h2>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Feature Card Large -->
      <div class="lg:col-span-2 lg:row-span-2 bg-gradient-to-br from-blue-600 to-blue-800 rounded-3xl p-10 text-white">
        <div class="h-full flex flex-col justify-between">
          <div>
            <span class="inline-block bg-white/20 rounded-full px-4 py-1 text-sm mb-6">New</span>
            <h3 class="text-3xl font-bold mb-4">AI-Powered Analytics</h3>
            <p class="text-blue-100 text-lg max-w-md">
              Get insights automatically with our machine learning engine.
            </p>
          </div>
          <div class="mt-8">
            <img src="/analytics-preview.png" alt="Analytics" class="rounded-2xl shadow-2xl" />
          </div>
        </div>
      </div>

      <!-- Stat Card -->
      <div class="bg-gray-50 rounded-3xl p-8 flex flex-col justify-center items-center text-center">
        <span class="text-5xl font-bold text-gray-900">50M+</span>
        <span class="text-gray-500 mt-2">Users worldwide</span>
      </div>

      <!-- Icon Feature -->
      <div class="bg-amber-50 rounded-3xl p-8">
        <div class="w-14 h-14 bg-amber-500 rounded-2xl flex items-center justify-center mb-6">
          <span class="text-2xl">🔒</span>
        </div>
        <h3 class="text-xl font-bold mb-2">Enterprise Security</h3>
        <p class="text-gray-600">Bank-level encryption for your data.</p>
      </div>

      <!-- Simple Feature -->
      <div class="bg-emerald-50 rounded-3xl p-8">
        <div class="w-14 h-14 bg-emerald-500 rounded-2xl flex items-center justify-center mb-6">
          <span class="text-2xl">⚡</span>
        </div>
        <h3 class="text-xl font-bold mb-2">Real-time Sync</h3>
        <p class="text-gray-600">Changes sync instantly across devices.</p>
      </div>

      <!-- Wide Feature -->
      <div class="md:col-span-2 lg:col-span-1 bg-purple-50 rounded-3xl p-8">
        <div class="w-14 h-14 bg-purple-500 rounded-2xl flex items-center justify-center mb-6">
          <span class="text-2xl">🌐</span>
        </div>
        <h3 class="text-xl font-bold mb-2">Global CDN</h3>
        <p class="text-gray-600">Content delivered from 200+ edge locations.</p>
      </div>
    </div>
  </div>
</section>
```

### Dashboard Stats Grid

```html
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <!-- Main Stat (2x2) -->
  <div class="col-span-2 row-span-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 text-white">
    <h3 class="text-lg font-medium mb-2 opacity-80">Total Revenue</h3>
    <span class="text-5xl font-bold">$124,500</span>
    <div class="mt-4 flex items-center gap-2 text-emerald-300">
      <span>↑ 12.5%</span>
      <span class="opacity-60">vs last month</span>
    </div>
  </div>

  <!-- Small Stats -->
  <div class="bg-white border border-gray-200 rounded-2xl p-6">
    <h3 class="text-gray-500 text-sm">Users</h3>
    <span class="text-2xl font-bold">8,420</span>
  </div>

  <div class="bg-white border border-gray-200 rounded-2xl p-6">
    <h3 class="text-gray-500 text-sm">Sessions</h3>
    <span class="text-2xl font-bold">24.1K</span>
  </div>

  <div class="bg-white border border-gray-200 rounded-2xl p-6">
    <h3 class="text-gray-500 text-sm">Bounce Rate</h3>
    <span class="text-2xl font-bold">32%</span>
  </div>

  <div class="bg-white border border-gray-200 rounded-2xl p-6">
    <h3 class="text-gray-500 text-sm">Conversions</h3>
    <span class="text-2xl font-bold">4.2%</span>
  </div>
</div>
```

### Portfolio/Gallery Grid

```html
<div class="grid grid-cols-2 md:grid-cols-4 auto-rows-[250px] gap-4">
  <!-- Large image -->
  <div class="col-span-2 row-span-2 relative overflow-hidden rounded-2xl group">
    <img src="/project1.jpg" class="w-full h-full object-cover transition-transform group-hover:scale-105" />
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-6">
      <div class="text-white">
        <h3 class="font-bold text-xl">Project Name</h3>
        <p class="text-white/70">Brand Identity</p>
      </div>
    </div>
  </div>

  <!-- Regular images -->
  <div class="relative overflow-hidden rounded-2xl group">
    <img src="/project2.jpg" class="w-full h-full object-cover transition-transform group-hover:scale-105" />
  </div>

  <div class="relative overflow-hidden rounded-2xl group">
    <img src="/project3.jpg" class="w-full h-full object-cover transition-transform group-hover:scale-105" />
  </div>

  <!-- Wide image -->
  <div class="col-span-2 relative overflow-hidden rounded-2xl group">
    <img src="/project4.jpg" class="w-full h-full object-cover transition-transform group-hover:scale-105" />
  </div>
</div>
```

### Pricing Bento

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <!-- Basic -->
  <div class="bg-white border border-gray-200 rounded-3xl p-8">
    <h3 class="font-bold text-xl mb-2">Basic</h3>
    <p class="text-gray-500 mb-6">For individuals</p>
    <div class="mb-6">
      <span class="text-4xl font-bold">$9</span>
      <span class="text-gray-500">/month</span>
    </div>
    <ul class="space-y-3 text-gray-600 mb-8">
      <li class="flex items-center gap-2">
        <span class="text-emerald-500">✓</span> 5 projects
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-500">✓</span> Basic analytics
      </li>
    </ul>
    <button class="w-full py-3 border-2 border-gray-900 rounded-xl font-bold hover:bg-gray-900 hover:text-white transition-colors">
      Get Started
    </button>
  </div>

  <!-- Pro (Featured - Larger) -->
  <div class="md:row-span-2 bg-gray-900 text-white rounded-3xl p-8 flex flex-col">
    <span class="inline-block bg-amber-500 text-black px-3 py-1 rounded-full text-sm font-bold mb-4 w-fit">Popular</span>
    <h3 class="font-bold text-2xl mb-2">Pro</h3>
    <p class="text-gray-400 mb-6">For teams</p>
    <div class="mb-6">
      <span class="text-5xl font-bold">$29</span>
      <span class="text-gray-400">/month</span>
    </div>
    <ul class="space-y-3 text-gray-300 mb-8 flex-grow">
      <li class="flex items-center gap-2">
        <span class="text-emerald-400">✓</span> Unlimited projects
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-400">✓</span> Advanced analytics
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-400">✓</span> Priority support
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-400">✓</span> Custom domains
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-400">✓</span> Team collaboration
      </li>
    </ul>
    <button class="w-full py-4 bg-white text-gray-900 rounded-xl font-bold hover:bg-gray-100 transition-colors">
      Start Free Trial
    </button>
  </div>

  <!-- Enterprise -->
  <div class="bg-white border border-gray-200 rounded-3xl p-8">
    <h3 class="font-bold text-xl mb-2">Enterprise</h3>
    <p class="text-gray-500 mb-6">For large orgs</p>
    <div class="mb-6">
      <span class="text-4xl font-bold">Custom</span>
    </div>
    <ul class="space-y-3 text-gray-600 mb-8">
      <li class="flex items-center gap-2">
        <span class="text-emerald-500">✓</span> Everything in Pro
      </li>
      <li class="flex items-center gap-2">
        <span class="text-emerald-500">✓</span> Dedicated support
      </li>
    </ul>
    <button class="w-full py-3 border-2 border-gray-900 rounded-xl font-bold hover:bg-gray-900 hover:text-white transition-colors">
      Contact Sales
    </button>
  </div>
</div>
```

---

## Patrones Comunes de Spanning

### Patrón 1: Hero + Grid

```
┌─────────┬───┐
│         │   │
│   2x2   │1x1│
│         ├───┤
├───┬───┬─┤1x1│
│1x1│1x1│ 1x1 │
└───┴───┴─────┘
```

```html
<div class="grid grid-cols-3 auto-rows-[150px] gap-4">
  <div class="col-span-2 row-span-2">Hero</div>
  <div>Item</div>
  <div>Item</div>
  <div>Item</div>
  <div>Item</div>
  <div>Item</div>
</div>
```

### Patrón 2: Masonry Style

```
┌───┬───────┬───┐
│   │       │   │
│1x2│  2x2  │1x1│
│   │       ├───┤
├───┤       │1x1│
│1x1│       │   │
└───┴───────┴───┘
```

```html
<div class="grid grid-cols-4 auto-rows-[120px] gap-4">
  <div class="row-span-2">Tall</div>
  <div class="col-span-2 row-span-2">Large</div>
  <div>Small</div>
  <div>Small</div>
  <div>Small</div>
</div>
```

### Patrón 3: Dashboard

```
┌─────────────────┐
│      3x1        │
├───┬───┬───┬───┬─┤
│1x1│1x1│1x1│1x1│ │
├───┴───┴───┴───┴─┤
│      2x1        │
└─────────────────┘
```

---

## Alternativas a CSS Grid

### CSS Columns (Masonry-like)

```html
<div class="columns-1 md:columns-2 lg:columns-3 gap-4">
  <div class="mb-4 break-inside-avoid bg-gray-100 rounded-2xl p-6">
    <!-- Contenido de altura variable -->
  </div>
  <div class="mb-4 break-inside-avoid bg-gray-100 rounded-2xl p-6">
    <!-- Contenido de altura variable -->
  </div>
  <!-- Más items... -->
</div>
```

**Clases clave:**
- `columns-X` - Número de columnas
- `break-inside-avoid` - Evita que un elemento se divida
- `mb-4` - Margen inferior (reemplaza gap)

### Flexbox (Columnas verticales)

```html
<div class="flex gap-4">
  <!-- Columna 1 -->
  <div class="flex-1 space-y-4">
    <div class="h-48 bg-gray-100 rounded-2xl"></div>
    <div class="h-32 bg-gray-100 rounded-2xl"></div>
  </div>

  <!-- Columna 2 -->
  <div class="flex-1 space-y-4">
    <div class="h-32 bg-gray-100 rounded-2xl"></div>
    <div class="h-48 bg-gray-100 rounded-2xl"></div>
  </div>

  <!-- Columna 3 -->
  <div class="flex-1 space-y-4">
    <div class="h-64 bg-gray-100 rounded-2xl"></div>
  </div>
</div>
```

---

## Mejores Prácticas

### DO (Hacer)

1. **Máximo 9 elementos** - Evita sobrecargar visualmente
2. **Jerarquía clara** - El item más grande = más importante
3. **Contenido variado** - Mezcla texto, iconos, imágenes, stats
4. **Gap consistente** - Usa `gap-4` o `gap-6`, no mezcles
5. **Responsive** - Siempre planea el colapso en móvil
6. **Esquinas redondeadas** - `rounded-2xl` o `rounded-3xl` para suavidad
7. **Contraste** - Un item colorido entre items neutros

### DON'T (No Hacer)

1. **No sobrepoblar** - Más de 9 items confunde
2. **No todos iguales** - Sin variación es aburrido
3. **No ignorar móvil** - Planea `grid-cols-1` para mobile
4. **No mezclar gaps** - Mantén consistencia
5. **No olvidar altura** - Define `auto-rows` o alturas fijas

---

## Responsividad

### Estrategia de Breakpoints

```html
<div class="
  grid
  grid-cols-1          /* Mobile: 1 columna */
  sm:grid-cols-2       /* Small: 2 columnas */
  md:grid-cols-3       /* Medium: 3 columnas */
  lg:grid-cols-4       /* Large: 4 columnas */
  xl:grid-cols-6       /* XL: 6 columnas */
  gap-4
">
```

### Spanning Responsivo

```html
<!-- Grande en desktop, normal en mobile -->
<div class="col-span-1 md:col-span-2 lg:col-span-3">
  Responsive item
</div>

<!-- Alto solo en desktop -->
<div class="row-span-1 lg:row-span-2">
  Conditionally tall
</div>
```

---

## Estilos de Cards para Bento

### Minimal

```html
<div class="bg-gray-50 rounded-2xl p-6">
```

### Con Borde

```html
<div class="bg-white border border-gray-200 rounded-2xl p-6">
```

### Con Sombra

```html
<div class="bg-white rounded-2xl p-6 shadow-lg">
```

### Gradiente

```html
<div class="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-6 text-white">
```

### Glassmorphism

```html
<div class="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-6">
```

### Neobrutalism

```html
<div class="bg-yellow-300 border-4 border-black shadow-[6px_6px_0_#000] rounded-xl p-6">
```

---

## Referencias

- [Tailwind CSS Bento Grids](https://tailwindcss.com/plus/ui-blocks/marketing/sections/bento-grids)
- [DEV.to - Creating Bento Grid Layouts](https://dev.to/ibelick/creating-bento-grid-layouts-with-css-tailwind-css-26mo)
- [Lexington Themes - Bento Grid Tutorial](https://lexingtonthemes.com/tutorials/how-to-create-a-bento-grid-with-tailwind-css/)
- [BentoGrids.com](https://bentogrids.com/) - Inspiración
- [ibelick - Bento Grid Layouts](https://ibelick.com/blog/create-bento-grid-layouts)

---

*Este documento es parte del Design System de SaaS Factory V2.*
