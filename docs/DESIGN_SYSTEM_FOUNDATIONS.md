# DESIGN SYSTEM FOUNDATIONS (Token Contract)

**Source of Truth**: `analytics_hub_platform/app/styles/tokens.py`  
**Status**: APPROVED  
**Format**: Figma Spec Reflection  

---

## SECTION 1 — Color Tokens

### Backgrounds (bg/*)
| Token Name | Value | Usage Note |
| :--- | :--- | :--- |
| `bg_deep` | `#0B1120` | Deepest background (hero, overlays) |
| `bg_main` | `#111827` | Main canvas background |
| `bg_card` | `#1E293B` | Card background |
| `bg_card_alt` | `#1E2340` | Alternate card (subtle differentiation) |
| `bg_hover` | `#334155` | Hover state |
| `bg_glass` | `linear-gradient(...)` | Glassmorphism effect |

### Text (text/*)
| Token Name | Value | Usage Note |
| :--- | :--- | :--- |
| `text_primary` | `rgba(255, 255, 255, 0.95)` | Main body text |
| `text_secondary` | `rgba(255, 255, 255, 0.78)` | Secondary text |
| `text_muted` | `rgba(255, 255, 255, 0.55)` | Labels, captions |
| `text_subtle` | `rgba(255, 255, 255, 0.35)` | Hints, disabled |

### Status (status/*)
| Token Name | Value | Usage Note |
| :--- | :--- | :--- |
| `status_green` | `#10B981` | Success foreground |
| `status_green_bg` | `rgba(16, 185, 129, 0.15)` | Success background |
| `status_amber` | `#F59E0B` | Warning foreground |
| `status_amber_bg` | `rgba(245, 158, 11, 0.15)` | Warning background |
| `status_red` | `#EF4444` | Danger/Risk foreground |
| `status_red_bg` | `rgba(239, 68, 68, 0.15)` | Danger/Risk background |

### Accent (accent/*)
| Token Name | Value | Usage Note |
| :--- | :--- | :--- |
| `accent_primary` | `#06B6D4` | Cyan - primary accent |
| `accent_secondary` | `#3B82F6` | Blue - secondary accent |
| `accent_purple` | `#8B5CF6` | Violet |
| `accent_pink` | `#EC4899` | Pink |

### Domain (domain/*)
| Token Name | Value | Usage Note |
| :--- | :--- | :--- |
| `domain_economic` | `#3B82F6` | Blue |
| `domain_labor` | `#8B5CF6` | Violet |
| `domain_social` | `#06B6D4` | Cyan |
| `domain_environmental` | `#10B981` | Green |
| `domain_data_quality` | `#64748B` | Slate |

---

## SECTION 2 — Typography Tokens

### Font Families
- **Base**: `family_base` ('Inter', -apple-system...)
- **Arabic**: `family_arabic`
- **Mono**: `family_mono`

### Headings & Body
| Token Name | Size | Weight | Sample |
| :--- | :--- | :--- | :--- |
| `hero` | 48px | - | Executive Overview |
| `h1` | 32px | - | Page Title |
| `h2` | 24px | - | Section Header |
| `h3` | 18px | - | Card Title |
| `h4` | 16px | - | Subsection |
| `body` | 14px | - | The quick brown fox... |
| `caption` | 12px | - | Figure 1.1 |
| `small` | 11px | - | Metadata |
| `tiny` | 10px | - | Microcopy |

### Weights (weight/*)
- `weight_regular`: 400
- `weight_medium`: 500
- `weight_semibold`: 600
- `weight_bold`: 700
- `weight_extrabold`: 800

### Line Heights
- `line_tight`: 1.25
- `line_normal`: 1.5
- `line_relaxed`: 1.75

---

## SECTION 3 — Spacing Tokens (8pt System)

### Base Scale
| Token Name | Value | Visual |
| :--- | :--- | :--- |
| `xs` | 4px | █ |
| `sm` | 8px | ██ |
| `md` | 16px | ████ |
| `lg` | 24px | ██████ |
| `xl` | 32px | ████████ |
| `xxl` | 48px | ████████████ |

### Semantic Spacing
- `page_margin`: 32px
- `section_gap`: 32px
- `card_gap`: 24px
- `card_padding`: 20px
- `row_gap`: 20px
- `gutter`: 16px
- `inline_gap`: 8px

---

## SECTION 4 — Radius Tokens

### Base Scale
| Token Name | Value |
| :--- | :--- |
| `xs` | 4px |
| `sm` | 6px |
| `md` | 8px |
| `lg` | 12px |
| `xl` | 16px |
| `xxl` | 20px |
| `full` | 9999px |

### Semantic Radius
- `card`: 16px
- `button`: 8px
- `input`: 8px
- `badge`: 20px

---

## SECTION 5 — Shadow Tokens

### Main Tokens
| Token Name | Value |
| :--- | :--- |
| `card` | `0 4px 6px rgba(0, 0, 0, 0.1), 0 20px 50px rgba(0, 0, 0, 0.4)` |
| `card_hover` | `0 8px 16px rgba(0, 0, 0, 0.15), 0 30px 60px rgba(0, 0, 0, 0.45)` |

### Variants
- `card_sm`: `0 2px 4px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.3)`
- `card_subtle`: `0 4px 12px rgba(0, 0, 0, 0.25)`

### Glows
- `glow_purple`, `glow_cyan`, `glow_green`, `glow_amber`, `glow_red`

---

## SECTION 6 — Transition Tokens

| Token Name | Duration/Config |
| :--- | :--- |
| `fast` | 150ms ease |
| `normal` | 200ms ease |
| `slow` | 300ms ease |
| `smooth` | 280ms cubic-bezier(0.4, 0, 0.2, 1) |

---

## Verification Logic for Figma Designer
1. **Checklist**:
   - [x] Section 1: Color Tokens
   - [x] Section 2: Typography Tokens
   - [x] Section 3: Spacing Tokens
   - [x] Section 4: Radius Tokens
   - [x] Section 5: Shadow Tokens
   - [x] Section 6: Transition Tokens

2. **Match Confirmation**: 
   - All token names listed above are 1:1 matches with `app/styles/tokens.py`.

3. **Missing Tokens**:
   - None. All major token categories from the python file are represented.
   - Note: The specialized `chart_palette` tuple in Python maps to the chart color cycle in Figma but is not a named dictionary key like the others. It uses the hex codes listed in `ColorTokens`.

