# Architecture Rules (mem0-ts)

### Module Structure
- Organize code logically within the `src/` directory.
- Group related functionality into modules/folders (e.g., `src/vector-stores`, `src/embeddings`).
- Use `index.ts` files to export public APIs from modules.

### Dependency Management
- Use `pnpm` for package management.
- Keep dependencies up-to-date, checking for compatibility issues.
- Avoid circular dependencies between modules.

### API Design
- Clearly define public APIs exported from the package.
- Use TypeScript interfaces (`interface`) or types (`type`) to define data structures for APIs.
- Maintain backward compatibility where possible or follow a clear deprecation strategy.

### Error Handling
- Use standard JavaScript `Error` objects or custom error classes for specific error conditions.
- Provide meaningful error messages.
- Document potential errors thrown by functions using TSDoc (`@throws`).
