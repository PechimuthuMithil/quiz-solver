# Quiz Solver (TDS P2)

Small toolset to fetch/render web tasks, extract assets (audio/images/files), run bounded Python snippets, analyze media, and optionally publish visualizations to GitHub Pages.

## Waking up or testing the render deployemnt
Submit a query with invalid secret
### On Windows
```sh
Invoke-RestMethod `
  -Uri "https://quiz-solver-0j5p.onrender.com/start-solve" `
  -Method Post `
  -ContentType "application/json" `
  -Body (
    @{
      email  = "21f3001995@ds.study.iitm.ac.in"
      secret = "1234"
      url    = "https://tds-llm-analysis.s-anand.net/project2"
    } | ConvertTo-Json
  )
```

### On Linux kernels (curl)
```sh
 curl -X POST "https://quiz-solver-0j5p.onrender.com/start-solve" \
            -H "Content-Type: application/json" \
            -i \
            -d '{
        "email": "21f3001995@ds.study.iitm.ac.in",
        "secret": "1234",
        "url": "https://tds-llm-analysis.s-anand.net/project2"
    }'
```


## Querying the render deployment 
(The orchestrator will be xai/grok-4.1-fast)
### On Windows
```sh
Invoke-RestMethod `
  -Uri "https://quiz-solver-0j5p.onrender.com/start-solve" `
  -Method Post `
  -ContentType "application/json" `
  -Body (
    @{
      email  = "21f3001995@ds.study.iitm.ac.in"
      secret = "the secret"
      url    = "the start url goes here"
    } | ConvertTo-Json
  )
```

### On Linux kernels (curl)
```sh
curl -X POST "https://quiz-solver-0j5p.onrender.com/start-solve" \
      -H "Content-Type: application/json" \
      -i \
      -d '{
      "email": "21f3001995@ds.study.iitm.ac.in",
      "secret": "the secret",
      "url": "the start url goes here"
  }'
```
### Querying local deployment
(The orchestrator will be mostly kwaipilot/kat-coder-pro:free, as it is free and will be used in case of limit exhaustion)
### On Windows
```sh
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/start-solve" `
  -Method Post `
  -ContentType "application/json" `
  -Body (
    @{
      email  = "21f3001995@ds.study.iitm.ac.in"
      secret = "the secret"
      url    = "the start url goes here"
    } | ConvertTo-Json
  )
```

### On Linux kernels (curl)
```sh
curl -X POST "http://127.0.0.1:8000/start-solve" \
      -H "Content-Type: application/json" \
      -i \
      -d '{
      "email": "21f3001995@ds.study.iitm.ac.in",
      "secret": "the secret",
      "url": "the start url goes here"
  }'
```

## Quick Overview
- Core utilities: `src/utils/tools.py` — helpers for Playwright rendering, download, audio/image processing, executing isolated Python, saving files, and publishing.
- Orchestration: `src/tasks/solve.py` — uses an LLM orchestrator (via `src/utils/aipipe`) and the tools to iteratively solve tasks.
- Test page: `test/index.html` — minimal page used for local render/testing.

## Architecture
The system is designed as a modular pipeline:
1. **Task Orchestration**: 
   - The orchestrator (`src/tasks/solve.py`) acts as the central controller, leveraging an LLM to parse tasks, plan tool usage, and iteratively solve problems.
   - Tools are exposed as callable functions with strict parameter schemas.
2. **Toolset**:
   - Tools in `src/utils/tools.py` handle specific subtasks like fetching HTML, downloading files, processing audio, analyzing images, and executing Python code.
   - Each tool is designed to be stateless and reusable.
3. **LLM Integration**:
   - The orchestrator communicates with an LLM via `src/utils/aipipe` to interpret tasks and generate tool calls.
   - The LLM is guided by strict instructions to minimize unnecessary calls and optimize task-solving efficiency.
4. **Output Handling**:
   - Results are saved to a memory directory (`memory/`) for intermediate processing.
   - Final outputs can be published to GitHub Pages for visualization.

## Models Used
- **LLM Orchestrator**:
  - The system relies on a large language model (LLM) to interpret tasks, plan tool usage, and refine answers iteratively.
  - The LLM is accessed via the `aipipe` module, which abstracts the communication layer.
- **Image and Audio Processors**:
  - Image analysis and audio transcription tasks are delegated to specialized AI models via `aipipe`.
  - These models are optimized for tasks like object recognition, transcription, and answering specific queries about media content.

## Tricks, Retries, and Fallbacks
### Retries and Fallbacks
- **Submission Retries**:
  - If `submit_answer` fails with a 400 status code, the system retries up to 2 times with the same parameters before refining the approach.
  - For numeric answers, the system tries a range of values around the predicted answer (e.g., ±10) to account for minor errors.
- **Fallback Submission URL**:
  - If the provided `submit_url` fails, a fallback URL is constructed from the task URL and used for submission.
- **Timeout Handling**:
  - If the task exceeds the maximum allowed time, the system extracts the `submit_url` and submits a dummy answer to ensure graceful termination.

### Tricks and Optimizations
- **Tool Call Minimization**:
  - The LLM is instructed to minimize redundant tool calls by caching results and reusing them when possible.
- **Sandboxed Python Execution**:
  - Python code execution is sandboxed to prevent unauthorized file writes and ensure safe package installation in isolated environments.
- **Dynamic URL Resolution**:
  - Relative URLs in HTML content are resolved to absolute URLs to ensure accurate resource fetching.
- **Memory Cleanup**:
  - Temporary files in the `memory/` directory are cleaned up after task completion to prevent clutter and ensure security.
- **GitHub Pages Deployment**:
  - Visualizations are published to GitHub Pages by creating a temporary repository and pushing to the `gh-pages` branch.

## Prerequisites
- Python 3.8+
- System packages for audio/image processing (e.g., `ffmpeg` for `pydub`)
- Node/browser dependencies for Playwright: run `playwright install` after installing Python dependencies.

## Install
(Can follow the `Dockerfile` for more information)
1. Create and activate a virtual environment (recommended).
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   python -m playwright install
   ```

## Environment
- `GITHUB_TOKEN` — required if you want `publish_to_github_pages()` to create/push a repo and enable GitHub Pages.
- (Optional) Any other secrets used by `src/utils/aipipe` must be set in the environment as used by that module.

## Run / Usage
- The orchestrator expects an LLM integration accessible via `src/utils/aipipe`.
- Example invocation (from repo root):
  - Import and call `solve_task_with_llm(task_url, email, secret)` in a small runner or Python REPL.
- For local testing, use `file://` URLs to pages in `test/` (e.g., `file://<repo>/test/index.html`).

## Testing the Static Preview
- `test/index.html` is a minimal page that asks the user to "Describe the image."
- The codebase contains a best-effort Playwright render check before publishing to GitHub Pages; Playwright must be available for that check to run.
- You can also follow the steps in `tests/tds-llm-analysis-main/README.md`.

## Important Notes / Security
- `execute_python_code` installs requested packages into an isolated temp target and runs user code with a timeout and restricted file writes (redirected into `memory/`). This is not a perfect sandbox — review before running untrusted code.
- `save_contents_to_file` writes only under `memory/` (path traversal prevented).
- `publish_to_github_pages` will create a public repository in the authenticated user's account; ensure `GITHUB_TOKEN` scope is appropriate.
- Playwright check for `index.html` is best-effort and may produce false positives for pages expecting network services or authentication.

## Files of Interest
- `src/utils/tools.py` — main helper functions (rendering, downloads, media handling, publishing).
- `src/tasks/solve.py` — orchestrates LLM tool-calls and manages the loop & submission logic.
- `test/index.html` — small test page to validate rendering and image description flow.

## How to Contribute
- Create a branch, keep changes minimal, add tests where appropriate, and open a PR.
- Document any new tool function in `src/tasks/solve.py` tools array (so the orchestrator can call it).

## Further Reading
- See `README-Development.md` for notes and TODOs maintained by the project.
- See `VIVA_Questions.md` for a list of viva/practice questions about this repository.
