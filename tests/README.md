# End-to-End Tests

This directory contains end-to-end tests for the lego-agent project using Playwright.

## Prerequisites

1. Node.js (v18 or higher)
2. Python 3.8+
3. All dependencies installed:
   - `npm install` (in project root)
   - `npx playwright install` (install browsers)

## Running Tests

### Automated Test Run

The simplest way to run the tests is using the npm script from the project root:

```bash
npm run test:e2e
```

This will:
- Start the lego-web dev server automatically
- Run all tests in the `tests/e2e` directory
- Generate an HTML report

### Manual Service Start (for development)

If you need more control over the services, you can start them manually:

1. **Start lego-mcp in mock mode:**
   ```bash
   cd lego-mcp
   npm run build
   IS_MOCK=true node build/index.js
   ```

2. **Start lego-api:**
   ```bash
   cd lego-api
   # Create venv if needed
   python3 -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   pip install -e ../lego-robot-agent
   
   # Start the API
   uvicorn main:app --reload --port 8000
   ```

3. **Start lego-web:**
   ```bash
   cd lego-web
   npm run dev
   ```

4. **Run tests:**
   ```bash
   # From project root
   npx playwright test
   ```

## Test Structure

- `lego-web.spec.ts` - Main test suite for the web application
- Contains tests for:
  - Page rendering
  - Input box interaction
  - Command sending
  - Multiple command handling

## Mock Mode

The tests run with mock mode enabled for the observer agent:
- First image request returns `sample/step1.jpg`
- Subsequent image requests return `sample/step2.jpg`
- Robot commands are simulated (no actual robot connection)

## Viewing Test Results

After running tests, view the HTML report:

```bash
npx playwright show-report
```

## Screenshots

Test screenshots are saved in `tests/e2e/screenshots/` (ignored by git).
