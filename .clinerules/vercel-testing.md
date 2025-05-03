# Testing Rules (Vercel AI SDK)

### Framework
- Use Jest for all unit and integration tests in TypeScript projects (`mem0-ts/`, `vercel-ai-sdk/`).
- Configure Jest via `jest.config.js`.

### Test Structure
- Place test files alongside the code they test, or in a dedicated `__tests__` directory.
- Use the `.test.ts` or `.spec.ts` suffix for test files.
- Follow the Arrange-Act-Assert (AAA) pattern:
  ```typescript
  describe('MyComponent', () => {
    it('should perform an action correctly', () => {
      // Arrange: Set up mocks, data, and component instances
      const mockService = { fetchData: jest.fn().mockResolvedValue('mock data') };
      const component = new MyComponent(mockService);

      // Act: Call the method or trigger the behavior being tested
      const result = await component.loadData();

      // Assert: Verify the outcome, mock calls, and state changes
      expect(mockService.fetchData).toHaveBeenCalledTimes(1);
      expect(result).toBe('mock data');
      expect(component.data).toBe('mock data');
    });
  });
  ```

### Mocking
- Use `jest.fn()` for simple function mocks.
- Use `jest.mock()` for module mocking.
- Clearly document mocks and their expected behavior.

### Coverage
- Aim for high test coverage, especially for critical logic.
- Use Jest's coverage reporting (`--coverage`) to identify untested code paths.
- Strive to meet or exceed the project's overall coverage goals (refer to Python testing rules for general targets if applicable).
