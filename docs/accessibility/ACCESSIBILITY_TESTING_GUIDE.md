# Accessibility Testing Guide - Nzila Exports Platform
**Date:** December 16, 2025  
**Tester:** Development Team  
**Standards:** WCAG 2.1 Level AA

## Testing Environment Setup

### Prerequisites
- ✅ Frontend server running at http://localhost:5173/
- ⏳ Screen reader (NVDA on Windows or VoiceOver on macOS)
- ⏳ Browser: Chrome with axe DevTools extension
- ⏳ Keyboard-only testing mode (unplug/disable mouse)

## 1. Keyboard-Only Navigation Testing

### Test Objectives
- Verify all interactive elements are keyboard accessible
- Ensure logical tab order throughout the application
- Confirm modal dialogs trap focus properly
- Test skip links functionality

### Test Cases

#### TC-1.1: Login Page Navigation
**Steps:**
1. Navigate to http://localhost:5173/
2. Press Tab repeatedly
3. Verify tab order: Email → Password → Remember me → Login button → Register link → Language toggle
4. Press Enter on Login button (without filling fields)
5. Verify error messages are visible and reachable

**Expected Results:**
- ✅ Focus indicator (2px blue outline) visible on each element
- ✅ Tab order follows logical reading order
- ✅ Error messages receive focus and are keyboard accessible
- ✅ Enter key triggers form submission

**Status:** ⏳ Pending manual test

---

#### TC-1.2: Dashboard Navigation
**Steps:**
1. Login to application
2. Press Tab from top of page
3. Test "Skip to main content" link appears and works
4. Navigate through all sidebar menu items
5. Verify active page indicator is visible

**Expected Results:**
- ✅ Skip link visible on focus and functional
- ✅ All menu items reachable via Tab
- ✅ Active page has visual indicator
- ✅ Sidebar doesn't trap focus

**Status:** ⏳ Pending manual test

---

#### TC-1.3: Vehicle Modal Keyboard Access
**Steps:**
1. Navigate to Vehicles page
2. Tab to "Add Vehicle" button
3. Press Enter to open modal
4. Tab through all 12 form fields
5. Press Escape to close modal
6. Verify focus returns to "Add Vehicle" button

**Expected Results:**
- ✅ Modal opens with Enter key
- ✅ Focus trapped within modal
- ✅ Tab order through all fields is logical
- ✅ Escape closes modal
- ✅ Focus returns to trigger button

**Status:** ⏳ Pending manual test

---

#### TC-1.4: Payments Tab Navigation
**Steps:**
1. Navigate to Payments page
2. Tab to tab list
3. Use Left/Right arrow keys to navigate tabs
4. Press Home key to go to first tab
5. Press End key to go to last tab
6. Verify aria-selected updates correctly

**Expected Results:**
- ✅ Arrow keys change active tab
- ✅ Home/End keys work correctly
- ✅ Only active tab is in tab order (tabIndex=0)
- ✅ Tab key moves to tab panel content

**Status:** ⏳ Pending manual test

---

#### TC-1.5: Keyboard Shortcuts Modal
**Steps:**
1. From any page, press ? key
2. Verify Keyboard Shortcuts modal opens
3. Tab through all interactive elements
4. Press Escape to close

**Expected Results:**
- ✅ ? key triggers modal (not in input fields)
- ✅ Modal shows all keyboard shortcuts
- ✅ Focus trapped in modal
- ✅ Escape closes modal

**Status:** ⏳ Pending manual test

---

## 2. Screen Reader Testing

### Test Objectives
- Verify all content is announced correctly
- Ensure form labels and descriptions are read
- Confirm error messages are announced immediately
- Test landmark navigation

### Test Cases

#### TC-2.1: Page Structure & Landmarks
**Screen Reader:** NVDA (Windows) / VoiceOver (macOS)

**Steps:**
1. Navigate to Dashboard
2. Use landmark navigation (NVDA: D key, VO: Ctrl+Option+U)
3. Verify these landmarks exist:
   - Banner (header)
   - Navigation (sidebar)
   - Main content
   - Search (global search)

**Expected Announcements:**
- "Banner landmark" (top header)
- "Navigation landmark, Main navigation" (sidebar)
- "Main landmark, Main content" (page content)
- "Search landmark" (when opening search)

**Status:** ⏳ Pending manual test

---

#### TC-2.2: Vehicle Form Labels & Descriptions
**Screen Reader:** NVDA / VoiceOver

**Steps:**
1. Open Vehicle form modal
2. Tab through each field
3. Listen for announcements

**Expected Announcements for each field:**
- **Make:** "Make, required, edit, blank"
- **Model:** "Model, required, edit, blank"
- **VIN:** "VIN, required, 17-character Vehicle Identification Number, edit, blank"
- **Price:** "Price in USD, required, edit, blank"

**Status:** ⏳ Pending manual test

---

#### TC-2.3: Form Error Announcements
**Screen Reader:** NVDA / VoiceOver

**Steps:**
1. Open Vehicle form
2. Click Submit without filling required fields
3. Listen for error announcements

**Expected Announcements:**
- "Make is required" (immediate, assertive)
- "Model is required" (immediate, assertive)
- "Year is required" (immediate, assertive)
- Each error should be announced as role="alert"

**Status:** ⏳ Pending manual test

---

#### TC-2.4: Loading State Announcements
**Screen Reader:** NVDA / VoiceOver

**Steps:**
1. Submit Vehicle form with valid data
2. Listen during submission

**Expected Announcements:**
- Button changes to "Saving vehicle, busy"
- After success: "Vehicle saved successfully" (polite)
- Modal closes and focus returns

**Status:** ⏳ Pending manual test

---

#### TC-2.5: Tab Panel Announcements
**Screen Reader:** NVDA / VoiceOver

**Steps:**
1. Navigate to Payments page
2. Tab to tab list
3. Use arrow keys to switch tabs

**Expected Announcements:**
- "Payment sections, tab list"
- "Payment Methods, tab, selected, 1 of 3"
- Arrow Right: "Payment History, tab, 2 of 3"
- Enter: "Payment History panel"

**Status:** ⏳ Pending manual test

---

#### TC-2.6: Route Change Announcements
**Screen Reader:** NVDA / VoiceOver

**Steps:**
1. Click on "Vehicles" link in navigation
2. Listen for page change announcement

**Expected Announcements:**
- "Navigated to Vehicles" (polite, status)
- "Vehicles, heading level 1"
- Focus on h1 heading

**Status:** ⏳ Pending manual test

---

## 3. Automated Accessibility Testing

### Tool: axe DevTools (Chrome Extension)

#### TC-3.1: Full Page Scans
**Steps:**
1. Install axe DevTools extension
2. Navigate to each page:
   - Login
   - Dashboard
   - Vehicles
   - Deals
   - Payments
   - Settings
3. Run axe scan on each page
4. Document issues by severity

**Target:** 0 Critical, 0 Serious, < 5 Moderate, < 10 Minor

**Results Template:**
```
Page: [Page Name]
Critical: X
Serious: X
Moderate: X
Minor: X
Best Practices: X
Total Issues: X

Top Issues:
1. [Issue description]
2. [Issue description]
```

**Status:** ⏳ Pending automated test

---

### Tool: Lighthouse Accessibility Audit

#### TC-3.2: Lighthouse Scores
**Steps:**
1. Open Chrome DevTools → Lighthouse
2. Select "Accessibility" category only
3. Run audit on each page
4. Aim for 90+ score

**Expected Scores:**
- Login: 95+
- Dashboard: 90+
- Vehicles: 90+
- Deals: 90+
- Payments: 90+
- Settings: 90+

**Status:** ⏳ Pending automated test

---

## 4. Manual Keyboard Navigation Checklist

### All Pages
- [ ] Skip to main content link works
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicator visible (2px blue outline)
- [ ] No keyboard traps
- [ ] Tab order is logical
- [ ] Escape key closes modals
- [ ] Enter activates buttons

### Forms
- [ ] All labels associated with inputs
- [ ] Required fields marked with aria-required
- [ ] Error messages have role="alert"
- [ ] Submit button shows loading state (aria-busy)
- [ ] Focus moves to first error on validation

### Navigation
- [ ] All links keyboard accessible
- [ ] Active page indicator visible
- [ ] Dropdown menus keyboard accessible
- [ ] Mobile menu keyboard accessible

### Tabs (Payments Page)
- [ ] Arrow keys navigate between tabs
- [ ] Home/End keys work
- [ ] Only active tab in tab order
- [ ] Tab key moves to panel content

### Modals
- [ ] Focus trapped within modal
- [ ] First focusable element receives focus
- [ ] Escape key closes modal
- [ ] Focus returns to trigger on close

---

## 5. Screen Reader Testing Checklist

### Content Structure
- [ ] Page title announced on load
- [ ] Heading hierarchy is logical (h1 → h2 → h3)
- [ ] Landmarks identified (banner, nav, main)
- [ ] Lists properly marked up

### Forms
- [ ] Form labels read correctly
- [ ] Help text associated with fields
- [ ] Required fields announced
- [ ] Error messages announced immediately
- [ ] Validation errors listed

### Interactive Elements
- [ ] Button purpose clear from label
- [ ] Link destination clear
- [ ] Status messages announced
- [ ] Loading states communicated

### Dynamic Content
- [ ] Route changes announced
- [ ] Toast notifications announced
- [ ] Loading spinners communicated
- [ ] Form submission results announced

---

## 6. Color Contrast Verification

### Manual Checks
- [ ] All text meets 4.5:1 ratio (normal text)
- [ ] Large text meets 3:1 ratio
- [ ] Focus indicators have sufficient contrast
- [ ] UI components meet 3:1 contrast
- [ ] No information conveyed by color alone

**Reference:** See [COLOR_CONTRAST_AUDIT.md](COLOR_CONTRAST_AUDIT.md) for detailed analysis

**Status:** ✅ Completed - 98% WCAG AA compliant

---

## 7. Testing Tools Setup

### Install axe DevTools
```bash
# Chrome Web Store
# Search for "axe DevTools - Web Accessibility Testing"
# Install extension
```

### Install Screen Readers

**Windows (NVDA):**
```bash
# Download from: https://www.nvaccess.org/download/
# Install and start NVDA
# Key commands:
# - Insert + Down Arrow: Read from cursor
# - Insert + B: Read document from top
# - D: Next landmark
# - H: Next heading
# - F: Next form field
```

**macOS (VoiceOver):**
```bash
# Built-in, activate with: Cmd + F5
# Key commands:
# - Ctrl + Option + Right Arrow: Navigate forward
# - Ctrl + Option + U: Open rotor
# - Ctrl + Option + H: Next heading
# - Ctrl + Option + J: Next form control
```

---

## 8. Automated Testing Commands

### Run Lighthouse from CLI
```bash
# Install Lighthouse globally
npm install -g lighthouse

# Run audit on Login page
lighthouse http://localhost:5173/ --only-categories=accessibility --view

# Run audit on Dashboard (requires auth - use manual method)
# Open DevTools → Lighthouse → Run audit
```

### Run axe-core programmatically (future enhancement)
```javascript
// Install axe-core
npm install --save-dev @axe-core/cli

// Run automated scan
npx axe http://localhost:5173/ --exit
```

---

## 9. Test Results Summary

### Completion Status

| Test Category | Status | Pass Rate | Issues |
|---------------|--------|-----------|--------|
| Color Contrast | ✅ Complete | 98% | 2 minor |
| Keyboard Navigation | ⏳ Pending | - | - |
| Screen Reader | ⏳ Pending | - | - |
| Automated (axe) | ⏳ Pending | - | - |
| Automated (Lighthouse) | ⏳ Pending | - | - |

### Known Issues
1. **Minor:** Placeholder text uses slate-400 (3.39:1) - Recommend slate-500
2. **Minor:** Primary-500 color insufficient for normal text (3.29:1) - Use primary-600+

### Recommendations
1. Run full screen reader test suite with NVDA/VoiceOver
2. Complete keyboard-only navigation testing
3. Run automated axe scans on all pages
4. Achieve 90+ Lighthouse accessibility scores
5. Fix placeholder text contrast (0.5h effort)

---

## 10. Next Steps

1. **Immediate (Today):**
   - [x] Start frontend dev server ✅
   - [ ] Run keyboard navigation tests (1h)
   - [ ] Document initial findings

2. **Short-term (This Week):**
   - [ ] Complete screen reader testing (1.5h)
   - [ ] Run automated axe scans (0.5h)
   - [ ] Run Lighthouse audits (0.5h)
   - [ ] Fix any critical issues found

3. **Long-term (Ongoing):**
   - [ ] Set up automated accessibility tests in CI/CD
   - [ ] Train team on accessibility best practices
   - [ ] Establish accessibility review process
   - [ ] Monitor WCAG compliance in new features

---

## Contact & Resources

**Testing Lead:** Development Team  
**Reference Standard:** [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)  
**Support:** accessibility@nzilaexports.com (example)

**Resources:**
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [axe DevTools Documentation](https://www.deque.com/axe/devtools/)
- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)

---

**Last Updated:** December 16, 2025  
**Status:** 🟡 In Progress - Implementation complete, testing pending  
**Next Review:** December 17, 2025
