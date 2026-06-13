---
name: Civic Intelligence
colors:
  surface: '#f9f9fc'
  surface-dim: '#dadadc'
  surface-bright: '#f9f9fc'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f6'
  surface-container: '#eeeef0'
  surface-container-high: '#e8e8ea'
  surface-container-highest: '#e2e2e5'
  on-surface: '#1a1c1e'
  on-surface-variant: '#40484b'
  inverse-surface: '#2f3133'
  inverse-on-surface: '#f0f0f3'
  outline: '#70787c'
  outline-variant: '#bfc8cb'
  surface-tint: '#216678'
  primary: '#003c49'
  on-primary: '#ffffff'
  primary-container: '#005566'
  on-primary-container: '#89c8dc'
  inverse-primary: '#91d0e4'
  secondary: '#586061'
  on-secondary: '#ffffff'
  secondary-container: '#dae1e3'
  on-secondary-container: '#5d6466'
  tertiary: '#562c02'
  on-tertiary: '#ffffff'
  tertiary-container: '#714217'
  on-tertiary-container: '#f3b17c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b0ecff'
  primary-fixed-dim: '#91d0e4'
  on-primary-fixed: '#001f27'
  on-primary-fixed-variant: '#004e5e'
  secondary-fixed: '#dde4e6'
  secondary-fixed-dim: '#c1c8ca'
  on-secondary-fixed: '#161d1e'
  on-secondary-fixed-variant: '#41484a'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#fcb883'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#693c11'
  background: '#f9f9fc'
  on-background: '#1a1c1e'
  surface-variant: '#e2e2e5'
  surface-base: '#F8F9FA'
  surface-subtle: '#F1F3F4'
  border-low: '#DDE1E4'
  policy-blue: '#005566'
  policy-mint: '#93B1B7'
  dark-bg: '#0D0F10'
  dark-surface: '#16181A'
  dark-border: '#2C2F33'
typography:
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Public Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.4'
  label-md:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 26px
    fontWeight: '600'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1280px
  sidebar-width: 280px
  gutter: 24px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered for a pan-European youth think tank, prioritizing intellectual rigor, cross-border collaboration, and policy-driven impact. The aesthetic departs from typical "startup" vibrancy, opting instead for **Institutional Minimalism**: a style that conveys credibility through precision, whitespace, and structural clarity.

The target audience consists of policymakers, researchers, and young advocates. Consequently, the UI evokes a "digital atelier" feel—a calm, focused environment where complex information is easily parsed. The visual language utilizes a refined palette of soft neutrals and a singular, disciplined accent color to guide attention without overwhelming the content. High information density is balanced by a strict rhythmic grid, ensuring that even data-heavy policy papers remain legible and elegant.

## Colors

The color strategy is anchored in **Policy Teal (#005566)**, a color that suggests both the traditional stability of European institutions and the fresh perspective of a youth-led organization. 

- **Primary:** Reserved for critical actions, active navigation states, and primary brand markers. 
- **Neutral Palette:** Utilizes cool-toned grays to maintain a professional, "paper-like" quality in light mode. 
- **Dark Mode:** A "Calm Dark" implementation uses deep charcoal (`#0D0F10`) instead of pure black to reduce eye strain during long-form reading, with surfaces differentiated by subtle tonal shifts rather than heavy shadows.
- **Functional Accents:** Used sparingly for tags or map nodes to indicate categories without disrupting the monochromatic harmony.

## Typography

Typography is the cornerstone of this design system’s authority. We use **Hanken Grotesk** for headings to provide a sharp, contemporary edge, while **Public Sans**—originally designed for institutional clarity—serves as the workhorse for body copy and data.

To achieve "compact elegance," line heights are tightened slightly for headings but kept generous for body text to maintain readability in long-form policy briefs. Labels and metadata use a slightly tracked-out uppercase style to differentiate them clearly from narrative text.

## Layout & Spacing

The system employs a **Fixed-Fluid Hybrid** grid. The primary content area adheres to a 12-column grid with a maximum width of 1280px to prevent excessive line lengths in reports. The sidebar remains fixed at 280px on desktop to provide constant navigation access.

A strict 4px baseline grid ensures vertical rhythm. Spacing between sections is generous (`32px`+) to provide visual "breathing room," while internal component spacing is tight (`8px` or `12px`) to maintain the "compact" feel requested for high information density applications like data tables and member directories.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Subtle Outlines** rather than dramatic shadows. 

- **Surface Levels:** The background uses the base surface color, while interactive cards and containers sit one level above, differentiated by a 1px border in `border-low`.
- **Shadows:** Only used for transient elements like dropdowns or active search bars. These shadows are extremely diffused (20px-40px blur) with low opacity (4-8%), acting more as a soft glow than a physical drop shadow.
- **Glassmorphism:** Reserved exclusively for the sidebar navigation background in dark mode, using a slight backdrop blur to maintain context with the content "underneath."

## Shapes

The shape language is **Conservative & Sophisticated**. We use a "Soft" roundedness level (`4px` for standard components) to provide a modern feel without appearing too casual or "bubbly."

- **Small Components:** Tags and input fields use a `4px` radius.
- **Large Components:** Member cards and map modals use an `8px` radius (`rounded-lg`) to soften the larger surface area.
- **Interactive Nodes:** Map nodes are perfectly circular to distinguish them from structural UI elements.

## Components

### Sidebar Navigation
The sidebar is the primary anchor. It uses a clear vertical hierarchy with active states indicated by a subtle `policy-blue` left-border and a light `secondary_color_hex` background tint. 

### Member Cards
Cards are flat with a 1px border. They prioritize the person’s role and country icon, using `body-sm` for contact details and `label-md` for expertise tags. Hover states trigger a subtle shift in border color rather than an elevation lift.

### Data Tables
Tables are designed for high-density policy data. Use "ghost" horizontal lines only. The header row uses the `label-md` style with a slightly darker neutral background to anchor the columns.

### Search & Tags
Search bars are "Edge-to-Edge" in their containers with a leading icon. Tags are rectangular with `4px` corners, using low-saturation background colors (e.g., a very pale tint of the accent) to categorize content without visual noise.

### Interactive Map Nodes
Map nodes represent hubs of collaboration. Use the `primary_color_hex` for active hubs and a hollow ring for inactive or secondary nodes. On hover, nodes should expand slightly and trigger a "Tonal Layer" tooltip.

### Buttons
Primary buttons are solid `policy-blue` with white text. Secondary buttons are "Ghost" style—1px border with teal text—maintaining the system's minimal profile.