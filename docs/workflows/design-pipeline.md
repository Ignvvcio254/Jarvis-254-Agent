# 🎨 Visual Design Pipeline

Jarvis converts abstract design goals into production-ready code using a **Blueprint-to-Implementation** pipeline.

## 🚀 The Workflow

### Step 1: Blueprint Selection
The user specifies a style (e.g., "I want a Liquid Glass landing page"). The agent accesses the `design-systems/` folder and reads the `liquid-glass.md` blueprint.

### Step 2: Token Mapping
The agent extracts the "Visual Truths" from the blueprint:
- **Blur**: 12px
- **Opacity**: 10%
- **Border**: 1px semi-transparent white
- **Shadow**: Soft, deep blur

### Step 3: SCSS Generation
The agent generates a modular SCSS structure:
1. **Tokens**: Defines the extracted values as variables.
2. **Mixins**: Creates a `.glass-effect()` mixin.
3. **Application**: Applies the mixin to the requested components.

## 📐 Available Design Systems

- **Liquid Glass**: Modern, translucent, airy.
- **Neumorphism**: Soft, tactile, extruded.
- **Neobrutalism**: High contrast, bold borders, vibrant.
- **Bento Grid**: Modular, organized, Apple-inspired.
- **Gradient Mesh**: Fluid, organic, high-end.

## 💡 Best Practices
- **Don't Hardcode**: Always use the variables defined in the token map.
- **Layering**: Use `backdrop-filter` for glass effects to ensure they interact with the background.
- **Consistency**: Stick to one design system per project to maintain visual harmony.
