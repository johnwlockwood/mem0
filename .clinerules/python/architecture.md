# Architecture Rules (Python)

### Package Structure
- All business logic must reside in `mem0/` directory
- Use 3-tier architecture pattern:
  ```python
  # Example service structure
  mem0/
    services/
      __init__.py
      chat_service.py
    repositories/
      __init__.py
      memory_repository.py
    use_cases/
      __init__.py
      add_memory_use_case.py
  ```

### Dependency Management
- Follow dependency inversion principle
- No circular dependencies allowed
- Use `poetry add` for all new dependencies
- Keep `pyproject.toml` exclude list up-to-date

### API Design
- REST endpoints must follow OpenAPI 3.0 spec
- GraphQL must use Strawberry with type annotations
- All public APIs require deprecation plan for removal
