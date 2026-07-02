# Contributing to logcmd

This started as a personal tool for logging pentest command output cleanly, but issues and pull requests are welcome.

## Reporting Issues

Open a GitHub Issue with:
- OS and shell (e.g. Kali Linux / bash, macOS / zsh)
- The exact command you passed to `logcmd`
- Expected vs. actual behavior
- The relevant portion of the saved log (redact anything sensitive — IPs, credentials, hostnames)

## Submitting Changes

1. Fork the repo and create a branch: `git checkout -b feature/your-feature-name`
2. Keep to the existing style — PEP 8, and match the existing docstring/comment density (this is a security tool; readability matters more than brevity).
3. If you touch `ansi_to_html`, `render_*`, or the metadata builder, test against real tool output (nmap, nxc, gobuster) before submitting — ANSI parsing edge cases are easy to get subtly wrong.
4. Update `CHANGELOG.md` under an `[Unreleased]` heading.
5. Open a pull request describing what changed and why.

## Ideas Welcome

- Additional entries for `TOOL_NAME_MAP`
- JSON output format
- Redaction support for saved logs

## Code Style

- PEP 8.
- No external dependencies unless there's a strong reason — part of this tool's value is that it runs anywhere Python 3 does, with nothing to `pip install`.
