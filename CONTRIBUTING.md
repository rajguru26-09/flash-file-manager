# Contributing to Flash File Manager

Thanks for collaborating! Please follow these simple guidelines to keep the project healthy and easy to review.

- Fork the repository and create a branch for your work: `git checkout -b feature/short-description`.
- Keep commits small and focused; write clear commit messages.
- Push your branch to your fork and open a Pull Request against `main` (or the default branch).
- Describe the problem, what you changed, and how to test it in the PR description.
- If your change modifies user-facing behavior, include short usage or test steps.

Code quality:

- This project uses the Python standard library; keep dependencies minimal.
- Run a syntax check locally before opening PRs:

```bash
python -m compileall -q .
```

Testing:

- Add unit tests where useful and describe how to run them in the PR.

Communication:

- Tag one of the authors from `AUTHORS` in the PR for review.

Thank you — we appreciate your contributions!
