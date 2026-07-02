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

## What kind of changes are welcome

This tool runs against real pentest targets and shells out to `/bin/bash -c`, so contribution scope is intentionally tiered:

### Straightforward — open a PR, no discussion needed
- New entries for `TOOL_NAME_MAP`
- New output formats added *alongside* existing ones (e.g. JSON) — must not change default behavior
- Bug fixes in ANSI/HTML conversion, backed by a real tool-output test case
- Documentation improvements
- Additional test coverage
- New **opt-in** CLI flags that don't change default behavior (e.g. a future `--redact`)
- Packaging (Homebrew formula, pipx, `.deb`, etc.) that doesn't touch the tool itself

### Please open an issue to discuss before submitting a PR
- Any change to `run_command()` or the pty execution path — this is the security-critical core that shells out to bash; changes here need extra scrutiny for injection risk, not just correctness
- Any new external dependency — this project is intentionally pure-stdlib with zero `pip install` requirements, and that's a deliberate design choice, not an oversight
- Changes to *default* behavior: default output format, default metadata fields, filename-based format inference
- Changes to SIGINT / interrupted-run handling

### Out of scope — will not be merged
- Anything that adds network calls, telemetry, or "phone home" behavior of any kind, including "just checking for updates." This tool is used against live pentest targets; silent outbound connections are an opsec problem, not a feature.
- Auto-update or auto-download-and-execute functionality.
- Removing, gating, or making optional the live terminal output streaming — that's the tool's core value and isn't up for negotiation.

## Ideas Welcome

- Additional entries for `TOOL_NAME_MAP`
- JSON output format
- Redaction support for saved logs (opt-in, discuss design first — see scoping above)

## Code Style

- PEP 8.
- No external dependencies unless there's a strong reason — part of this tool's value is that it runs anywhere Python 3 does, with nothing to `pip install`.
