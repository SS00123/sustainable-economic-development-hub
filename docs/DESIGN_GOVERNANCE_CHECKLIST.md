# DESIGN GOVERNANCE CHECKLIST
**Design System: Analytics Hub Platform**  
**Version: 1.0**  
**Last Updated: January 15, 2026**

---

## SECTION A: TOKEN PARITY VALIDATION

### A1. Color Token Verification
- [ ] All `bg_*` tokens match `app/styles/tokens.py` exactly
- [ ] All `text_*` tokens match code values
- [ ] All `status_*` tokens (green, amber, red) match
- [ ] All `accent_*` tokens match
- [ ] All `domain_*` tokens match
- [ ] All `border_*` tokens match
- [ ] Chart palette (10 colors) matches code array
- [ ] No additional colors invented in Figma
- [ ] Hex values are identical (case-insensitive)

### A2. Typography Token Verification
- [ ] Font families match code strings exactly
- [ ] All size tokens (hero through tiny) match
- [ ] All weight tokens (400-800) match
- [ ] Line height tokens match
- [ ] No additional font sizes created
- [ ] Inter font family loaded correctly
- [ ] Arabic fallback configured (if applicable)

### A3. Spacing Token Verification
- [ ] Base scale (xs through xxl) matches code
- [ ] Semantic spacing tokens match
- [ ] All values are multiples of 4px (8pt system)
- [ ] No arbitrary spacing values introduced
- [ ] Page margin = 32px verified
- [ ] Card padding = 20px verified

### A4. Radius Token Verification
- [ ] Base scale (xs through xxl) matches code
- [ ] Component-specific tokens match (card, button, input, badge)
- [ ] Full radius = 9999px verified
- [ ] No additional radius values created

### A5. Shadow Token Verification
- [ ] `card` shadow matches code string exactly
- [ ] `card_hover` shadow matches code string exactly
- [ ] Glow effects match (if used)
- [ ] Shadow blur, spread, offset values are precise
- [ ] No additional shadow layers invented

### A6. Transition Token Verification
- [ ] Fast = 150ms ease verified
- [ ] Normal = 200ms ease verified
- [ ] Slow = 300ms ease verified
- [ ] Smooth = 280ms cubic-bezier(0.4, 0, 0.2, 1) verified
- [ ] No additional timing curves created

---

## SECTION B: DRIFT PREVENTION

### B1. No Unauthorized Styles
- [ ] Figma Local Styles = Token count only
- [ ] No "legacy" or "deprecated" styles exist
- [ ] No styles named "Copy of..." or "Untitled"
- [ ] All styles reference token system
- [ ] No inline color/spacing values in designs

### B2. No Creative Additions
- [ ] No gradients beyond `bg_glass`
- [ ] No custom illustrations or patterns
- [ ] No marketing/decorative visuals
- [ ] No experimental color schemes
- [ ] No additional accent colors

### B3. No Naming Drift
- [ ] Token names use exact casing (e.g., `bg_main`, not `bgMain`)
- [ ] Token names use underscores (not hyphens or camelCase)
- [ ] No abbreviated names (e.g., `btn` instead of `button`)
- [ ] Category prefixes consistent (bg, text, status, accent, domain)

---

## SECTION C: IMPLEMENTATION ALIGNMENT

### C1. Figma-to-Code Handoff
- [ ] Designer can export token JSON
- [ ] Developer can map Figma tokens to Python tokens 1:1
- [ ] CSV files match JSON structure
- [ ] No ambiguous token references in designs
- [ ] Prototypes use only documented tokens

### C2. Documentation Completeness
- [ ] `DESIGN_SYSTEM_FOUNDATIONS.md` exists and is current
- [ ] `design_tokens.figmatokens.json` validated
- [ ] CSV files complete for all 6 categories
- [ ] `FIGMA_CONSTRUCTION_GUIDE.md` accurate
- [ ] All usage notes are clear and actionable

### C3. Version Control
- [ ] Figma file URL documented in project README
- [ ] Token changes logged with rationale
- [ ] Code changes trigger Figma review
- [ ] Figma changes trigger code review
- [ ] Sync process defined (weekly/monthly)

---

## SECTION D: SAFE EXTENSION RULES

### D1. Adding New Tokens (Approved Process)
1. **Proposal Phase**
   - [ ] Business case documented
   - [ ] Technical feasibility assessed
   - [ ] No overlap with existing tokens

2. **Implementation Phase**
   - [ ] Token added to `app/styles/tokens.py` first
   - [ ] Token added to Figma second
   - [ ] CSV and JSON updated
   - [ ] Tests pass (if applicable)

3. **Documentation Phase**
   - [ ] Token usage documented
   - [ ] Design guide updated
   - [ ] Governance checklist updated
   - [ ] Change announced to team

### D2. Forbidden Operations
- [ ] **NEVER** add tokens only in Figma
- [ ] **NEVER** modify token values without code sync
- [ ] **NEVER** rename tokens without migration plan
- [ ] **NEVER** delete tokens without deprecation period
- [ ] **NEVER** create "temp" or "test" token variants

### D3. Emergency Override
If urgent design need arises:
1. [ ] Use inline styles temporarily (mark as TEMP)
2. [ ] Create GitHub issue for token addition
3. [ ] Complete token addition process within 1 sprint
4. [ ] Replace temp styles with new token
5. [ ] Audit for other temp styles

---

## SECTION E: AUDIT PROTOCOL

### E1. Monthly Audit (Design Lead)
- [ ] Run Figma plugin: "Design Lint" or equivalent
- [ ] Check for unnamed layers
- [ ] Check for detached styles
- [ ] Verify no hard-coded values in components
- [ ] Review last 30 days of token changes

### E2. Quarterly Audit (Design + Engineering)
- [ ] Compare Figma file to `tokens.py` (line-by-line)
- [ ] Test JSON export/import cycle
- [ ] Verify all CSV files match code
- [ ] Review deprecated token candidates
- [ ] Check for unused tokens (usage < 1%)

### E3. Pre-Release Audit (Before Major Versions)
- [ ] Full token parity check (A1-A6)
- [ ] No drift detected (B1-B3)
- [ ] Documentation complete (C2)
- [ ] Handoff materials updated (C1)
- [ ] All forbidden operations verified (D2)

---

## SECTION F: APPROVAL WORKFLOW

### F1. Token Addition
1. **Requester:** Create proposal with justification
2. **Design Lead:** Approve design system fit
3. **Engineering Lead:** Approve technical feasibility
4. **Both:** Coordinate implementation
5. **QA:** Verify parity post-implementation

### F2. Token Modification
1. **Requester:** Document reason for change
2. **Design Lead:** Assess visual impact
3. **Engineering Lead:** Assess code impact
4. **Both:** Plan migration if breaking change
5. **QA:** Verify no regressions

### F3. Token Deprecation
1. **Requester:** Propose replacement token
2. **Design Lead:** Update designs to use replacement
3. **Engineering Lead:** Update code to use replacement
4. **Both:** Mark as deprecated for 1 release cycle
5. **Both:** Remove after deprecation period

---

## SECTION G: SIGN-OFF

### Initial Governance Setup (One-Time)
- [ ] **Design Lead** reviewed and approved token contract
- [ ] **Engineering Lead** reviewed and approved token contract
- [ ] **Product Owner** acknowledged governance process
- [ ] **QA Lead** integrated checks into test suite
- [ ] All stakeholders trained on process

Date: __________________  
Signatures:
- Design Lead: ___________________________
- Engineering Lead: ___________________________
- Product Owner: ___________________________

### Ongoing Compliance (Per Audit)
- [ ] Date of last audit: __________________
- [ ] Audit type (Monthly/Quarterly/Pre-Release): __________________
- [ ] Issues found: __________________
- [ ] Issues resolved: __________________
- [ ] Next audit scheduled: __________________

Auditor Signature: ___________________________

---

## APPENDIX: VIOLATION RESPONSE

### Severity Levels
1. **Critical:** Token values don't match code → Block release
2. **High:** Unauthorized tokens in production → Hotfix required
3. **Medium:** Naming drift detected → Fix in next sprint
4. **Low:** Documentation out of sync → Update within 2 weeks

### Escalation Path
1. Designer/Developer identifies issue
2. Report to Design Lead + Engineering Lead
3. Assess severity
4. Execute fix according to severity SLA
5. Update governance checklist
6. Post-mortem if Critical/High

---

**END OF GOVERNANCE CHECKLIST**
