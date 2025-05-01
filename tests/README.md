# Unit Test Guide

This guide provides instructions for running unit tests and generating coverage reports for the `LEOCraft` project.

---

## Running Tests

### Run All Tests
To execute all the unit tests in the `tests` directory:
```bash
python -m unittest discover tests/ -v
```

### Run a Single Test Module
To run a specific test module, replace `<test_file>` with the desired test file name:
```bash
python -m unittest -v tests/<test_file>.py
```
Example:
```bash
python -m unittest -v tests/test_satellite.py
```

---

## Coverage Report

### Run Tests with Coverage
To run all tests and collect coverage data:
```bash
coverage run -m unittest discover tests/ -v
```

### View Coverage Report in Terminal
To display the coverage report in the terminal:
```bash
coverage report
```

### Generate HTML Coverage Report
To generate an HTML report for better visualization:
```bash
coverage html
```

Open the generated `htmlcov/index.html` file in your browser to view the detailed coverage report.