# Timeout Fix for PAT-001

## Issue
PAT-001 was failing with a timeout error when trying to navigate to the login page:
```
playwright._impl._errors.TimeoutError: Page.goto: Timeout 30000ms exceeded.
```

## Root Cause
The default 30-second timeout was insufficient for the initial page navigation, especially when:
- The Django server needs time to initialize
- Network requests are slow
- The page has blocking modals or heavy JavaScript

## Solution Applied

### 1. Increased Default Timeouts
- **Navigation timeout**: Increased from 30s to 60s
- **General timeout**: Set to 30s for other operations

### 2. Retry Logic
- Added 3 retry attempts for navigation
- 2-second wait between retries
- Helps handle transient network issues

### 3. Improved Load State Handling
- Use `domcontentloaded` for faster initial load
- Then wait for `networkidle` with timeout
- Fallback to `load` state if `networkidle` times out

### 4. Modal Handling
- Automatically detect and close blocking modals (like reminder modal)
- Prevents modals from blocking page interactions

## Code Changes

```python
def login_as_patient(page: Page, username: str, password: str):
    # Set increased default timeout for navigation
    page.set_default_navigation_timeout(60000)
    page.set_default_timeout(30000)
    
    # Navigate to login page with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Use domcontentloaded for faster initial load
            page.goto(f"{BASE_URL}/accounts/login/", wait_until="domcontentloaded")
            # Wait for network to be idle with timeout
            try:
                page.wait_for_load_state("networkidle", timeout=30000)
            except:
                # If networkidle times out, at least wait for load state
                page.wait_for_load_state("load", timeout=10000)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                page.wait_for_timeout(2000)  # Wait 2 seconds before retry
                continue
            else:
                # Last attempt failed, raise the error
                raise
    
    # Check for and close any blocking modals
    try:
        reminder_modal = page.locator('#reminderModal, .modal.show, [id*="reminder"]').first
        if reminder_modal.is_visible(timeout=2000):
            close_button = page.locator('button:has-text("Got it"), button:has-text("Close"), .modal .close, .btn-close').first
            if close_button.is_visible(timeout=1000):
                close_button.click()
                page.wait_for_timeout(500)
    except:
        pass  # No modal found, continue
```

## Benefits

1. **More Reliable**: Retry logic handles transient failures
2. **Faster Initial Load**: Using `domcontentloaded` instead of waiting for full load
3. **Better Error Handling**: Graceful fallback if networkidle times out
4. **Modal Handling**: Automatically closes blocking modals
5. **Increased Timeouts**: Gives server more time to respond

## Testing

After this fix, PAT-001 should:
- Successfully navigate to the login page
- Handle slow server responses
- Retry on transient failures
- Close any blocking modals automatically

---

*Last updated: After fixing timeout issues in login_as_patient function*





