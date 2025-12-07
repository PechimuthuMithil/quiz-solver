# VIVA / Practice Questions — Quiz Solver Project

Sections:
- Architecture & purpose
- Core modules & functions
- Tooling & third-party deps
- Security & sandboxing
- Testing, debugging & deployment
- Advanced / design choices

Architecture & purpose
1. What is the primary goal of this repository?
2. Describe the high-level data flow from receiving a task URL to submitting an answer.
3. What role does the LLM play versus the local utilities?

Core modules & functions
4. What are the main responsibilities of src/utils/tools.py?
5. Explain how get_html_content works and why Playwright is used.
6. How does download_file_from_url handle file:// URLs differently from http(s)?
7. What does execute_python_code do to limit filesystem writes?
8. How does save_contents_to_file prevent path traversal?
9. What is the purpose of analyse_image_to_text and process_audio_url?
10. Describe publish_to_github_pages: steps it takes and required environment variables.

Tooling & third-party dependencies
11. Why is Playwright required and what extra step is needed after pip install?
12. What system utilities might pydub require to function properly?
13. Why are temporary directories used in execute_python_code and publish_to_github_pages?

Security & sandboxing
14. How is arbitrary Python execution limited? What are the remaining risks?
15. Explain the file write restrictions imposed by restricted_open in execute_python_code.
16. Why should GITHUB_TOKEN be used with care and limited scope?
17. What kinds of false-positives might the Playwright render check produce?

Testing, debugging & deployment
18. How would you test the Playwright render check locally?
19. How can you validate that save_contents_to_file wrote the intended file?
20. Describe steps to reproduce a publish_to_github_pages failure and how to debug it.
21. How does the orchestrator loop in src/tasks/solve.py decide when to stop?

Advanced / design choices
22. Why prefer execute_python_code for heavy file processing instead of sending files to the LLM?
23. Explain the reasoning behind storing outputs under memory/ and cleaning them up.
24. When would you prefer to bypass the Playwright check before publishing?
25. Discuss trade-offs of trying to auto-create a GitHub repo for each publish attempt.

Edge cases & failure modes
26. What happens if Playwright is installed but browsers are not?
27. How does the code handle failed downloads or network timeouts?
28. What are potential issues when running index.html that expects remote APIs?
29. How would you handle tasks that require authentication to fetch assets?

Improvements & future work
30. Suggest three improvements to make execute_python_code safer.
31. How would you add unit tests for save_contents_to_file?
32. Propose a way for the Playwright render check to better simulate a production environment (e.g., mock network responses).

Practical questions to demonstrate code knowledge
33. Walk through the code path when the LLM asks to save a visualization and publish it.
34. Show how you would instrument more logging for publish_to_github_pages.
35. If asked in a viva: explain how you would add a feature to preview deploys privately (not public gh-pages).

Use these questions for quick oral practice. Prepare concrete examples from the codebase to illustrate answers during the viva.

Why did I use Grok as the orchestrator and not gpt-4o-mini? Because grok 4.1 was free and had a huge context length.
Why have so many tools and not just leverage python execution for everything? Somethings need to be reliable and python execution was for lightweight to medium execution and computations. 
