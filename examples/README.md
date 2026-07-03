# Examples

Real `logcmd` output, captured against HackTheBox's "Dancing" (an easy, publicly documented training box) — not fabricated samples.

Each tool has a before/after write-up showing the raw command's output next to the same command wrapped in `logcmd`, plus the raw captured log file it produces.

| Tool | Before/After write-up | Raw captured log |
|---|---|---|
| smbclient | [`smbclient.md`](smbclient.md) | [`smbclient_dancing.txt`](smbclient_dancing.txt) |
| nxc (NetExec) | [`nxc.md`](nxc.md) | [`nxc_dancing.txt`](nxc_dancing.txt) |
| nmap | [`nmap.md`](nmap.md) | [`nmap_dancing.txt`](nmap_dancing.txt) |

Metadata in every captured log (timestamp, user@host, cwd, tool, target, exit code, duration, status) is auto-populated by `logcmd` itself — nothing here is hand-edited.

See the main [README](../README.md#real-example) for a condensed version of these same runs.
