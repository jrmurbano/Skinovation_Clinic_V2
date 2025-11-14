# Playwright Test Scripts

This directory contains Python Playwright test scripts for all test cases defined in `TEST_CASES.md`.

## Structure

```
tests/playwright_python/
├── auth/              # Authentication test scripts (8 tests)
├── patient/           # Patient test scripts (6 tests)
├── attendant/         # Attendant test scripts (7 tests)
├── owner/             # Owner test scripts (20 tests)
├── staff/             # Staff/Admin test scripts (28 tests)
├── services/          # Services/Products/Packages test scripts (7 tests)
├── analytics/         # Analytics test scripts (5 tests)
├── screenshots/       # Screenshot output organized by category
├── conftest.py        # Shared fixtures and helper functions
└── README.md          # This file
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Configuration

The base URL is configured in `conftest.py` as `http://localhost:8000`. Make sure your Django development server is running before executing tests.

## Running Tests

### Run all tests:
```bash
pytest tests/playwright_python/
```

### Run tests by category:
```bash
# Authentication tests
pytest tests/playwright_python/auth/

# Patient tests
pytest tests/playwright_python/patient/

# Attendant tests
pytest tests/playwright_python/attendant/

# Owner tests
pytest tests/playwright_python/owner/

# Staff/Admin tests
pytest tests/playwright_python/staff/

# Services/Products/Packages tests
pytest tests/playwright_python/services/

# Analytics tests
pytest tests/playwright_python/analytics/
```

### Run a specific test:
```bash
pytest tests/playwright_python/auth/test_auth_001.py
```

### Run with verbose output:
```bash
pytest tests/playwright_python/ -v
```

### Run with screenshots on failure:
```bash
pytest tests/playwright_python/ --screenshot=only-on-failure
```

## Screenshots

Each test takes screenshots before and after execution:
- Before screenshot: `screenshots/{category}/{TEST_CASE_ID}-before.png`
- After screenshot: `screenshots/{category}/{TEST_CASE_ID}-after.png`

Screenshots are saved in the `screenshots/` directory, organized by test category.

## Test Credentials

The tests use the following test credentials (as defined in TEST_CASES.md):

- **Patient**: `maria.santos` / `TestPass123!`
- **Staff/Admin**: `admin.staff` / `AdminPass123!`
- **Owner**: `clinic.owner` / `OwnerPass123!`
- **Attendant**: `attendant.01` / `AttendPass123!`

## Helper Functions

The `conftest.py` file provides:

- `login_as_patient(page, username, password)` - Login as a patient
- `login_as_staff(page, username, password)` - Login as staff/admin
- `login_as_owner(page, username, password)` - Login as owner
- `login_as_attendant(page, username, password)` - Login as attendant
- `take_screenshot(page, filename)` - Take a full-page screenshot

## Notes

- Tests are designed to be independent and can be run in any order
- Some tests may require specific data to exist in the database (e.g., appointments, services)
- Delete operations in tests may be skipped to avoid data loss
- The browser runs in non-headless mode by default (visible) for debugging
- Adjust `browser_type_launch_args` in `conftest.py` to run in headless mode

## Troubleshooting

1. **Browser not found**: Run `playwright install` to install browser binaries
2. **Connection refused**: Ensure Django server is running on `http://localhost:8000`
3. **Element not found**: Check that the page has loaded completely using `page.wait_for_load_state("networkidle")`
4. **Screenshot errors**: Ensure the `screenshots/` directory structure exists

