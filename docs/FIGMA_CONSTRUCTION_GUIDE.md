# FIGMA CONSTRUCTION GUIDE
**Token Contract Implementation**  
**Source:** `analytics_hub_platform/app/styles/tokens.py`  
**Target:** Figma Page "00 — Foundations (Token Contract)"

---

## PREREQUISITE ACTIONS
1. Install "Tokens Studio for Figma" plugin (if using JSON import)
2. Set default font to Inter (or system fallback)
3. Create new Figma page: `00 — Foundations (Token Contract)`
4. Set page background: `#0B1120` (bg_deep)

---

## FRAME STRUCTURE

### ROOT FRAME
1. Create frame: `Foundations Container`
   - Width: 1440px
   - Height: Auto
   - Layout: Auto Layout (Vertical)
   - Padding: 48px all sides
   - Gap: 48px
   - Background: `#111827` (bg_main)

---

## SECTION 1 — COLOR TOKENS

### Frame: `01 Color Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 32px
4. Width: Fill container

### Header
1. Text: "Color Tokens"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Color Groups
For each group (bg, text, status, accent, domain, border, chart_palette):

1. Create sub-frame: `[group_name]` (e.g., "bg")
   - Auto Layout: Vertical
   - Gap: 8px

2. Add group label:
   - Text: Group name in uppercase
   - Font: Inter Medium 14px
   - Color: `rgba(255, 255, 255, 0.55)`

3. Create swatch grid:
   - Auto Layout: Horizontal Wrap
   - Gap: 8px
   - Padding: 0

4. For each token in group:
   - Create frame: 160px × 80px
   - Border radius: 8px
   - Fill: Token color value
   - Border: 1px, `rgba(255, 255, 255, 0.08)`

5. Add text overlay to each swatch:
   - Token name (Inter Medium 12px)
   - Hex value (Inter Regular 11px, opacity 0.78)
   - Position: Bottom left, padding 8px

---

## SECTION 2 — TYPOGRAPHY TOKENS

### Frame: `02 Typography Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 24px
4. Width: Fill container

### Header
1. Text: "Typography Tokens"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Font Families
1. Create sub-frame: `Font Families`
2. List each family:
   - Token name (Inter Medium 12px)
   - Font stack (Inter Regular 11px, mono)

### Type Scale
For each size token (hero, h1, h2, h3, h4, body, caption, small, tiny):

1. Create text sample frame
   - Auto Layout: Vertical
   - Gap: 4px
   - Padding: 12px 0

2. Add label:
   - Text: Token name
   - Font: Inter Medium 11px
   - Color: `rgba(255, 255, 255, 0.55)`

3. Add sample text:
   - Text: "Executive KPI performance overview"
   - Font: Inter Regular [token_size]
   - Color: `rgba(255, 255, 255, 0.95)`

4. Add metadata:
   - Text: "Size: [value] | Weight: Regular | Line: 1.5"
   - Font: Inter Regular 10px
   - Color: `rgba(255, 255, 255, 0.35)`

### Weights
1. Create sub-frame: `Font Weights`
2. For each weight (regular, medium, semibold, bold, extrabold):
   - Sample text with weight applied
   - Label with token name and value

---

## SECTION 3 — SPACING TOKENS

### Frame: `03 Spacing Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 24px
4. Width: Fill container

### Header
1. Text: "Spacing Tokens (8pt System)"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Spacing Scale
For each token (xs, sm, md, lg, xl, xxl, and semantic tokens):

1. Create row frame:
   - Auto Layout: Horizontal
   - Align: Center
   - Gap: 16px
   - Height: 40px

2. Add label:
   - Text: Token name
   - Font: Inter Medium 12px
   - Color: `rgba(255, 255, 255, 0.95)`
   - Width: 120px

3. Add value:
   - Text: Pixel value
   - Font: Inter Mono Regular 11px
   - Color: `rgba(255, 255, 255, 0.78)`
   - Width: 60px

4. Add visualization bar:
   - Rectangle: Width = token value, Height = 24px
   - Fill: `#06B6D4` (accent_primary)
   - Border radius: 4px

---

## SECTION 4 — RADIUS TOKENS

### Frame: `04 Radius Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 24px
4. Width: Fill container

### Header
1. Text: "Radius Tokens"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Radius Samples
1. Create grid:
   - Auto Layout: Horizontal Wrap
   - Gap: 16px

2. For each token (xs, sm, md, lg, xl, xxl, full, card, button, input, badge):
   - Create sample frame: 120px × 120px
   - Fill: `#1E293B` (bg_card)
   - Border: 1px, `rgba(255, 255, 255, 0.08)`
   - Border radius: Token value
   
3. Add label below each sample:
   - Token name (Inter Medium 11px)
   - Value (Inter Regular 10px, muted)

---

## SECTION 5 — SHADOW TOKENS

### Frame: `05 Shadow Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 24px
4. Width: Fill container

### Header
1. Text: "Shadow Tokens"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Shadow Samples
1. Create grid:
   - Auto Layout: Horizontal Wrap
   - Gap: 24px

2. For primary shadows (card, card_hover):
   - Create sample card: 200px × 120px
   - Fill: `#1E293B` (bg_card)
   - Border radius: 16px
   - Shadow: Apply token value exactly
   
3. Add label inside card:
   - Token name (Inter Semibold 14px)
   - Shadow string (Inter Mono Regular 9px, word wrap)

4. For glow effects:
   - Use same layout
   - Add note: "Used sparingly"

---

## SECTION 6 — TRANSITION TOKENS

### Frame: `06 Transition Tokens`
1. Create frame inside `Foundations Container`
2. Auto Layout: Vertical
3. Gap: 16px
4. Width: Fill container

### Header
1. Text: "Transition Tokens"
2. Font: Inter Semibold 24px
3. Color: `rgba(255, 255, 255, 0.95)`

### Transition List
For each token (fast, normal, slow, smooth):

1. Create row frame:
   - Auto Layout: Horizontal
   - Gap: 16px
   - Padding: 12px 0

2. Add token name:
   - Font: Inter Medium 12px
   - Color: `rgba(255, 255, 255, 0.95)`
   - Width: 100px

3. Add value:
   - Font: Inter Mono Regular 11px
   - Color: `rgba(255, 255, 255, 0.78)`

4. Add usage note:
   - Font: Inter Regular 11px
   - Color: `rgba(255, 255, 255, 0.55)`

---

## LAYOUT POLISH

### Final Steps
1. Ensure all frames use Auto Layout
2. Verify 8px spacing increments throughout
3. Set consistent padding:
   - Section frames: 24px all sides
   - Sub-frames: 16px all sides
4. Add divider lines between sections:
   - Height: 1px
   - Fill: `rgba(255, 255, 255, 0.08)`
5. Group related elements properly
6. Name all layers with token names (no "Rectangle 1" or "Frame 42")

### Naming Convention
- Frames: `Token Category - Token Name`
- Text: `Label: [content]`
- Shapes: `Swatch: token_name` or `Bar: token_name`

---

## JSON IMPORT (ALTERNATIVE)

If using Tokens Studio plugin:

1. Open Tokens Studio panel
2. Click "Load from JSON"
3. Select `design_tokens.figmatokens.json`
4. Tokens will populate automatically
5. Use "Create Styles" to generate Figma styles
6. Manual layout still required for documentation page

---

## QUALITY CHECKLIST

Before finalizing:
- [ ] All frames use Auto Layout
- [ ] No absolute positioning (except text overlays)
- [ ] All colors match hex values exactly
- [ ] All spacing uses 8pt increments
- [ ] All text layers have proper names
- [ ] Inter font family applied consistently
- [ ] Background colors from token system
- [ ] No invented or ad-hoc values
- [ ] Page renders correctly at 1440px width
- [ ] Export capability verified (PDF/PNG)
