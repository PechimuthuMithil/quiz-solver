# Quiz Solver (TDS P2)

Small toolset to fetch/render web tasks, extract assets (audio/images/files), run bounded Python snippets, analyze media, and optionally publish visualizations to GitHub Pages.

Quick overview
- Core utilities: src/utils/tools.py — helpers for Playwright rendering, download, audio/image processing, executing isolated Python, saving files, and publishing.
- Orchestration: src/tasks/solve.py — uses an LLM orchestrator (via src/utils/aipipe) and the tools to iteratively solve tasks.
- Test page: test/index.html — minimal page used for local render/testing.

Prerequisites
- Python 3.8+
- System packages for audio/image processing (ffmpeg for pydub)
- Node/browser dependencies for Playwright: run `playwright install` after installing Python deps

Install
1. Create and activate a virtualenv (recommended)
2. pip install -r requirements.txt
3. Install Playwright browsers:
   - python -m playwright install

Environment
- GITHUB_TOKEN — required if you want publish_to_github_pages() to create/push a repo and enable GitHub Pages.
- (Optional) Any other secrets used by src/utils/aipipe must be set in the environment as used by that module.

Run / Usage
- The orchestrator expects an LLM integration accessible via src/utils/aipipe.
- Example invocation (from repo root):
  - Import and call solve_task_with_llm(task_url, email, secret) in a small runner or Python REPL.
- For local testing use file:// URLs to pages in test/ (e.g., file://<repo>/test/index.html).

Testing the static preview
- test/index.html is a minimal page that asks the user to "Describe the image".
- The codebase contains a best-effort Playwright render check before publishing gh-pages; Playwright must be available for that check to run.
- You can also follow the steps in `tests/tds-llm-analysis-main/README.md`

Important notes / security
- execute_python_code installs requested packages into an isolated temp target and runs user code with a timeout and restricted file writes (redirected into memory/). This is not a perfect sandbox — review before running untrusted code.
- save_contents_to_file writes only under memory/ (path traversal prevented).
- publish_to_github_pages will create a public repository in the authenticated user's account; ensure GITHUB_TOKEN scope is appropriate.
- Playwright check for index.html is best-effort and may produce false positives for pages expecting network services or auth.

Files of interest
- src/utils/tools.py — main helper functions (rendering, downloads, media handling, publishing)
- src/tasks/solve.py — orchestrates LLM tool-calls and manages the loop & submission logic
- test/index.html — small test page to validate rendering and image description flow

How to contribute
- Create a branch, keep changes minimal, add tests where appropriate, and open a PR.
- Document any new tool function in src/tasks/solve.py tools array (so orchestrator can call it).

Further reading
- See README-Development.md for notes and TODOs maintained by the project.
- See VIVA_Questions.md for a list of viva/practice questions about this repository.
