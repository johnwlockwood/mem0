# Style Guide (TypeScript)

### Formatting
- Follow Prettier configuration defined in `mem0-ts/package.json`.
- Run `pnpm format` or `pnpm format:check` regularly.
- Ensure consistent code style across the TypeScript codebase (`mem0-ts/`, `vercel-ai-sdk/`).

### Naming Conventions
- Use `PascalCase` for types, interfaces, enums, and classes.
- Use `camelCase` for variables, functions, and methods.
- Use `UPPER_SNAKE_CASE` for constants.
- Prefix interfaces with `I` (e.g., `IMemoryData`) if preferred, otherwise use plain `PascalCase`. (Clarify project preference if needed).

### Types & Interfaces
- Prefer `interface` for defining object shapes that might be extended.
- Prefer `type` for unions, intersections, primitives, and utility types.
- Use explicit types; avoid `any` unless absolutely necessary and document the reason.
- Use `readonly` for properties that should not be modified after creation.

### Modules & Imports
- Use ES module syntax (`import`/`export`).
- Organize imports: group by source (standard library, external packages, internal modules). Consider using an import sorter if not handled by Prettier.
- Use relative paths for internal imports within the same package (e.g., `../utils/helpers`).

### Documentation
- Use TSDoc comments for exported functions, classes, types, and interfaces.
  ```typescript
  /**
   * Retrieves memory entries based on the provided query.
   * @param query - The search query string.
   * @param limit - The maximum number of results to return.
   * @returns A promise resolving to an array of memory entries.
   */
  async function searchMemory(query: string, limit: number = 10): Promise<IMemoryEntry[]> {
    // ... implementation
  }
