# Debugging Rules

### Logging
- Use the standard Python `logging` module configured project-wide.
- Log levels:
    - `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
    - `INFO`: Confirmation that things are working as expected.
    - `WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
    - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
    - `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.
- Include contextual information in log messages (e.g., user ID, request ID, relevant data IDs).
- Avoid logging sensitive information (passwords, API keys, PII).

### Troubleshooting Workflow
1. **Reproduce the issue:** Consistently reproduce the bug in a controlled environment (local or staging).
2. **Isolate the cause:** Use logging, debugging tools (like `pdb` or IDE debuggers), and code inspection to pinpoint the root cause.
3. **Consult logs:** Check application logs, system logs, and any relevant third-party service logs for errors or warnings related to the issue.
4. **Simplify the scenario:** If possible, reduce the complexity of the test case to isolate the failing component.
5. **Verify assumptions:** Double-check assumptions about data, state, and external system behavior.

### Debugging Tools
- Utilize IDE debugging features (breakpoints, stepping, variable inspection).
- Use `pdb` or `ipdb` for command-line debugging when necessary.
- Leverage browser developer tools for frontend debugging (if applicable).
