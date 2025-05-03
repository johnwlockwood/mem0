# Feature Development Rules

### Planning & Design
1.  **Understand Requirements:** Clearly define the feature's goals, scope, and acceptance criteria before starting implementation.
2.  **Design Review:** For significant features, create a brief design document outlining the approach, potential impacts, and alternatives. Discuss this with the team.
3.  **Break Down Tasks:** Divide the feature into smaller, manageable tasks or user stories.

### Implementation
1.  **Branching:** Create a dedicated feature branch from the main development branch (e.g., `main` or `develop`). Use a clear naming convention (e.g., `feat/add-user-authentication`).
2.  **Follow Project Rules:** Adhere strictly to the rules defined in `architecture.md`, `style.md`, and `testing.md`.
3.  **Incremental Commits:** Make small, logical commits using conventional commit messages (see `style.md`).
4.  **Code Quality:** Ensure code is clean, readable, and maintainable. Run linters and formatters (`ruff`, `isort`) frequently.

### Testing
1.  **Unit Tests:** Write comprehensive unit tests covering the new logic. Aim for high coverage as specified in `testing.md`.
2.  **Integration Tests:** Add integration tests if the feature interacts with other components or external services.
3.  **End-to-End Tests (If Applicable):** Consider adding E2E tests for critical user flows.
4.  **Manual Testing:** Perform manual testing to catch issues not covered by automated tests.

### Documentation
1.  **Code Documentation:** Add or update docstrings and comments as needed (see `style.md`).
2.  **User Documentation:** Update user-facing documentation (e.g., `docs/`) if the feature changes how users interact with the system.
3.  **API Documentation:** Update API specifications (e.g., OpenAPI, GraphQL schema) if the feature modifies APIs.

### Code Review & Merging
1.  **Pull Request:** Create a pull request (PR) targeting the main development branch. Include a clear description of the feature, changes made, and how to test it. Link relevant tickets or issues.
2.  **Address Feedback:** Respond to code review comments and make necessary revisions.
3.  **Merge:** Once approved and all checks pass, merge the PR according to the project's strategy (e.g., squash and merge, rebase and merge).
