# Patient Test Screenshot Coverage

## Overview
All patient test scripts now include comprehensive screenshots at key points in the test flow to capture:
- **Before** input details are entered
- **After** input details are captured
- **Before** form submission
- **After** form submission and results

This ensures screenshots are taken when pages are fully loaded with content, not blank or loading states.

---

## PAT-001: View appointments list

### Screenshots:
1. **PAT-001-before.png** - Appointments page loaded (after navigation, before verification)
2. **PAT-001-after.png** - Appointments page with content verified

---

## PAT-002: Book service

### Screenshots:
1. **PAT-002-before-calendar.png** - Booking page with calendar loaded (before date selection)
2. **PAT-002-after-date-selection.png** - Time slots visible after date selected (before time selection)
3. **PAT-002-before-form-input.png** - Booking form visible (before filling attendant)
4. **PAT-002-after-form-input.png** - Form with all inputs filled (attendant selected)
5. **PAT-002-before-submission.png** - Form ready to submit (all fields filled)
6. **PAT-002-after-submission.png** - Result page after booking submission
7. **PAT-002-after.png** - Appointments list showing new appointment

**Total: 7 screenshots** covering the complete booking flow

---

## PAT-003: Book product-based session

### Screenshots:
1. **PAT-003-before-calendar.png** - Booking page with calendar loaded (before date selection)
2. **PAT-003-after-date-selection.png** - Time slots visible after date selected (before time selection)
3. **PAT-003-before-form-input.png** - Booking form visible (before filling attendant)
4. **PAT-003-after-form-input.png** - Form with all inputs filled (attendant selected)
5. **PAT-003-before-submission.png** - Form ready to submit (all fields filled)
6. **PAT-003-after-submission.png** - Result page after booking submission
7. **PAT-003-after.png** - Appointments list showing new appointment

**Total: 7 screenshots** covering the complete booking flow

---

## PAT-004: Book package session

### Screenshots:
1. **PAT-004-before-calendar.png** - Booking page with calendar loaded (before date selection)
2. **PAT-004-after-date-selection.png** - Time slots visible after date selected (before time selection)
3. **PAT-004-before-form-input.png** - Booking form visible (before filling attendant)
4. **PAT-004-after-form-input.png** - Form with all inputs filled (attendant selected)
5. **PAT-004-before-submission.png** - Form ready to submit (all fields filled)
6. **PAT-004-after-submission.png** - Result page after booking submission
7. **PAT-004-after.png** - My packages page showing updated balance

**Total: 7 screenshots** covering the complete booking flow

---

## PAT-005: View notifications

### Screenshots:
1. **PAT-005-before.png** - Notifications page loaded (after navigation)
2. **PAT-005-after.png** - Notifications page with content verified

---

## PAT-006: Request cancellation

### Screenshots:
1. **PAT-006-before.png** - Appointments list page (before finding appointment)
2. **PAT-006-before-form-input.png** - Cancellation form visible (before entering reason)
3. **PAT-006-after-form-input.png** - Form with cancellation reason entered
4. **PAT-006-before-submission.png** - Form ready to submit
5. **PAT-006-after-submission.png** - Result page after cancellation request
6. **PAT-006-after.png** - Appointments list showing cancellation status

**Total: 6 screenshots** covering the complete cancellation flow

---

## Screenshot Timing Strategy

### Key Principles:
1. **Wait for page load** - All screenshots are taken after `wait_for_load_state("networkidle")` to ensure content is loaded
2. **Wait for elements** - Screenshots are taken after waiting for specific elements (calendar, form, etc.) to be visible
3. **Wait after input** - Added `page.wait_for_timeout(500)` after filling forms to ensure UI updates are captured
4. **Before/After pairs** - Each major action has both "before" and "after" screenshots

### Screenshot Points:
- ✅ **Before calendar interaction** - Calendar fully loaded
- ✅ **After date selection** - Time slots visible
- ✅ **Before form input** - Form visible, empty
- ✅ **After form input** - All fields filled
- ✅ **Before submission** - Form ready to submit
- ✅ **After submission** - Result/confirmation page
- ✅ **Final state** - End result page

---

## Benefits

1. **Debugging** - Easy to see exactly what the page looked like at each step
2. **Verification** - Can verify form fields were filled correctly
3. **Documentation** - Visual record of test execution
4. **No blank pages** - All screenshots are taken after proper waits ensure content is loaded

---

*Last updated: After comprehensive screenshot coverage implementation*

