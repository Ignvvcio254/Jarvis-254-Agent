# Gradient Mesh - Sistema de Fondos

> *"Los fondos que ves en Stripe, Linear, Vercel. Colores fluidos que respiran."*

## Referencia Visual

![Gradient Mesh Example](./images/gradient-mesh.webp)

---

## Qué es Gradient Mesh

**Gradient Mesh** (también llamado Mesh Gradient, Blur Gradient, o Aurora Background) es una técnica de fondos que combina múltiples gradientes radiales con blur para crear efectos de color fluidos y orgánicos.

### Dónde lo Ves

- **Stripe** - Hero sections con colores vibrantes
- **Linear** - Fondos oscuros con auroras
- **Vercel** - Gradientes sutiles
- **Tailwind CSS** - Background del hero
- **Apple** - Fondos de productos

### Características Clave

| Característica | Descripción |
|----------------|-------------|
| Múltiples gradientes | 2-5 radial-gradients superpuestos |
| Blur intenso | `filter: blur()` o blobs desenfocados |
| Colores RGBA | Transparencia para mezcla suave |
| Posicionamiento | Cada gradiente en diferente posición |
| Fluido/orgánico | Sin bordes duros, todo se funde |

---

## Las 3 Técnicas Principales

### 1. CSS Puro con Múltiples Radial-Gradients

La técnica más limpia y performante:

```css
.mesh-gradient {
  background:
    radial-gradient(at 40% 20%, rgba(255, 0, 128, 0.3) 0px, transparent 50%),
    radial-gradient(at 80% 0%, rgba(0, 128, 255, 0.3) 0px, transparent 50%),
    radial-gradient(at 0% 50%, rgba(128, 0, 255, 0.3) 0px, transparent 50%),
    radial-gradient(at 80% 50%, rgba(255, 128, 0, 0.3) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(0, 255, 128, 0.3) 0px, transparent 50%);
  background-color: #0f0f0f; /* Fondo base */
}
```

### 2. Div Blobs con Filter Blur

Elementos posicionados con blur extremo:

```html
<div class="relative overflow-hidden">
  <!-- Blob 1 -->
  <div class="absolute top-0 left-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-[128px] opacity-30"></div>

  <!-- Blob 2 -->
  <div class="absolute top-1/2 right-1/4 w-80 h-80 bg-pink-500 rounded-full filter blur-[128px] opacity-25"></div>

  <!-- Blob 3 -->
  <div class="absolute bottom-0 left-1/2 w-72 h-72 bg-blue-500 rounded-full filter blur-[128px] opacity-30"></div>

  <!-- Contenido -->
  <div class="relative z-10">
    <!-- Tu contenido aquí -->
  </div>
</div>
```

### 3. Imagen Pre-renderizada (Más Performante)

Para máximo rendimiento, usa una imagen:

```html
<div class="relative">
  <img
    src="/mesh-gradient.jpg"
    class="absolute inset-0 w-full h-full object-cover opacity-50"
    alt=""
  />
  <div class="relative z-10">
    <!-- Contenido -->
  </div>
</div>
```

---

## Implementación con Tailwind CSS

### Gradiente Simple (3 colores)

```html
<div class="
  min-h-screen
  bg-slate-950
  [background-image:radial-gradient(at_40%_20%,rgba(120,119,198,0.3)_0px,transparent_50%),radial-gradient(at_80%_0%,rgba(251,113,133,0.3)_0px,transparent_50%),radial-gradient(at_0%_50%,rgba(59,130,246,0.3)_0px,transparent_50%)]
">
```

### Gradiente Completo (5 colores)

```html
<div class="
  min-h-screen
  bg-gray-950
  [background-image:radial-gradient(at_40%_20%,rgba(120,119,198,0.3)_0px,transparent_50%),radial-gradient(at_80%_0%,rgba(251,113,133,0.3)_0px,transparent_50%),radial-gradient(at_0%_50%,rgba(59,130,246,0.3)_0px,transparent_50%),radial-gradient(at_80%_50%,rgba(168,85,247,0.3)_0px,transparent_50%),radial-gradient(at_0%_100%,rgba(20,184,166,0.3)_0px,transparent_50%)]
">
```

### Técnica de Blobs (Más Flexible)

```html
<div class="relative min-h-screen bg-slate-950 overflow-hidden">
  <!-- Blobs de gradiente -->
  <div class="absolute top-0 -left-40 w-[500px] h-[500px] bg-purple-500 rounded-full blur-[128px] opacity-20"></div>
  <div class="absolute top-0 -right-40 w-[400px] h-[400px] bg-pink-500 rounded-full blur-[128px] opacity-20"></div>
  <div class="absolute -bottom-20 left-1/2 w-[600px] h-[400px] bg-blue-500 rounded-full blur-[128px] opacity-20"></div>

  <!-- Contenido -->
  <div class="relative z-10">
    <!-- Tu contenido -->
  </div>
</div>
```

---

## Recetas Listas para Usar

### Hero Section Estilo Stripe

```html
<section class="relative min-h-screen overflow-hidden bg-slate-950">
  <!-- Mesh Gradient Background -->
  <div class="absolute inset-0">
    <div class="absolute top-20 left-1/4 w-[600px] h-[600px] bg-violet-600 rounded-full blur-[150px] opacity-20"></div>
    <div class="absolute top-40 right-1/4 w-[500px] h-[500px] bg-fuchsia-600 rounded-full blur-[150px] opacity-15"></div>
    <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyan-500 rounded-full blur-[150px] opacity-15"></div>
  </div>

  <!-- Grid Pattern Overlay (opcional) -->
  <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]"></div>

  <!-- Content -->
  <div class="relative z-10 max-w-6xl mx-auto px-8 py-32 text-center">
    <h1 class="text-5xl md:text-7xl font-bold text-white mb-6">
      Your Amazing Product
    </h1>
    <p class="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
      A beautiful description of what makes your product special.
    </p>
    <button class="bg-white text-gray-900 px-8 py-4 rounded-full font-semibold hover:bg-gray-100 transition-colors">
      Get Started
    </button>
  </div>
</section>
```

### Aurora Background (Estilo Linear)

```html
<div class="relative min-h-screen bg-black overflow-hidden">
  <!-- Aurora Effect -->
  <div class="absolute inset-0">
    <!-- Layer 1: Main aurora -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1/2 bg-gradient-to-b from-emerald-500/20 via-cyan-500/10 to-transparent blur-3xl"></div>

    <!-- Layer 2: Side glows -->
    <div class="absolute top-1/4 -left-20 w-96 h-96 bg-purple-500 rounded-full blur-[100px] opacity-20"></div>
    <div class="absolute top-1/4 -right-20 w-96 h-96 bg-blue-500 rounded-full blur-[100px] opacity-20"></div>
  </div>

  <!-- Noise Overlay (opcional) -->
  <div class="absolute inset-0 opacity-20" style="background-image: url('data:image/svg+xml,...');"></div>

  <!-- Content -->
  <div class="relative z-10">
    <!-- Tu contenido -->
  </div>
</div>
```

### Gradient Card Background

```html
<div class="
  relative
  p-8
  rounded-3xl
  bg-gray-900
  overflow-hidden
">
  <!-- Mini mesh gradient -->
  <div class="absolute top-0 right-0 w-64 h-64 bg-purple-500 rounded-full blur-[80px] opacity-20"></div>
  <div class="absolute bottom-0 left-0 w-48 h-48 bg-blue-500 rounded-full blur-[60px] opacity-20"></div>

  <!-- Content -->
  <div class="relative z-10">
    <h3 class="text-white text-2xl font-bold mb-4">Card Title</h3>
    <p class="text-gray-400">Card description goes here...</p>
  </div>
</div>
```

### Subtle Light Mode

```html
<div class="relative min-h-screen bg-white overflow-hidden">
  <!-- Light mesh gradient -->
  <div class="absolute top-0 left-1/4 w-[500px] h-[500px] bg-violet-200 rounded-full blur-[150px] opacity-60"></div>
  <div class="absolute top-1/2 right-1/4 w-[400px] h-[400px] bg-pink-200 rounded-full blur-[150px] opacity-50"></div>
  <div class="absolute bottom-0 left-1/2 w-[600px] h-[400px] bg-blue-200 rounded-full blur-[150px] opacity-50"></div>

  <!-- Content -->
  <div class="relative z-10">
    <!-- Contenido con texto oscuro -->
  </div>
</div>
```

### Footer con Gradient

```html
<footer class="relative bg-gray-950 pt-32 pb-16 overflow-hidden">
  <!-- Top glow -->
  <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full h-48 bg-gradient-to-b from-purple-500/10 to-transparent"></div>

  <!-- Mesh blobs -->
  <div class="absolute bottom-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full blur-[120px] opacity-10"></div>
  <div class="absolute bottom-0 right-1/4 w-80 h-80 bg-purple-500 rounded-full blur-[100px] opacity-10"></div>

  <!-- Content -->
  <div class="relative z-10 max-w-6xl mx-auto px-8">
    <!-- Footer content -->
  </div>
</footer>
```

### CTA Section

```html
<section class="relative py-32 overflow-hidden">
  <!-- Gradient background -->
  <div class="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600"></div>

  <!-- Mesh overlay -->
  <div class="absolute top-0 left-0 w-96 h-96 bg-white rounded-full blur-[100px] opacity-20"></div>
  <div class="absolute bottom-0 right-0 w-80 h-80 bg-yellow-300 rounded-full blur-[100px] opacity-20"></div>

  <!-- Content -->
  <div class="relative z-10 max-w-4xl mx-auto px-8 text-center">
    <h2 class="text-4xl font-bold text-white mb-6">Ready to Get Started?</h2>
    <p class="text-white/80 text-lg mb-10">Join thousands of happy customers today.</p>
    <button class="bg-white text-purple-600 px-10 py-4 rounded-full font-bold hover:bg-gray-100 transition-colors">
      Start Free Trial
    </button>
  </div>
</section>
```

---

## Paletas de Color Recomendadas

### Cyberpunk/Tech (Stripe style)

```html
<!-- Blobs -->
bg-purple-500   /* #A855F7 */
bg-pink-500     /* #EC4899 */
bg-cyan-500     /* #06B6D4 */
bg-blue-500     /* #3B82F6 */

<!-- Base -->
bg-slate-950    /* #020617 */
bg-gray-950     /* #030712 */
```

### Aurora/Northern Lights (Linear style)

```html
<!-- Blobs -->
bg-emerald-500  /* #10B981 */
bg-teal-500     /* #14B8A6 */
bg-cyan-500     /* #06B6D4 */
bg-blue-500     /* #3B82F6 */

<!-- Base -->
bg-black        /* #000000 */
```

### Sunset/Warm

```html
<!-- Blobs -->
bg-orange-500   /* #F97316 */
bg-rose-500     /* #F43F5E */
bg-purple-500   /* #A855F7 */
bg-yellow-400   /* #FACC15 */

<!-- Base -->
bg-slate-900    /* #0F172A */
```

### Minimal/Subtle (Light mode)

```html
<!-- Blobs -->
bg-violet-200   /* #DDD6FE */
bg-pink-200     /* #FBCFE8 */
bg-blue-200     /* #BFDBFE */
bg-indigo-200   /* #C7D2FE */

<!-- Base -->
bg-white        /* #FFFFFF */
bg-gray-50      /* #F9FAFB */
```

---

## Valores de Blur Recomendados

| Intensidad | Tailwind | Uso |
|------------|----------|-----|
| Sutil | `blur-[60px]` | Cards, elementos pequeños |
| Medio | `blur-[100px]` | Secciones medianas |
| Intenso | `blur-[128px]` | Hero sections |
| Extremo | `blur-[150px]` | Fondos full-page |
| Máximo | `blur-[200px]` | Efecto muy difuso |

---

## Configuración Tailwind (Opcional)

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      backgroundImage: {
        // Mesh gradients predefinidos
        'mesh-1': `
          radial-gradient(at 40% 20%, rgba(120,119,198,0.3) 0px, transparent 50%),
          radial-gradient(at 80% 0%, rgba(251,113,133,0.3) 0px, transparent 50%),
          radial-gradient(at 0% 50%, rgba(59,130,246,0.3) 0px, transparent 50%)
        `,
        'mesh-2': `
          radial-gradient(at 0% 0%, rgba(168,85,247,0.4) 0px, transparent 50%),
          radial-gradient(at 100% 0%, rgba(236,72,153,0.3) 0px, transparent 50%),
          radial-gradient(at 50% 100%, rgba(6,182,212,0.3) 0px, transparent 50%)
        `,
        'mesh-aurora': `
          radial-gradient(ellipse at top, rgba(16,185,129,0.2) 0%, transparent 50%),
          radial-gradient(at 0% 50%, rgba(59,130,246,0.2) 0%, transparent 50%),
          radial-gradient(at 100% 50%, rgba(168,85,247,0.2) 0%, transparent 50%)
        `,
      },
    },
  },
}
```

```html
<!-- Uso -->
<div class="min-h-screen bg-slate-950 bg-mesh-1">
<div class="min-h-screen bg-black bg-mesh-aurora">
```

---

## Overlays Complementarios

### Grid Pattern

```html
<!-- Sobre el mesh gradient -->
<div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]"></div>
```

### Dot Pattern

```html
<div class="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:20px_20px]"></div>
```

### Noise Texture (requiere imagen)

```html
<div class="absolute inset-0 opacity-[0.015]" style="background-image: url('/noise.png');"></div>
```

### Vignette

```html
<div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.4)_100%)]"></div>
```

---

## Performance Tips

### DO (Hacer)

1. **Usar `overflow-hidden`** - Evita scroll horizontal por blobs fuera del viewport
2. **Limitar blobs a 3-5** - Más impacta rendimiento
3. **Preferir CSS puro** - Más performante que divs con blur
4. **Usar imágenes pre-renderizadas** - Para fondos estáticos complejos
5. **`will-change: transform`** - Si animas los blobs

### DON'T (No Hacer)

1. **No usar demasiados blobs** - Afecta rendimiento
2. **No animar `filter: blur()`** - Es muy costoso
3. **No olvidar `z-index`** - El contenido debe estar encima
4. **No usar en elementos pequeños** - Blur pesado en divs pequeños = desperdicio

---

## Animaciones (Opcionales)

### Blob Flotante

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      animation: {
        'blob': 'blob 7s infinite',
      },
      keyframes: {
        blob: {
          '0%': { transform: 'translate(0px, 0px) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
          '100%': { transform: 'translate(0px, 0px) scale(1)' },
        },
      },
    },
  },
}
```

```html
<div class="absolute animate-blob bg-purple-500 rounded-full blur-[128px] opacity-20"></div>
<div class="absolute animate-blob animation-delay-2000 bg-pink-500 rounded-full blur-[128px] opacity-20"></div>
<div class="absolute animate-blob animation-delay-4000 bg-blue-500 rounded-full blur-[128px] opacity-20"></div>
```

**Nota:** `animation-delay` requiere CSS adicional:

```css
.animation-delay-2000 { animation-delay: 2s; }
.animation-delay-4000 { animation-delay: 4s; }
```

---

## Generadores Útiles

- [Hypercolor Mesh Generator](https://hypercolor.dev/mesh/) - Tailwind CSS colors
- [MagicPattern Blurry Gradients](https://www.magicpattern.design/blurry-gradients) - Export PNG/JPG
- [Colorffy Mesh Generator](https://colorffy.com/mesh-gradient-generator) - CSS export
- [fffuel ffflux](https://www.fffuel.co/ffflux/) - SVG fluid gradients
- [CSS Gradient](https://cssgradient.io/) - Gradientes básicos

---

## Referencias

- [LogRocket - Gradients with Tailwind CSS](https://blog.logrocket.com/guide-adding-gradients-tailwind-css/)
- [Tailwind CSS Docs - Background Image](https://tailwindcss.com/docs/background-image)
- [MDN - radial-gradient()](https://developer.mozilla.org/en-US/docs/Web/CSS/gradient/radial-gradient)
- [CSS-Tricks - CSS Gradients](https://css-tricks.com/css3-gradients/)
- [MagicPattern - Blurry Gradients](https://www.magicpattern.design/blog/add-blurry-gradient-to-your-html-code)

---

*Este documento es parte del Design System de SaaS Factory V2.*
