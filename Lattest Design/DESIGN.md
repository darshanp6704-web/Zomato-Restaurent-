---
name: Culinary Intelligence System
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#e0c0b1'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#a78b7d'
  outline-variant: '#584237'
  surface-tint: '#ffb690'
  primary: '#ffb690'
  on-primary: '#552100'
  primary-container: '#f97316'
  on-primary-container: '#582200'
  inverse-primary: '#9d4300'
  secondary: '#ffb3ad'
  on-secondary: '#68000a'
  secondary-container: '#a40217'
  on-secondary-container: '#ffaea8'
  tertiary: '#c0c1ff'
  on-tertiary: '#1000a9'
  tertiary-container: '#8c8fff'
  on-tertiary-container: '#1304ac'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb690'
  on-primary-fixed: '#341100'
  on-primary-fixed-variant: '#783200'
  secondary-fixed: '#ffdad7'
  secondary-fixed-dim: '#ffb3ad'
  on-secondary-fixed: '#410004'
  on-secondary-fixed-variant: '#930013'
  tertiary-fixed: '#e1e0ff'
  tertiary-fixed-dim: '#c0c1ff'
  on-tertiary-fixed: '#07006c'
  on-tertiary-fixed-variant: '#2f2ebe'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding-mobile: 16px
  container-padding-desktop: 32px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system is engineered for a premium AI-driven gastronomic experience. It targets discerning food enthusiasts who value speed, curation, and high-end aesthetics. The brand personality is sophisticated yet approachable, blending the precision of artificial intelligence with the warmth of culinary passion.

The visual direction utilizes **Glassmorphism** to create a sense of depth and atmospheric perspective. By layering semi-transparent surfaces over deep, tonal gradients, the UI achieves a "high-tech lounge" aesthetic. This approach minimizes visual noise, allowing vibrant food imagery and AI-generated insights to take center stage. The emotional response should be one of effortless discovery and modern luxury.

## Colors
The color palette is anchored in a **Deep Charcoal and Slate** foundation, designed to provide maximum contrast for the glass effects. The primary brand expression is a **Gastronomy Gradient** (Orange to Red), representing heat, spice, and energy.

- **Backgrounds:** Use a linear gradient from #0F172A at the top to #1E293B at the bottom to maintain vertical rhythm.
- **Glass Surfaces:** All containers must use the defined semi-transparent charcoal with a 12px backdrop-blur and a subtle 1px translucent border.
- **Accents:** Use the primary orange for interactive states and AI-driven highlights.
- **Typography Colors:** Primary text stays at #F8FAFC for readability, while secondary information uses #94A3B8 to maintain hierarchy.

## Typography
This design system utilizes **Outfit**, a modern geometric sans-serif, across all touchpoints. Its open counters and clean geometry align with the AI-driven nature of the product.

- **Scale:** A tight typographic scale is used to maintain a clean, app-like feel.
- **Headlines:** Use Bold and SemiBold weights for clear information architecture. Display type should always use negative letter-spacing to appear more compact and premium.
- **Labels:** Use Medium and SemiBold weights for buttons and badges to ensure they stand out against glass surfaces.
- **Mobile Optimization:** Large display titles should scale down by approximately 15-20% on mobile devices to prevent excessive wrapping.

## Layout & Spacing
The layout follows a **fluid grid** model with a base unit of 4px. This ensures all elements align to a consistent rhythmic scale.

- **Mobile:** 4-column grid with 16px margins and 16px gutters.
- **Desktop:** 12-column centered grid with a maximum content width of 1280px. 
- **AI Feed:** Content should utilize an asymmetrical stack where AI recommendations occupy larger card spans (e.g., 2 columns on mobile, 8 columns on desktop) compared to standard list items.
- **Vertical Rhythm:** Use the `stack-md` (16px) for related items and `stack-lg` (32px) for distinct section breaks.

## Elevation & Depth
Elevation in this design system is conveyed through **Z-index layering and blur intensity** rather than traditional black shadows.

- **Level 1 (Base):** The background gradient.
- **Level 2 (Cards):** Glassmorphic surfaces with 12px blur. These are the primary containers for content.
- **Level 3 (Overlays/Modals):** Increased backdrop blur (24px) and a slightly lighter surface opacity (0.8) to indicate foreground priority.
- **Glow Effects:** Interactive elements like active sliders or primary buttons use a soft, colored outer glow (`box-shadow: 0 0 20px rgba(249, 115, 22, 0.3)`) to simulate a light source emitting from within the "glass."

## Shapes
The shape language is consistently **Rounded**. This softens the "technical" feel of the AI and makes the UI feel more organic and culinary-friendly.

- **Cards & Modals:** Use `rounded-lg` (1rem / 16px) for primary containers.
- **Buttons & Selectors:** Use `rounded-xl` (1.5rem / 24px) or full pill shapes to indicate interactivity.
- **Input Fields:** Match the button roundedness for a cohesive form language.
- **Selection Indicators:** Small dots or active state pills should always be fully rounded.

## Components
- **Glassmorphic Cards:** The core unit. Must feature a 1px border (`rgba(255, 255, 255, 0.08)`), backdrop-filter: blur(12px), and a subtle inner shadow to define the edge.
- **Glowing Sliders:** Track should be a muted slate; the thumb and active track should carry the Primary Orange gradient with a 10px outer glow.
- **Pill Selectors:** Used for budget ($, $$, $$$) and cuisine tags. Unselected: transparent border. Selected: Primary gradient background with white text.
- **Star-Rated Badges:** Floating glass pills with a gold-tinted star icon and SemiBold text.
- **Shimmering Skeletons:** Use a linear-gradient animation across slate-colored blocks (`#1E293B`) to simulate loading. The shimmer should be a subtle white sweep at 10% opacity.
- **AI Insight Chips:** Specialized chips with a secondary purple-to-blue gradient border to distinguish AI-generated suggestions from standard metadata.
- **Primary Buttons:** High-contrast gradient fills (Orange to Red) with white text. Apply a subtle 15% white overlay on hover to simulate the "lighting up" of the glass.