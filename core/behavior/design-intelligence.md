# Design Intelligence Protocol — Visual Generation

This protocol governs how the Jarvis Framework translates abstract visual blueprints into production-grade Sass/SCSS code.

## 🎨 The Design-to-Code Pipeline

1. **Reference Selection**: The agent identifies the target visual style from `design-systems/` (e.g., `liquid-glass.md`).
2. **Blueprint Analysis**: The agent reads the technical definitions:
   - **Color Palettes**: Exact hex/rgba values.
   - **Blur/Shadows**: Specific pixel values and spread.
   - **Transitions**: Timing functions and durations.
   - **Layout Patterns**: Grid/Flex logic.
3. **SCSS Architecture**: The agent implements the styles using a modular approach:
   - **Variables**: Define tokens based on the blueprint.
   - **Mixins**: Create reusable style blocks for complex effects (e.g., `@mixin glass-effect`).
   - **Components**: Apply styles to specific UI elements.
4. **Validation**: The agent verifies the output against the blueprint's "Golden Rules" to ensure visual fidelity.

---

## 🛠️ Styling Standards

### 1. Variable-First Approach
Never hardcode colors or spacing. Use a design token system:
```scss
$color-glass-bg: rgba(255, 255, 255, 0.1);
$glass-blur: 12px;
$glass-border: 1px solid rgba(255, 255, 255, 0.2);
```

### 2. Glassmorphism Implementation
When using the `liquid-glass` system, always ensure the following stack:
- `backdrop-filter: blur($glass-blur);`
- `background: $color-glass-bg;`
- `border: $glass-border;`
- `box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);`

### 3. Neumorphism Implementation
When using the `neumorphism` system, implement dual shadows:
- **Raised**: `box-shadow: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff;`
- **Inset**: `box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;`

---

## 🚀 Operational Commands

When a user requests a design, the agent should:
1. Read the corresponding `.md` file in `design-systems/`.
2. Propose a **Design Token Map** first.
3. Generate the `.scss` file using the modular architecture defined above.
