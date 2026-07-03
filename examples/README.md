# Examples
This directory contains real `logcmd` examples captured during testing
against Hack The Box's **Dancing** machine (an easy, publicly documented
training target).

These are genuine command outputs and logs—not fabricated examples.

| Tool | Before/After write-up | Raw captured log |
|---|---|---|
| smbclient | [`smbclient.md`](smbclient.md) | [`smbclient_dancing.txt`](smbclient_dancing.txt) |
| nxc (NetExec) | [`nxc.md`](nxc.md) | [`nxc_dancing.txt`](nxc_dancing.txt) |
| nmap | [`nmap.md`](nmap.md) | [`nmap_dancing.txt`](nmap_dancing.txt) |

Metadata in every captured log (timestamp, user@host, cwd, tool, target, exit code, duration, status) is auto-populated by `logcmd` itself — nothing here is hand-edited.

For installation, usage, and additional examples, see the main
[README](../README.md).
