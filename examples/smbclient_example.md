# Example: smbclient

Target: HackTheBox "Dancing" (easy, publicly documented training box).

### Before

Running the command directly — output prints to the terminal and is gone once the scrollback clears. No record of when it ran, how long it took, or what exit code it returned.

```
noob@noob: ~ $ smbclient -L //10.129.74.71 -N

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.74.71 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

### After

Same command, wrapped in `logcmd`. Live output is identical — nothing about the interactive experience changes — but a structured, attributable log is now saved to disk.

```
noob@noob: ~ $ logcmd "smbclient -L //10.129.74.71 -N" smb.txt

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.74.71 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

[+] Log saved -> smb.txt (format: plain, exit: 0, duration: 9.23s)

noob@noob: ~ $ cat smb.txt
============================================================
Timestamp : 2026-07-03 04:11:39 IST
User      : noob@noob
CWD       : /home/noob
Tool      : smbclient
Target    : 10.129.74.71
Command   : smbclient -L //10.129.74.71 -N
============================================================

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.74.71 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available

============================================================
Exit Code : 0
Duration  : 9.23s
Status    : SUCCESS
============================================================
```

Raw captured log: [`smbclient_dancing.txt`](smbclient_dancing.txt)
