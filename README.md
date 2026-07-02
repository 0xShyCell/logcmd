# logcmd

A professional command-logging utility for penetration testing, red teaming, OSCP labs, and HTB/THM boxes. Runs any shell command through a pseudo-terminal (pty) so tool output streams live in your terminal — colors and all — while simultaneously writing a clean, timestamped, report-ready log to a file.

Built for the moment every OSCP/CPTS report needs: *"prove exactly what command you ran, when, against what, and what it returned."*

## Why

Piping a command's output to a file with `> log.txt` either loses color entirely or captures raw, unreadable ANSI escape codes. Tools like `script` capture a whole session but don't give you clean per-command metadata or a choice of output format. `logcmd` runs your command inside a real pty — so tools like `nmap`, `nxc`, `gobuster`, and `enum4linux-ng` believe they have a real terminal and emit color exactly as they would interactively — then saves a structured report with full metadata, in the format you actually want for your report.

## Features

- **Live output, unaltered** — see full color, live progress bars, everything exactly as if you ran the command directly.
- **Structured metadata per run** — timestamp, user@host, cwd, detected tool name, detected target IP, exit code, duration, and run status (success / failed / interrupted).
- **Three output formats**, auto-selected from the output filename's extension (or forced with `--format`):
  - **Plain text** — classic pentest log format
  - **Markdown** (`.md`) — metadata table + fenced code block, ANSI stripped automatically
  - **HTML** (`.html`) — full color preserved via inline-styled spans (supports 16-color, 256-color, and 24-bit truecolor ANSI)
- **Automatic tool recognition** — recognizes 25+ common offensive-security tools (nmap, NetExec, Hydra, BloodHound, Evil-WinRM, sqlmap, etc.) for a clean `Tool:` field in the report.
- **Target IP auto-detection** for the `Target:` metadata field.
- **Graceful Ctrl+C handling** — SIGINT is forwarded to the full process group (so piped commands stop together), and interrupted runs are recorded as such in the log rather than silently truncated.
- **Carriage-return collapsing** — progress-bar/spinner output (nmap `--stats-every`, hashcat, hydra) is collapsed to its final rendered line instead of dumping every intermediate frame.
- **Zero dependencies** — pure Python 3 standard library.

**Verified against:** `smbclient`, `nxc` (NetExec), `nmap`. `logcmd` works with any shell command generically — it's a pty wrapper, not tool-specific — and the tools listed in `TOOL_NAME_MAP` get clean display names in the metadata, see `examples/` and `screenshots/`" instead of just asserting "confirmed end-to-end".

## Installation

```bash
chmod +x logcmd.py
sudo cp logcmd.py /usr/local/bin/logcmd
```

## Usage

```
logcmd "<command>" <output_file> [options]
```

| Flag | Description |
|---|---|
| `-f, --format {plain,markdown,html}` | Force an output format (default: inferred from the output file extension) |
| `--strip-ansi` | Strip ANSI color codes from the **saved** log (live terminal output is always shown in color) |
| `-a, --append` | Append to the output file instead of overwriting it |
| `-q, --quiet` | Suppress the final summary line |
| `-V, --version` | Show version |

### Examples

```bash
logcmd "nxc smb 10.211.11.10 -u '' -p '' --shares" nxc.txt
logcmd "nmap -sV -p- 10.211.11.10" nmap.txt
logcmd "enum4linux-ng -A 10.211.11.10" enum4linux.html --format html
logcmd "gobuster dir -u http://10.211.11.10 -w /usr/share/wordlists/dirb/common.txt" gobuster.md
logcmd "cat /etc/passwd | grep -i bash" loot.txt --strip-ansi
logcmd "hydra -l admin -P rockyou.txt ssh://10.211.11.10" hydra.txt --append
```

Format is auto-detected from the file extension: `.md`/`.markdown` → Markdown, `.html`/`.htm` → HTML, anything else → plain text.

### Real example

Run against HackTheBox's "Dancing" (an easy, publicly documented training box). Output streams live exactly as it would running the command directly, and a structured log is saved alongside it.

```
$ logcmd "nxc smb 10.129.74.71 -u Anonymous -p Anonymous --shares" nxc.txt
SMB         10.129.74.71    445    DANCING          [*] Windows 10 / Server 2019 Build 17763 x64 (name:DANCING) (domain:Dancing) (signing:False) (SMBv1:None) (Null Auth:True)
SMB         10.129.74.71    445    DANCING          [+] Dancing\Anonymous:Anonymous (Guest)
SMB         10.129.74.71    445    DANCING          [*] Enumerated shares
SMB         10.129.74.71    445    DANCING          Share           Permissions     Remark
SMB         10.129.74.71    445    DANCING          -----           -----------     ------
SMB         10.129.74.71    445    DANCING          ADMIN$                          Remote Admin
SMB         10.129.74.71    445    DANCING          C$                              Default share
SMB         10.129.74.71    445    DANCING          IPC$            READ            Remote IPC
SMB         10.129.74.71    445    DANCING          WorkShares      READ,WRITE

[+] Log saved -> nxc.txt (format: plain, exit: 0, duration: 24.57s)
```

`nxc.txt` on disk — note `nxc` is automatically resolved to its full display name via `TOOL_NAME_MAP`, and the target IP is auto-detected:

```
============================================================
Timestamp : 2026-07-03 04:15:21 IST
User      : noob@noob
CWD       : /home/noob
Tool      : NetExec
Target    : 10.129.74.71
Command   : nxc smb 10.129.74.71 -u Anonymous -p Anonymous --shares
============================================================

SMB         10.129.74.71    445    DANCING          [*] Windows 10 / Server 2019 Build 17763 x64 (name:DANCING) (domain:Dancing) (signing:False) (SMBv1:None) (Null Auth:True)
SMB         10.129.74.71    445    DANCING          [+] Dancing\Anonymous:Anonymous (Guest)
SMB         10.129.74.71    445    DANCING          [*] Enumerated shares
SMB         10.129.74.71    445    DANCING          Share           Permissions     Remark
SMB         10.129.74.71    445    DANCING          -----           -----------     ------
SMB         10.129.74.71    445    DANCING          ADMIN$                          Remote Admin
SMB         10.129.74.71    445    DANCING          C$                              Default share
SMB         10.129.74.71    445    DANCING          IPC$            READ            Remote IPC
SMB         10.129.74.71    445    DANCING          WorkShares      READ,WRITE

============================================================
Exit Code : 0
Duration  : 24.57s
Status    : SUCCESS
============================================================
```

A follow-up `nmap` scan against the same host, logged the same way:

```
$ logcmd "nmap -p135,139,445 -sV -sC 10.129.74.71" nmap.txt
[+] Log saved -> nmap.txt (format: plain, exit: 0, duration: 36.55s)

$ cat nmap.txt
============================================================
Timestamp : 2026-07-03 04:20:11 IST
User      : noob@noob
CWD       : /home/noob
Tool      : Nmap
Target    : 10.129.74.71
Command   : nmap -p135,139,445 -sV -sC 10.129.74.71
============================================================

PORT    STATE SERVICE       VERSION
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2026-07-03T02:50:41
|_  start_date: N/A
|_clock-skew: 4h00m00s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 36.52 seconds

============================================================
Exit Code : 0
Duration  : 36.55s
Status    : SUCCESS
============================================================
```

Every run against this target — `smbclient`, `nxc`, `nmap` — produces the same consistent, timestamped, attributable format, ready to drop straight into a report's evidence appendix.

## How it works

`logcmd` opens a pty pair and runs your command via `/bin/bash -c "<command>"` with the child process attached to the pty's slave end. This preserves full shell syntax (pipes, redirects, quoting, subshells) and — critically — makes the invoked tool believe it's attached to a real terminal, which is what causes it to emit ANSI color and live progress output in the first place. The master side is read in a loop: every chunk is written straight to real stdout for live viewing, and simultaneously buffered for the saved log. Only the saved log gets post-processed (metadata header/footer, carriage-return collapsing, optional ANSI stripping/HTML conversion) — the live terminal stream is never touched.

## Requirements

Python 3, Linux or macOS (uses the POSIX-only `pty`, `fcntl`, and `termios` modules — not compatible with native Windows; WSL works fine).

## License

MIT — see [`LICENSE`](LICENSE).
