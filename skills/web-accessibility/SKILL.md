---
name: Web Accessibility (A11y / WCAG)
description: Audit and enforce WCAG 2.1 AA compliance — semantic HTML, ARIA, contrast, keyboard navigation, screen readers
---

Audit and enforce web accessibility standards. Target: **WCAG 2.1 Level AA** as the minimum bar for all production UI.

## Quick Audit Checklist

Run this against every component before shipping:

- [ ] All images have `alt` text (decorative: `alt=""`)
- [ ] Color contrast ≥ 4.5:1 for text, ≥ 3:1 for UI components
- [ ] All interactive elements reachable via `Tab` key
- [ ] Focus indicator visible (never `outline: none` without replacement)
- [ ] Form inputs have associated `<label>` or `aria-label`
- [ ] Errors identified with text (not just color)
- [ ] Page has a descriptive `<title>`
- [ ] Headings (`h1`→`h6`) form a logical hierarchy
- [ ] No keyboard traps
- [ ] `prefers-reduced-motion` respected

## Semantic HTML (always prefer over ARIA)

```html
<!-- WRONG -->
<div onClick={handler} className="button">Click me</div>

<!-- RIGHT -->
<button onClick={handler}>Click me</button>

<!-- WRONG -->
<div className="nav">...</div>

<!-- RIGHT -->
<nav aria-label="Main navigation">...</nav>

<!-- Landmark roles -->
<header>, <nav>, <main>, <aside>, <footer>, <section>, <article>
```

## ARIA Patterns

```html
<!-- Buttons with icons only -->
<button aria-label="Close dialog">
  <XIcon aria-hidden="true" />
</button>

<!-- Live regions (dynamic content) -->
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

<!-- Modal dialog -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">Title</h2>
  <p id="dialog-desc">Description</p>
</div>

<!-- Expandable -->
<button aria-expanded={isOpen} aria-controls="menu-id">
  Menu
</button>
<ul id="menu-id" hidden={!isOpen}>...</ul>

<!-- Progress -->
<div role="progressbar" aria-valuenow={50} aria-valuemin={0} aria-valuemax={100}>
  50%
</div>
```

## Focus Management

```tsx
// Trap focus inside modal
import { useEffect, useRef } from 'react';

function Modal({ isOpen, onClose }) {
  const firstFocusRef = useRef(null);

  useEffect(() => {
    if (isOpen) firstFocusRef.current?.focus();
  }, [isOpen]);

  return (
    <div role="dialog" aria-modal="true">
      <button ref={firstFocusRef}>First focusable</button>
      <button onClick={onClose}>Close</button>
    </div>
  );
}

// Return focus to trigger on close
const triggerRef = useRef(null);
useEffect(() => {
  if (!isOpen) triggerRef.current?.focus();
}, [isOpen]);
```

## Keyboard Navigation

| Key | Expected behavior |
|-----|------------------|
| `Tab` | Move to next interactive element |
| `Shift+Tab` | Move to previous |
| `Enter`/`Space` | Activate button/link |
| `Escape` | Close modal/menu/popover |
| `Arrow keys` | Navigate within widgets (menus, tabs, sliders) |
| `Home`/`End` | First/last item in list |

## Color Contrast Requirements

- **Normal text** (< 18pt or < 14pt bold): 4.5:1 minimum
- **Large text** (≥ 18pt or ≥ 14pt bold): 3:1 minimum
- **UI components** (borders, icons): 3:1 minimum
- **Disabled elements**: exempt

Check with: https://webaim.org/resources/contrastchecker/

## Touch Target Sizes

Minimum: **44×44 CSS pixels** (WCAG 2.5.5 AAA)
Minimum with spacing: **24×24 CSS pixels** (WCAG 2.5.8 AA)

```css
/* Ensure minimum tap target */
button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}
```

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```tsx
// In React
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const duration = prefersReduced ? 0 : 300;
```

## Form Accessibility

```tsx
// Always associate labels
<label htmlFor="email">Email address</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? 'email-error' : undefined}
/>
{hasError && (
  <span id="email-error" role="alert">
    Please enter a valid email address
  </span>
)}
```

## Automated Testing (Playwright + axe-core)

```tsx
import { checkA11y } from 'axe-playwright';

test('component is accessible', async ({ page }) => {
  await page.goto('/component');
  await checkA11y(page, '#root', {
    detailedReport: true,
    detailedReportOptions: { html: true },
  });
});
```

## WCAG 2.1 AA — Minimum Required Criteria

**Perceivable:** 1.1.1, 1.2.1-5, 1.3.1-5, 1.4.1-4, 1.4.10-13
**Operable:** 2.1.1-2, 2.2.1-2, 2.3.1, 2.4.1-7, 2.4.11, 2.5.1-4, 2.5.8
**Understandable:** 3.1.1-2, 3.2.1-4, 3.3.1-4, 3.3.8
**Robust:** 4.1.1-3
