#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool: logcmd - Professional Command Logging Utility
================================================

Purpose
-------
Execute any shell command while:
  * Displaying its output live in the terminal (colors preserved).
  * Saving a clean, report-ready log to a file with execution metadata
    (timestamp, user, host, cwd, command, duration, exit code).
  * Supporting plain text, Markdown, or color-preserving HTML output.
  * Handling Ctrl+C gracefully and recording interrupted runs.

Designed for penetration testing, red teaming, OSCP labs, HTB/THM boxes,
and professional security assessment reporting, where every command run
against a target needs a timestamped, attributable, reproducible record.

Author
------
Anand Sharma (0xShyCell)

GitHub
------
https://github.com/0xShyCell/logcmd

License
-------
MIT

Usage
-----
    logcmd "<command>" <output_file> [options]

Examples
--------
    logcmd "nxc smb 10.211.11.10 -u '' -p '' --shares" nxc.txt
    logcmd "nmap -sV -p- 10.211.11.10" nmap.txt
    logcmd "enum4linux-ng -A 10.211.11.10" enum4linux.html --format html
    logcmd "gobuster dir -u http://10.211.11.10 -w /usr/share/wordlists/dirb/common.txt" gobuster.md
    logcmd "cat /etc/passwd | grep -i bash" loot.txt --strip-ansi
    logcmd "hydra -l admin -P rockyou.txt ssh://10.211.11.10" hydra.txt --append

Installation
------------
    chmod +x logcmd.py
    sudo cp logcmd.py /usr/local/bin/logcmd

Notes
-----
* Commands are executed via `/bin/bash -c "<command>"` inside a pseudo
  terminal (pty), so pipes, redirects, quoting, subshells, and any other
  shell syntax behave exactly as they would in an interactive terminal.
  This also means the tool that owns the colorized output (nmap, nxc,
  enum4linux-ng, gobuster, etc.) believes it is attached to a real tty
  and emits ANSI color codes as normal -- which is how colors are
  preserved both live and in the saved log.
* Only the LOG FILE content is reformatted (metadata header/footer,
  carriage-return collapsing, optional ANSI stripping, format
  conversion). The LIVE terminal output is streamed completely
  untouched and in real time.
"""

import argparse
import fcntl
import getpass
import html
import os
import pty
import re
import select
import shlex
import shutil
import signal
import socket
import struct
import subprocess
import sys
import termios
import time
from datetime import datetime

# --------------------------------------------------------------------------- #
# Constants / lookup tables
# --------------------------------------------------------------------------- #

VERSION = "1.0.0"

SEPARATOR = "=" * 60

# Cosmetic display-name lookup only — does NOT imply every tool listed here
# has been verified end-to-end. logcmd works with any shell command
# generically; this map just makes the "Tool:" metadata field readable
# for commonly used offensive-security tools.

TOOL_NAME_MAP = {
    "nxc": "NetExec",
    "netexec": "NetExec",
    "crackmapexec": "CrackMapExec",
    "cme": "CrackMapExec",
    "nmap": "Nmap",
    "masscan": "Masscan",
    "enum4linux-ng": "Enum4linux-ng",
    "enum4linux": "Enum4linux",
    "gobuster": "Gobuster",
    "ffuf": "ffuf",
    "feroxbuster": "Feroxbuster",
    "smbclient": "smbclient",
    "smbmap": "smbmap",
    "hydra": "Hydra",
    "sqlmap": "sqlmap",
    "hashcat": "Hashcat",
    "john": "John the Ripper",
    "responder": "Responder",
    "bloodhound-python": "BloodHound",
    "bloodhound-ce-python": "BloodHound CE",
    "impacket-secretsdump": "secretsdump",
    "impacket-psexec": "psexec",
    "impacket-wmiexec": "wmiexec",
    "evil-winrm": "Evil-WinRM",
    "nikto": "Nikto",
    "wpscan": "WPScan",
    "whatweb": "WhatWeb",
    "searchsploit": "SearchSploit",
    "msfconsole": "Metasploit",
}

IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# Matches a full ANSI/VT100 escape sequence (used for full stripping).
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Matches CSI sequences that are NOT an SGR (color/style) sequence, i.e.
# anything that doesn't end in 'm' (cursor movement, clear-line, etc).
# These have no HTML equivalent and are dropped during HTML conversion.
ANSI_NON_SGR_RE = re.compile(r"\x1B\[[0-9;?]*[A-Za-ln-zA-LN-Z]")

# Standard 16-color terminal palette (approximation of common terminal themes).
FG_COLORS = {
    30: "#000000", 31: "#e06c75", 32: "#98c379", 33: "#e5c07b",
    34: "#61afef", 35: "#c678dd", 36: "#56b6c2", 37: "#dcdfe4",
    90: "#5c6370", 91: "#ff6b6b", 92: "#b5e890", 93: "#f0d878",
    94: "#82b8ff", 95: "#e0a0ff", 96: "#7fdbe0", 97: "#ffffff",
}
BG_COLORS = {code + 10: color for code, color in FG_COLORS.items()}


# --------------------------------------------------------------------------- #
# Command execution (pty-backed, live + captured)
# --------------------------------------------------------------------------- #

def get_term_size():
    """Return (rows, cols) of the controlling terminal, with a safe fallback."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.lines, size.columns


def run_command(command):
    """
    Execute `command` through `/bin/bash -c` inside a pseudo-terminal.

    Running inside a pty (rather than a plain pipe) makes the invoked
    program believe it has a real terminal attached, which is what causes
    tools like nmap/nxc/gobuster to emit ANSI colors and live progress
    output in the first place. The pty's master side is read in a loop:
    every chunk read is written straight to the real stdout (so the user
    sees live output exactly as if they had run the command directly) and
    is also appended to an in-memory buffer for later logging.

    Returns:
        (raw_output: bytes, exit_code: int, interrupted: bool)
    """
    master_fd, slave_fd = pty.openpty()

    # Match the real terminal's window size so full-screen / progress-bar
    # tools (e.g. nmap with --stats-every, hashcat) render correctly.
    try:
        rows, cols = get_term_size()
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
    except OSError:
        pass

    proc = subprocess.Popen(
        ["/bin/bash", "-c", command],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        preexec_fn=os.setsid,   # own process group, so Ctrl+C can target the whole pipeline
        close_fds=True,
    )
    os.close(slave_fd)

    output_chunks = []
    interrupted = {"flag": False}

    def handle_sigint(signum, frame):
        """On Ctrl+C, forward SIGINT to the child's whole process group
        (so piped commands like `cmd1 | cmd2` are stopped together) and
        flag the run as interrupted for the log footer."""
        interrupted["flag"] = True
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        except (ProcessLookupError, OSError):
            pass

    old_handler = signal.signal(signal.SIGINT, handle_sigint)

    try:
        while True:
            if proc.poll() is not None:
                # Process has exited -- drain any remaining buffered bytes.
                while True:
                    try:
                        ready, _, _ = select.select([master_fd], [], [], 0)
                    except (InterruptedError, OSError):
                        break
                    if not ready:
                        break
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    output_chunks.append(data)
                    os.write(1, data)
                break

            try:
                ready, _, _ = select.select([master_fd], [], [], 0.2)
            except InterruptedError:
                continue
            except OSError:
                break

            if master_fd in ready:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                output_chunks.append(data)
                os.write(1, data)
    finally:
        signal.signal(signal.SIGINT, old_handler)
        try:
            os.close(master_fd)
        except OSError:
            pass

    exit_code = proc.wait()
    return b"".join(output_chunks), exit_code, interrupted["flag"]


# --------------------------------------------------------------------------- #
# Output post-processing
# --------------------------------------------------------------------------- #

def collapse_carriage_returns(text):
    """
    Collapse in-place terminal overwrites (lines containing a lone '\\r',
    used by progress bars / spinners in tools like nmap, hashcat, hydra)
    down to their final rendered state, so the saved log shows one clean
    line per logical update instead of every intermediate frame.
    """
    cleaned_lines = []
    for line in text.split("\n"):
        if "\r" in line:
            line = line.split("\r")[-1]
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def normalize_output(raw_bytes):
    """Decode raw terminal bytes and normalize line endings for logging."""
    text = raw_bytes.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n")
    text = collapse_carriage_returns(text)
    return text.strip("\n")


def strip_ansi(text):
    """Remove all ANSI/VT100 escape sequences from text."""
    return ANSI_ESCAPE_RE.sub("", text)


# --------------------------------------------------------------------------- #
# ANSI -> HTML conversion (preserves colors for the HTML report format)
# --------------------------------------------------------------------------- #

def xterm256_to_hex(n):
    """Approximate conversion of an xterm 256-color index to a hex color."""
    basic16 = [
        0x000000, 0x800000, 0x008000, 0x808000, 0x000080, 0x800080, 0x008080, 0xc0c0c0,
        0x808080, 0xff0000, 0x00ff00, 0xffff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffffff,
    ]
    if n < 16:
        return f"#{basic16[n]:06x}"
    if n < 232:
        n -= 16
        levels = [0, 95, 135, 175, 215, 255]
        r, g, b = levels[n // 36], levels[(n % 36) // 6], levels[n % 6]
        return f"#{r:02x}{g:02x}{b:02x}"
    gray = 8 + (n - 232) * 10
    return f"#{gray:02x}{gray:02x}{gray:02x}"


def ansi_to_html(text):
    """
    Convert a string containing ANSI SGR (color/style) escape codes into
    HTML with inline <span style="..."> elements, preserving the original
    terminal colors. Supports standard 16 colors, bright 16 colors,
    256-color (38/48;5;N), and 24-bit truecolor (38/48;2;R;G;B) sequences.
    Non-SGR CSI sequences (cursor movement, clear-line, etc.) are stripped
    since they have no meaningful HTML equivalent.
    """
    text = ANSI_NON_SGR_RE.sub("", text)

    out = []
    open_span = False
    style = {"color": None, "background": None, "bold": False, "underline": False}

    def close_span():
        nonlocal open_span
        if open_span:
            out.append("</span>")
            open_span = False

    def open_span_if_styled():
        nonlocal open_span
        css = []
        if style["color"]:
            css.append(f"color:{style['color']}")
        if style["background"]:
            css.append(f"background-color:{style['background']}")
        if style["bold"]:
            css.append("font-weight:bold")
        if style["underline"]:
            css.append("text-decoration:underline")
        if css:
            out.append(f'<span style="{";".join(css)}">')
            open_span = True

    pos = 0
    for match in re.finditer(r"\x1B\[([0-9;]*)m", text):
        chunk = text[pos:match.start()]
        if chunk:
            out.append(html.escape(chunk))
        pos = match.end()

        raw_codes = [c for c in match.group(1).split(";") if c != ""]
        codes = [int(c) for c in raw_codes] if raw_codes else [0]

        close_span()
        i = 0
        while i < len(codes):
            code = codes[i]
            if code == 0:
                style = {"color": None, "background": None, "bold": False, "underline": False}
            elif code == 1:
                style["bold"] = True
            elif code == 4:
                style["underline"] = True
            elif code == 22:
                style["bold"] = False
            elif code == 24:
                style["underline"] = False
            elif code == 39:
                style["color"] = None
            elif code == 49:
                style["background"] = None
            elif code == 38 and i + 1 < len(codes):
                if codes[i + 1] == 5 and i + 2 < len(codes):
                    style["color"] = xterm256_to_hex(codes[i + 2])
                    i += 2
                elif codes[i + 1] == 2 and i + 4 < len(codes):
                    r, g, b = codes[i + 2:i + 5]
                    style["color"] = f"#{r:02x}{g:02x}{b:02x}"
                    i += 4
            elif code == 48 and i + 1 < len(codes):
                if codes[i + 1] == 5 and i + 2 < len(codes):
                    style["background"] = xterm256_to_hex(codes[i + 2])
                    i += 2
                elif codes[i + 1] == 2 and i + 4 < len(codes):
                    r, g, b = codes[i + 2:i + 5]
                    style["background"] = f"#{r:02x}{g:02x}{b:02x}"
                    i += 4
            elif code in FG_COLORS:
                style["color"] = FG_COLORS[code]
            elif code in BG_COLORS:
                style["background"] = BG_COLORS[code]
            i += 1
        open_span_if_styled()

    out.append(html.escape(text[pos:]))
    close_span()
    return "".join(out)


# --------------------------------------------------------------------------- #
# Metadata extraction
# --------------------------------------------------------------------------- #

def detect_tool(command):
    """Best-effort extraction of the primary tool name from the command,
    for a clean 'Tool:' metadata field. Falls back to the raw binary name."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return None

    first = os.path.basename(tokens[0])
    # Skip past common privilege-escalation/interpreter prefixes.
    skip_prefixes = {"sudo", "doas", "python3", "python", "bash", "sh"}
    idx = 0
    while first in skip_prefixes and idx + 1 < len(tokens):
        idx += 1
        first = os.path.basename(tokens[idx])

    return TOOL_NAME_MAP.get(first, first)


def detect_target(command):
    """Best-effort extraction of a target IP address from the command,
    for a clean 'Target:' metadata field."""
    match = IP_RE.search(command)
    return match.group(0) if match else None


def build_metadata(command, start_dt, duration, exit_code, interrupted):
    """Assemble the full metadata dictionary used by every report format."""
    tz = time.strftime("%Z")
    timestamp = start_dt.strftime("%Y-%m-%d %H:%M:%S") + (f" {tz}" if tz else "")

    if interrupted:
        status = "INTERRUPTED (Ctrl+C)"
    elif exit_code == 0:
        status = "SUCCESS"
    else:
        status = "FAILED"

    return {
        "timestamp": timestamp,
        "user": getpass.getuser(),
        "hostname": socket.gethostname(),
        "cwd": os.getcwd(),
        "command": command,
        "tool": detect_tool(command),
        "target": detect_target(command),
        "exit_code": exit_code,
        "duration": f"{duration:.2f}s",
        "status": status,
    }


# --------------------------------------------------------------------------- #
# Report rendering (plain / markdown / html)
# --------------------------------------------------------------------------- #

def render_plain(meta, output_text):
    """Render a concise, professional plain-text report (matches the
    classic pentest log style: header, raw output, footer)."""
    header = [SEPARATOR, f"Timestamp : {meta['timestamp']}",
              f"User      : {meta['user']}@{meta['hostname']}",
              f"CWD       : {meta['cwd']}"]
    if meta["tool"]:
        header.append(f"Tool      : {meta['tool']}")
    if meta["target"]:
        header.append(f"Target    : {meta['target']}")
    header.append(f"Command   : {meta['command']}")
    header.append(SEPARATOR)

    footer = [SEPARATOR,
              f"Exit Code : {meta['exit_code']}",
              f"Duration  : {meta['duration']}",
              f"Status    : {meta['status']}",
              SEPARATOR]

    return "\n".join(header) + "\n\n" + output_text.rstrip("\n") + "\n\n" + "\n".join(footer) + "\n"


def render_markdown(meta, output_text):
    """Render a Markdown report. ANSI codes are always stripped here since
    Markdown viewers don't reliably render terminal color escapes."""
    title = f"# Command Log{': ' + meta['tool'] if meta['tool'] else ''}"
    rows = [
        ("Timestamp", meta["timestamp"]),
        ("User", f"{meta['user']}@{meta['hostname']}"),
        ("CWD", f"`{meta['cwd']}`"),
    ]
    if meta["tool"]:
        rows.append(("Tool", meta["tool"]))
    if meta["target"]:
        rows.append(("Target", meta["target"]))
    rows.append(("Command", f"`{meta['command']}`"))
    rows.append(("Exit Code", str(meta["exit_code"])))
    rows.append(("Duration", meta["duration"]))
    rows.append(("Status", meta["status"]))

    table = ["| Field | Value |", "|---|---|"]
    table.extend(f"| {field} | {value} |" for field, value in rows)

    clean_output = strip_ansi(output_text).rstrip("\n")

    parts = [title, "", *table, "", "```text", clean_output, "```", ""]
    return "\n".join(parts)


def render_html(meta, output_text, keep_colors):
    """Render a self-contained HTML report. Preserves ANSI colors as
    inline-styled spans unless `keep_colors` is False."""
    body = ansi_to_html(output_text) if keep_colors else html.escape(strip_ansi(output_text))

    extra_rows = ""
    if meta["tool"]:
        extra_rows += f"<tr><th>Tool</th><td>{html.escape(meta['tool'])}</td></tr>\n"
    if meta["target"]:
        extra_rows += f"<tr><th>Target</th><td>{html.escape(meta['target'])}</td></tr>\n"

    title = html.escape(meta["command"])
    heading_tool = f": {html.escape(meta['tool'])}" if meta["tool"] else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Command Log - {title}</title>
<style>
  body {{
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    padding: 24px;
    font-size: 14px;
  }}
  h2 {{ color: #ffffff; margin-bottom: 16px; }}
  table {{ border-collapse: collapse; margin-bottom: 18px; }}
  th, td {{ border: 1px solid #3c3c3c; padding: 6px 14px; text-align: left; }}
  th {{ background: #2d2d2d; color: #9cdcfe; width: 140px; }}
  code {{ color: #ce9178; }}
  pre {{
    background: #000000;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.4;
  }}
  .footer {{ margin-top: 14px; color: #9cdcfe; }}
  .footer span {{ color: #d4d4d4; }}
</style>
</head>
<body>
<h2>Command Log{heading_tool}</h2>
<table>
  <tr><th>Timestamp</th><td>{html.escape(meta['timestamp'])}</td></tr>
  <tr><th>User</th><td>{html.escape(meta['user'])}@{html.escape(meta['hostname'])}</td></tr>
  <tr><th>CWD</th><td><code>{html.escape(meta['cwd'])}</code></td></tr>
  {extra_rows}<tr><th>Command</th><td><code>{title}</code></td></tr>
</table>
<pre>{body}</pre>
<div class="footer">
  Exit Code: <span>{meta['exit_code']}</span> &nbsp;|&nbsp;
  Duration: <span>{meta['duration']}</span> &nbsp;|&nbsp;
  Status: <span>{html.escape(meta['status'])}</span>
</div>
</body>
</html>
"""


def render_report(meta, output_text, fmt, strip_colors):
    """Dispatch to the correct renderer based on the chosen format."""
    if fmt == "markdown":
        return render_markdown(meta, output_text)
    if fmt == "html":
        return render_html(meta, output_text, keep_colors=not strip_colors)
    # plain
    text = strip_ansi(output_text) if strip_colors else output_text
    return render_plain(meta, text)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser():
    parser = argparse.ArgumentParser(
        prog="logcmd",
        description="Professional command logging utility for pentesting, "
                     "red teaming, and security assessment reporting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  logcmd "nxc smb 10.211.11.10 -u '' -p '' --shares" nxc.txt
  logcmd "nmap -sV -p- 10.211.11.10" nmap.txt
  logcmd "enum4linux-ng -A 10.211.11.10" enum4linux.html --format html
  logcmd "gobuster dir -u http://10.211.11.10 -w wordlist.txt" gobuster.md
  logcmd "cat /etc/passwd | grep -i bash" loot.txt --strip-ansi
  logcmd "hydra -l admin -P rockyou.txt ssh://10.211.11.10" hydra.txt --append

Notes:
  * Quote the full command as a single argument so pipes, redirects, and
    quoted flags (e.g. -u '' -p '') are passed through to bash correctly.
  * Output format defaults to: .md/.markdown -> markdown, .html/.htm -> html,
    anything else -> plain. Override with --format.
""",
    )
    parser.add_argument("command", help="Full command to execute (quote it as one argument)")
    parser.add_argument("output", help="File to save the log to")
    parser.add_argument("-f", "--format", choices=["plain", "markdown", "html"], default=None,
                         help="Output format (default: inferred from the output file extension)")
    parser.add_argument("--strip-ansi", action="store_true",
                         help="Strip ANSI color codes from the SAVED log file "
                              "(live terminal output is always shown in color)")
    parser.add_argument("-a", "--append", action="store_true",
                         help="Append to the output file instead of overwriting it")
    parser.add_argument("-q", "--quiet", action="store_true",
                         help="Suppress the final summary line printed after execution")
    parser.add_argument("-V", "--version", action="version", version=f"logcmd {VERSION}")
    return parser


def resolve_format(args):
    """Determine the output format: explicit --format wins, otherwise infer
    it from the output file's extension, defaulting to plain text."""
    if args.format:
        return args.format
    ext = os.path.splitext(args.output)[1].lower()
    if ext in (".md", ".markdown"):
        return "markdown"
    if ext in (".html", ".htm"):
        return "html"
    return "plain"


def main():
    parser = build_parser()
    args = parser.parse_args()

    fmt = resolve_format(args)

    start_dt = datetime.now()
    start_perf = time.perf_counter()

    raw_output, exit_code, interrupted = run_command(args.command)

    duration = time.perf_counter() - start_perf
    output_text = normalize_output(raw_output)
    meta = build_metadata(args.command, start_dt, duration, exit_code, interrupted)
    content = render_report(meta, output_text, fmt, args.strip_ansi)

    mode = "a" if args.append else "w"
    try:
        with open(args.output, mode, encoding="utf-8") as f:
            if args.append and os.path.getsize(args.output) > 0 if os.path.exists(args.output) else False:
                f.write("\n")
            f.write(content)
    except OSError as e:
        print(f"\n[!] Failed to write log file '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        status_tag = "[!]" if interrupted else ("[+]" if exit_code == 0 else "[-]")
        print(
            f"\n{status_tag} Log saved -> {args.output} "
            f"(format: {fmt}, exit: {exit_code}, duration: {meta['duration']})",
            file=sys.stderr,
        )

    # Propagate the wrapped command's exit code, with 130 for Ctrl+C (SIGINT)
    # to follow standard shell convention.
    sys.exit(130 if interrupted else exit_code)


if __name__ == "__main__":
    main()
