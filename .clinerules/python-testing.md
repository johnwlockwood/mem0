# Testing Rules (Python)

### Test Structure
- 100% test coverage for core memory operations
- Tests must follow this structure:
  ```python
  # tests/test_memory.py
  def test_add_memory_success(memory_service):
      # Given
      memory_data = {"content": "test", "user_id": "123"}

      # When
      result = memory_service.add(memory_data)

      # Then
      assert result.status == "success"
      assert result.id is not None
  ```

### Testing Requirements
- All tests must have:
  - Setup/Arrange
  - Execution/Act
  - Assertion/Assert
- Use pytest fixtures for common test data
- Mock external services (OpenAI, Qdrant, etc.)

### Test Execution
- All tests must be run using:
  ```bash
  poetry run pytest tests
  ```

### Test Coverage
- Minimum 85% branch coverage
- 100% coverage for:
  - Memory operations
  - Security critical code
  - Data validation layers
