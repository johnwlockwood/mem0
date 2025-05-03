# Bug Fixing Rules

### Workflow
1.  **Assign & Acknowledge:** Assign the bug ticket to yourself and acknowledge receipt.
2.  **Reproduce:** Follow the steps provided in the bug report to reproduce the issue locally or in a designated testing environment. If reproduction fails, request more information from the reporter.
3.  **Isolate:** Pinpoint the root cause using debugging techniques (refer to `debugging.md`). Understand *why* the bug occurs.
4.  **Fix:** Implement the code changes to resolve the bug. Ensure the fix doesn't introduce regressions.
5.  **Test:**
    *   Write a new test case that specifically targets the bug. This test should fail *before* your fix and pass *after*.
    *   Run all relevant existing tests to check for regressions.
6.  **Document:** Update the bug ticket with details of the fix, including the root cause and the solution implemented. Reference the relevant commit(s).
7.  **Code Review:** Submit the fix for code review, following standard procedures. Clearly explain the bug and the fix in the pull request description.
8.  **Merge & Deploy:** Once approved, merge the fix according to the project's branching strategy and deployment process.
9.  **Verify:** After deployment, verify that the fix works correctly in the target environment (e.g., staging, production). Close the bug ticket.

### Best Practices
*   **Prioritize:** Address critical bugs affecting core functionality or user experience first.
*   **Minimal Change:** Aim for the smallest possible change that effectively fixes the bug without unnecessary refactoring (unless the refactoring is essential to the fix).
*   **Understand Impact:** Consider the potential impact of the fix on other parts of the system.
*   **Communicate:** Keep the bug reporter and relevant stakeholders informed about the progress.
