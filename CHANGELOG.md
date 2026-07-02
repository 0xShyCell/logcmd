# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-07-03

### Added
- Initial public release.
- PTY-backed live command execution — full color and interactive output streamed to the terminal in real time while simultaneously captured for logging.
- Three output formats: plain text, Markdown (`.md`/`.markdown`), and HTML (`.html`/`.htm`) with format auto-detected from the output filename's extension.
- ANSI-to-HTML conversion supporting standard 16-color, 256-color (`38/48;5;N`), and 24-bit truecolor (`38/48;2;R;G;B`) SGR sequences.
- Structured metadata per run: timestamp, user@host, cwd, detected tool, detected target IP, exit code, duration, and status (SUCCESS / FAILED / INTERRUPTED).
- Automatic tool-name recognition for 25+ common offensive-security tools (Nmap, NetExec, Hydra, BloodHound, Evil-WinRM, sqlmap, Gobuster, etc.).
- Automatic target IP detection via regex for the `Target:` metadata field.
- Carriage-return collapsing so progress-bar/spinner output renders as its final state in the saved log, not every intermediate frame.
- Graceful SIGINT (Ctrl+C) handling — signal forwarded to the full child process group, run recorded as `INTERRUPTED` rather than silently truncated.
- `--strip-ansi`, `--append`, `--quiet`, `--format`, and `--version` CLI flags.
- Exit code propagation, with `130` returned on interrupted (Ctrl+C) runs per standard shell convention.

### Planned
- JSON output format for programmatic report ingestion.
- Optional automatic redaction of sensitive strings (credentials, session tokens) before saving.
- Session-replay mode (re-render a saved HTML log as an animated terminal playback).
 
