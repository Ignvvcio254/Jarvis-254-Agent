---
name: Emil Design Engineering
description: UI polish, animation physics, micro-interactions and design engineering principles by Emil Kowalski
---

I'm ready to help you build interfaces that feel right. My knowledge comes from Emil Kowalski's design engineering philosophy.

## Animation Principles

**Frequency determines animation necessity:**
- Frequent actions (100+ times daily): no animation
- Occasional interactions (modals, drawers): standard animation
- Rare events (onboarding): can include delight

**Easing matters tremendously.** Never use built-in CSS easings — they lack punch. Use custom curves via [easing.dev](https://easing.dev/). Never use `ease-in` for UI — it delays initial movement, making interfaces feel sluggish exactly when users watch most closely.

**Speed under 300ms feels snappier.** A 180ms dropdown outperforms a 400ms one perceptually.

**Purpose-driven motion.** Every animation must answer "why animate this?" Valid reasons: spatial consistency, state indication, feedback, preventing jarring transitions. "Looks cool" alone is not sufficient.

## Component Patterns

- **Buttons:** Add `transform: scale(0.97)` on `:active` for immediate feedback
- **Popovers:** Scale from trigger location, not center (modals stay centered)
- **Tooltips:** Skip animation on subsequent hovers after the first opens
- **Entries:** Never animate from `scale(0)` — start at `scale(0.95)` with opacity
- **Toasts:** Use transitions (interruptible) rather than keyframes (restart from zero)

## Performance Rules

Only animate `transform` and `opacity` — these skip layout/paint phases and run on GPU. Avoid animating dimensions or spacing properties.

CSS animations run off-thread and stay smooth during heavy loads. Framer Motion's shorthand (`x`, `y`) uses the main thread; use full `transform` strings for hardware acceleration.

## Spring Physics

Springs feel natural because they mimic physical forces. Key parameters:
- **stiffness**: how quickly it snaps (higher = faster)
- **damping**: how quickly oscillation stops (lower = bouncier)
- **mass**: inertia (higher = sluggish start, overshoot)

For UI interactions: `stiffness: 400, damping: 30` is a good starting point.

## Accessibility

Respect `prefers-reduced-motion` by removing movement-based animations while keeping opacity/color transitions:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Gate hover states behind `@media (hover: hover) and (pointer: fine)` to prevent false positives on touch devices.

## Taste

Taste develops through practice — not innate. Cultivate it by studying excellent work, understanding *why* things feel good, and iterating relentlessly. Invisible details create compound value: most refinements go unnoticed consciously, yet collectively produce experiences people love without articulating why.
