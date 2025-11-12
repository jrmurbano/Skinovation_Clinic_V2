# Test Script Issues Report

This document tracks issues found when manually navigating through test scripts using browser automation. Each test was reviewed to identify missing clicks, input fields, selector mismatches, and other issues that would cause tests to fail.

## Summary

- **Total Test Categories**: 6 (excluding AUTH)
- **Total Test Files Reviewed**: Representative samples from each category
- **Common Issues Found**: 
  1. Selector mismatches (tests look for elements that don't exist)
  2. Missing form field interactions (calendar widgets vs form inputs)
  3. Hardcoded IDs that may not exist in database
  4. Missing wait conditions for dynamic content

---

## PATIENT TESTS (PAT-001 to PAT-006)

### PAT-001: View appointments list ✅
**Status**: PASSES
- Test navigates to `/appointments/` correctly
- Page loads successfully
- No issues found

### PAT-002: Book service ✅
**Status**: FIXED - Calendar widget interactions implemented

**Issues**:
1. **Selector Mismatch**: Test looks for `a[href*='/services/1/']` but actual booking links go directly to `/appointments/book/service/{id}/` (e.g., `/appointments/book/service/25/`)
2. **Form Field Mismatch**: Test expects:
   - `input[name="date"]` or `input[type="date"]` → **NOT FOUND (0 elements)**
   - `select[name="time"]` → **NOT FOUND (0 elements)**
   - `select[name="attendant"]` → **FOUND (1 element)** ✅
   - But the actual UI uses a **calendar widget** with clickable date cells, not form inputs
3. **Missing Interaction**: Test needs to:
   - Click on a calendar date cell (dates are clickable elements, not input fields)
   - Select time from calendar interface (time selection appears after date selection, not as a dropdown)
   - Select attendant from dropdown (this exists and works!)
   - Click "Book Appointment" button (exists, text: "Book Appointment")

**Verified Elements on Booking Page**:
- ✅ Form exists (`hasForm: true`)
- ✅ Attendant select exists (`attendantSelects: 1`)
- ✅ Submit button exists (`submitButtons: 1`, text: "Book Appointment")
- ❌ Date input: 0 elements (uses calendar widget)
- ❌ Time select: 0 elements (time appears after date selection in calendar)

**Required Fixes**:
- Update selectors to match actual booking flow: `/appointments/book/service/{id}/`
- Replace `date_input.fill("2025-01-15")` with calendar date cell click: `page.click('button:has-text("15")')` or similar
- Replace time select interaction with calendar time slot selection (time slots appear after date is selected)
- Keep attendant select interaction (this works!)
- Update submit button selector to: `button:has-text("Book Appointment")`

### PAT-003: Book product-based session ✅
**Status**: FIXED - Calendar widget interactions implemented
- Updated to use calendar widget instead of form fields
- Fixed date and time selection logic

### PAT-004: Book package session ✅
**Status**: FIXED - Calendar widget interactions implemented
- Updated to use calendar widget instead of form fields
- Fixed date and time selection logic

### PAT-005: View notifications ⚠️
**Status**: PARTIAL - API Issue
- Test navigates to `/appointments/notifications/` correctly
- **Issue Found**: Console shows 404 error for notifications API endpoint
- Error: `Failed to load resource: the server responded with a status of 404`
- Test may pass URL check but functionality may be broken

### PAT-006: Request cancellation ⚠️
**Status**: UNTESTED - Requires Existing Appointment
- Test requires appointment with ID 5 to exist
- Cannot verify without test data
- Selectors look reasonable but need verification with actual data

---

## ATTENDANT TESTS (ATD-001 to ATD-007)

### ATD-001: View appointments list ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/attendant/appointments/` route
- Needs attendant login to verify

### ATD-002: Appointment detail ⚠️
**Status**: UNTESTED - Requires Data
- Test expects appointment ID 5 to exist
- Selectors look for appointment links/details
- Cannot verify without test data

---

## OWNER TESTS (OWN-001 to OWN-010, plus image/SMS tests)

### OWN-001: View owner dashboard ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/owner/` route
- Needs owner login to verify

### OWN-002: View patients ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/owner/patients/` route
- Selectors look reasonable but need verification

---

## STAFF/ADMIN TESTS (ADM-001 to ADM-026, plus SMS tests)

### ADM-001: View admin dashboard ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/appointments/admin/dashboard/` route
- Needs admin login to verify

### ADM-002: Maintenance page ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/appointments/admin/maintenance/` route
- Needs admin login to verify

---

## SERVICES TESTS (SRV, PRD, PKG)

### SRV-001: Services list ✅
**Status**: PASSES
- Test navigates to `/services/` correctly
- Page loads successfully with service cards
- "Book Now" buttons are present and functional
- No issues found

---

## ANALYTICS TESTS (ANA-001 to ANA-005)

### ANA-001: Analytics dashboard ⚠️
**Status**: UNTESTED - Requires Login
- Test expects `/owner/analytics/` route
- Needs owner login to verify

---

## COMMON PATTERNS & RECOMMENDATIONS

### 1. Calendar Widget vs Form Fields
**Issue**: Many booking tests expect form inputs but UI uses calendar widgets
**Affected Tests**: PAT-002, PAT-003, PAT-004, and likely others
**Solution**: 
- Update tests to interact with calendar widget
- Click date cells instead of filling date inputs
- Find time selection mechanism in calendar interface
- Update attendant selection logic

### 2. Hardcoded IDs
**Issue**: Tests use hardcoded IDs (e.g., service ID 1, appointment ID 5) that may not exist
**Affected Tests**: Most tests with specific IDs
**Solution**:
- Use dynamic ID selection (first available, or create test data)
- Or ensure test data exists before running tests

### 3. Selector Specificity
**Issue**: Some selectors may be too specific or not match actual implementation
**Solution**:
- Use more flexible selectors
- Add fallback selectors (already done in some tests)
- Verify selectors match actual HTML structure

### 4. Missing Wait Conditions
**Issue**: Some tests may need additional wait conditions for dynamic content
**Solution**:
- Add `wait_for_load_state("networkidle")` where needed
- Wait for specific elements before interacting
- Handle async content loading

### 5. API Endpoint Issues
**Issue**: Notifications API returns 404
**Affected**: PAT-005 and potentially other notification-related tests
**Solution**:
- Fix notifications API endpoint
- Or update tests to handle missing API gracefully

---

## PRIORITY FIXES

### High Priority
1. ✅ **PAT-002, PAT-003, PAT-004**: Fixed calendar widget interactions
2. **Notifications API**: Fix 404 error for notifications endpoint
3. **Test Data Setup**: Ensure test data exists (appointments, services, etc.)

### Medium Priority
1. Verify all login flows work correctly
2. Test all category-specific routes exist
3. Verify selector accuracy across all tests

### Low Priority
1. Add more robust error handling
2. Improve test data management
3. Add more comprehensive assertions

---

## NEXT STEPS

1. ✅ Fix calendar widget interaction logic in booking tests (COMPLETED)
2. Fix notifications API endpoint
3. Create test data fixtures for required IDs
4. Verify all routes exist and are accessible
5. ✅ Update selectors to match actual UI implementation (COMPLETED for booking tests)
6. ✅ Add proper wait conditions for dynamic content (COMPLETED for booking tests)

## FIXES APPLIED

### Booking Tests (PAT-002, PAT-003, PAT-004)
- ✅ Replaced form field interactions with calendar widget clicks
- ✅ Updated date selection to use `.calendar-day[data-date]` selector
- ✅ Updated time selection to use `.time-slot` clickable divs
- ✅ Added proper wait conditions for calendar, time slots, and booking form
- ✅ Fixed service/product/package booking link selectors
- ✅ Updated submit button selector to match actual button text
- ✅ Added fallback logic for unavailable dates/times

---

*Report generated by manual browser navigation through test scripts*
*Date: 2025-01-XX*

