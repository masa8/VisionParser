# Testing Guide

## Overview
This project uses pytest for testing with comprehensive coverage of all modules:
- `models/`: Configuration and data models
- `services/`: Business logic (extractor, processor)
- `utils/`: Utility functions
- `main.py`: Main application entry point

## Test Structure
```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Pytest configuration and fixtures
├── test_models.py        # Tests for models package
├── test_services.py      # Tests for services package
├── test_utils.py         # Tests for utils package
└── test_main.py          # Tests for main module
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_models.py -v
```

### Run specific test class
```bash
pytest tests/test_models.py::TestEnvConfig -v
```

### Run specific test
```bash
pytest tests/test_models.py::TestEnvConfig::test_get_openai_api_key_valid -v
```

### Run with coverage report
```bash
pytest tests/ --cov=models --cov=services --cov=utils --cov=main --cov-report=term-missing
```

### Generate HTML coverage report
```bash
pytest tests/ --cov=models --cov=services --cov=utils --cov=main --cov-report=html
```
Then open `htmlcov/index.html` in your browser.

## Test Coverage

Current test coverage: **94%**

| Module                          | Coverage |
|---------------------------------|----------|
| models/env_config.py            | 97%      |
| models/image_folder_config.py   | 97%      |
| models/openai_config.py         | 96%      |
| models/app_config.py            | 94%      |
| services/extractor.py           | 98%      |
| services/processor.py           | 85%      |
| utils/image_utils.py            | 100%     |
| main.py                         | 98%      |

## Test Categories

### Unit Tests
Tests individual components in isolation using mocks:
- `test_models.py`: Tests configuration classes and validation logic
- `test_utils.py`: Tests utility functions
- `test_services.py`: Tests service classes with mocked dependencies
- `test_main.py`: Tests main function with mocked services

### Key Test Scenarios

#### Models Tests
- Environment variable configuration
- OpenAI API key validation
- Image folder validation
- Configuration parameter validation
- Config facade integration

#### Services Tests
- Image data extraction with GPT-4 Vision
- JSON response parsing
- Error handling (JSON decode, API errors)
- Batch image processing
- CSV file generation
- Processing result calculation

#### Utils Tests
- Image base64 encoding
- File handling
- Error cases

#### Main Tests
- Successful execution flow
- Configuration error handling
- Keyboard interrupt handling
- Unexpected error handling

## Writing New Tests

### Test Template
```python
import pytest
from unittest.mock import Mock, patch

class TestYourClass:
    """Test cases for YourClass"""
    
    @pytest.fixture
    def mock_dependency(self):
        """Create a mock dependency"""
        return Mock()
    
    def test_your_method(self, mock_dependency):
        """Test description"""
        # Arrange
        instance = YourClass(mock_dependency)
        
        # Act
        result = instance.your_method()
        
        # Assert
        assert result == expected_value
```

### Best Practices
1. **Use descriptive test names**: `test_get_openai_api_key_valid` is better than `test_key`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies**: Use `unittest.mock` for OpenAI API, file system, etc.
4. **Test edge cases**: Empty inputs, invalid values, error conditions
5. **Use fixtures**: Share common setup code across tests
6. **Test one thing**: Each test should verify one specific behavior

## Continuous Integration

Add to your CI/CD pipeline:
```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ --cov --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Dependencies

Test dependencies (already in requirements):
- `pytest>=9.0.0`: Testing framework
- `pytest-cov>=7.0.0`: Coverage plugin

Install with:
```bash
pip install pytest pytest-cov
```
