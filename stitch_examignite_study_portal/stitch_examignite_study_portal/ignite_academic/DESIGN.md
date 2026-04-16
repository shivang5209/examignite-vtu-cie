# Design System Strategy: The Scholarly Curator

## 1. Overview & Creative North Star
The "Creative North Star" for this design system is **The Scholarly Curator**. 

In an era of cluttered, generic educational dashboards, this system moves in the opposite direction. It treats engineering study material not as data points, but as high-value editorial content. The goal is to create a "Focus Sanctuary"—an environment that feels as premium as a physical high-end library but as fluid as a modern digital workspace.

We achieve this by breaking the "SaaS template" look. We favor **intentional asymmetry**, high-contrast typography scales, and layered tonal depth over rigid grids and lines. The interface should feel breathable and smart, encouraging students to stay longer and think deeper.

---

## 2. Colors & Tonal Architecture
The palette is rooted in a deep, authoritative Teal (`primary`) supported by a focused Blue (`secondary`) and an Amber (`tertiary`) that acts as a beacon for critical insights.

### The "No-Line" Rule
To maintain a premium editorial feel, **1px solid borders for sectioning are strictly prohibited.** Boundaries must be defined solely through:
- **Background Color Shifts:** Placing a `surface-container-low` section against a `surface` background.
- **Tonal Transitions:** Using subtle shifts in hue to define the start of a sidebar or header.

### Surface Hierarchy & Nesting
Think of the UI as physical layers of fine paper. 
- **Base Layer:** `surface` (#F9F9FF) is your canvas.
- **Mid Layer:** `surface-container-low` (#F1F3FF) for large structural areas like sidebars.
- **Top Layer:** `surface-container-lowest` (#FFFFFF) for interactive cards and primary content blocks.
- **Floating Layer:** `surface-bright` for elements that need to feel elevated above the logic of the page.

### The Glass & Gradient Rule
To avoid a "flat" feel, use **Glassmorphism** for floating navigation or overlays. Use `surface_container_lowest` at 80% opacity with a `24px` backdrop-blur. 
**Signature Texture:** Main CTAs and Hero sections should utilize a subtle linear gradient (135°) from `primary` (#005C55) to `primary_container` (#0F766E). This adds "soul" and prevents the teal from feeling clinical.

---

## 3. Typography: The Editorial Voice
We use typography to command attention and guide the eye. The contrast between the expressive **Epilogue** and the functional **Manrope** is the core of our visual identity.

- **Display & Headlines (Epilogue):** These are your "Confidence" anchors. Use `display-lg` (3.5rem) for welcome states and `headline-md` (1.75rem) for module titles. Keep letter-spacing tight (-0.02em) to maintain a bold, editorial punch.
- **Body & Labels (Manrope):** This is the "Engine." `body-lg` (1rem) is the standard for study notes. It provides high legibility for complex engineering concepts.
- **Hierarchy through Scale:** Do not use bold weights for everything. Use size contrast. A huge `display-sm` headline next to a small, muted `label-md` creates more "design intent" than two medium-sized bold elements.

---

## 4. Elevation & Depth
We convey hierarchy through **Tonal Layering** rather than structural lines.

- **The Layering Principle:** Place a `surface-container-lowest` card on a `surface-container-low` section. The natural contrast creates a soft lift.
- **Ambient Shadows:** For floating elements (Modals, Popovers), use "Shadow-Soft." 
  - *Value:* `0px 20px 48px rgba(20, 27, 43, 0.06)`. 
  - The shadow color must be a tinted version of `on_surface` (Dark Navy) rather than pure black, ensuring the depth feels natural to the environment.
- **The "Ghost Border" Fallback:** If a container sits on a background of the same color (e.g., for accessibility), use a `0.5px` border of `outline-variant` (#BDC9C6) at 20% opacity. It should be felt, not seen.

---

## 5. Components

### Buttons
- **Primary:** Gradient fill (`primary` to `primary_container`), `xl` (1.5rem) rounding, white text.
- **Secondary:** `secondary_fixed` background with `on_secondary_fixed` text. No border.
- **Tertiary:** No background. Bold `primary` text with a subtle underline or icon.

### Cards & Study Modules
- **Rule:** No divider lines. Separate content using `1.5rem` or `2rem` vertical whitespace.
- **Styling:** Use `surface_container_lowest`, `lg` (1rem) rounding, and the Ambient Shadow for "active" states.

### Input Fields
- **Base State:** `surface_container_low` background, no border, `md` rounding.
- **Focus State:** `1.5px` solid `primary` border. The background remains light to keep the focus on the text.

### Progress & Chips (The "Ignite" Elements)
- **Selection Chips:** `primary_fixed` background with `on_primary_fixed` text.
- **Accent Chips:** Use the Amber `tertiary_fixed` for "Important" or "Exam-Prep" tags. It provides a warm contrast to the cool Teal/Blue environment.

### Special Component: The Study Pulse
A unique card type for VTU engineering subjects. It uses a `backdrop-blur` glass effect over a subtle `primary_container` gradient background to highlight "Trending Topics" or "Flashcards."

---

## 6. Do’s and Don’ts

### Do:
- **Do** use whitespace as a functional tool. If elements feel crowded, increase the gap before adding a line.
- **Do** use `display` type for personal moments (e.g., "Good Morning, Rahul").
- **Do** align items to a 8px/4px soft grid but allow for asymmetrical "editorial" offsets in hero areas.

### Don’t:
- **Don't** use pure black (#000000) for text. Always use `on_surface` (#141B2B) to keep the contrast premium.
- **Don't** use standard 1px gray dividers. They break the flow of the Scholarly Curator aesthetic.
- **Don't** use the Amber accent for large surfaces. It is a "spark" (Accent), not a "fire" (Primary).
- **Don't** use "Dashboard" cards (small, cramped boxes). Keep cards large, spacious, and meaningful.