# Example: ftp (interactive)

Target: HackTheBox lab target (IP varies by session — this was the specific bug that drove `logcmd` v1.1.0's interactive PTY support).

### Before (v1.0.0 — the bug)

`ftp` is interactive: it prompts for a username, waits for input, then prompts for a password. v1.0.0 only forwarded the child's output to the terminal — it never forwarded the user's keystrokes back to the child. The result: the session hangs the moment it needs input.

```
noob@noob: ~ $ logcmd "ftp 10.129.2.84" ftp.txt
Connected to 10.129.2.84.
220 (vsFTPd 3.0.5)
Name (10.129.2.84:noob): anonymous
```

Typing `anonymous` and pressing Enter did nothing — the session was stuck here indefinitely. No password prompt ever appeared, and Ctrl+C was needed to break out.

### After (v1.1.0 — fixed)

<!--
TODO: replace this block with your real captured terminal session.
Run:
    logcmd "ftp <target>" ftp.txt
and paste the full interactive session here (login, `ls`, `quit`, etc.),
followed by `cat ftp.txt` to show the saved log, same format as the
other examples in this folder.
-->

```
$ logcmd "ftp <target>" ftp.txt
[paste your real terminal session here]
```

`ftp.txt` on disk:

```
[paste the real contents of ftp.txt here]
```

### Why this works now

v1.1.0 forwards the real terminal's stdin to the child's pty (with the local terminal in raw mode), so `ftp`'s username/password prompts — and any other interactive program's prompts — receive input exactly as if you'd run the command directly. See the [CHANGELOG](../CHANGELOG.md#110---2026-07-09) for the full technical explanation.
