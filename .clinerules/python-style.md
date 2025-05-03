# Style Guide (Python)

### Python Specific
- Follow Ruff config in `pyproject.toml`
- Line length: 120 chars (already configured)
- Type hints required for all public APIs
- Use type guards for complex type checks

### Documentation
- All public modules require:
  - Module-level docstring
  - Example usage
  - API changelog
- Use Google-style docstrings:
  ```python
  def add_memory(data: dict) -> Memory:
      """Adds a new memory to the system.

      Args:
          data: Memory data containing content and metadata

      Returns:
          Created Memory object

      Raises:
          ValueError: If data validation fails
      """
