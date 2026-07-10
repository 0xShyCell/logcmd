# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-07-09

### Added
- Full interactive PTY support: `ftp`, `ssh`, `telnet`, `mysql`, `psql`, `redis-cli`, `gdb`, the Python REPL, `vim`, `nano`, and similar programs now work correctly — previously they would hang after the first prompt since the real terminal's stdin was never forwarded to the child.
- Real stdin is now forwarded to the child's pty with the local terminal in raw mode, enabling byte-perfect passthrough for arrow keys, backspace/line-editing, and password prompts.
- Dynamic terminal resize forwarding — resizing the real terminal window now updates the child's pty size live (`SIGWINCH`), so full-screen apps (`vim`, `gdb`, `hashcat`) redraw correctly.
- Ctrl+C, Ctrl+D, and Ctrl+Z are now forwarded as raw bytes to the child's pty, which generates the correct real signal for the child directly via its own (unmodified) cooked terminal settings — the same mechanism `ssh`/`tmux` use.

### Changed
- "Interrupted" status detection in interactive mode now watches for the real `VINTR` character (read from termios, not hardcoded) in the forwarded input stream, since raw mode means this process no longer receives `SIGINT` directly from the keyboard. Detection semantics ("did the user press Ctrl+C") are unchanged from 1.0.0 — this only changes *how* it's detected.

### Notes
- Fully backward compatible: CLI syntax, flags, output formats, and logging behavior for non-interactive tools (`nmap`, `nxc`, `gobuster`, etc.) are unaffected.
- Piped/non-interactive invocations (stdin not a real tty) continue to use the original 1.0.0 SIGINT-handling path unchanged.
- Known limitation: Ctrl+Z suspends the wrapped child correctly, but does not make the outer `logcmd` process itself a suspended job from the calling shell's perspective (would require job-control proxying between the two pty layers — out of scope).

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
