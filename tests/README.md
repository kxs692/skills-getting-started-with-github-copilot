# Test configuration and documentation

## Running Tests

To run all tests:
```bash
python -m pytest tests/ -v
```

To run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

To run a specific test class:
```bash
python -m pytest tests/test_app.py::TestSignupEndpoint -v
```

To run a specific test:
```bash
python -m pytest tests/test_app.py::TestSignupEndpoint::test_successful_signup -v
```

## Test Structure

- `conftest.py`: Contains pytest fixtures and test configuration
- `test_app.py`: Main test file with comprehensive API endpoint tests

## Test Coverage

The tests provide comprehensive coverage for the FastAPI application, including:
- All major API endpoints (GET /activities, POST /signup, DELETE /unregister)
- Error handling scenarios
- Edge cases with URL encoding
- Complete signup/unregister workflows

## Test Categories

1. **TestBasicEndpoints**: Basic API functionality tests
2. **TestSignupEndpoint**: Activity signup functionality tests
3. **TestUnregisterEndpoint**: Activity unregister functionality tests
4. **TestActivityCapacity**: Participant count and workflow tests
5. **TestErrorHandling**: Error scenarios and edge cases