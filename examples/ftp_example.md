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

```
$ logcmd "ftp 10.129.3.103" ftp.txt                                        
Connected to 10.129.3.103.                                                                 
220 (vsFTPd 3.0.5)                                                                         
Name (10.129.3.103:noob): anonymous                                                        
230 Login successful.                                                                      
Remote system type is UNIX.                                                                
Using binary mode to transfer files.                                                       
ftp> ls                                                                                    
229 Entering Extended Passive Mode (|||41920|)                                             
150 Here comes the directory listing.                                                      
drwxr-xr-x    2 ftp      ftp          4096 Sep 22  2025 pub                                
226 Directory send OK.                                                                     
ftp> cd pub                                                                                
250 Directory successfully changed.                                                        
ftp> ls -lah                                                                               
229 Entering Extended Passive Mode (|||42757|)                                             
150 Here comes the directory listing.                                                      
drwxr-xr-x    2 ftp      ftp          4096 Sep 22  2025 .                                  
drwxr-xr-x    3 ftp      ftp          4096 Sep 22  2025 ..                                 
-rw-r--r--    1 ftp      ftp       6445030 Sep 22  2025 employee-service.jar               
226 Directory send OK.                                                                     
ftp> get employee-service.jar                                                              
local: employee-service.jar remote: employee-service.jar                                   
229 Entering Extended Passive Mode (|||41078|)                                             
150 Opening BINARY mode data connection for employee-service.jar (6445030 bytes).          
100% |************************************|  6293 KiB  947.00 KiB/s    00:00 ETA           
226 Transfer complete.                                                                     
6445030 bytes received in 00:06 (931.46 KiB/s)                                             
ftp> exit                                                                                  
221 Goodbye.                                                                               
                                                                                           
[+] Log saved -> ftp.txt (format: plain, exit: 0, duration: 21.87s)
```

`ftp.txt` on disk:

```
$ cat ftp.txt
============================================================
Timestamp : 2026-07-10 17:25:01 IST
User      : noob@noob
CWD       : /home/noob/lab/htb/DevArea/nmap
Tool      : ftp
Target    : 10.129.3.103
Command   : ftp 10.129.3.103
============================================================

Connected to 10.129.3.103.
220 (vsFTPd 3.0.5)
Name (10.129.3.103:noob): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||41920|)
150 Here comes the directory listing.
drwxr-xr-x    2 ftp      ftp          4096 Sep 22  2025 pub
226 Directory send OK.
ftp> cd pub
250 Directory successfully changed.
ftp> ls -lah
229 Entering Extended Passive Mode (|||42757|)
150 Here comes the directory listing.
drwxr-xr-x    2 ftp      ftp          4096 Sep 22  2025 .
drwxr-xr-x    3 ftp      ftp          4096 Sep 22  2025 ..
-rw-r--r--    1 ftp      ftp       6445030 Sep 22  2025 employee-service.jar
226 Directory send OK.
          mployee-service.jar
local: employee-service.jar remote: employee-service.jar
229 Entering Extended Passive Mode (|||41078|)
150 Opening BINARY mode data connection for employee-service.jar (6445030 bytes).
100% |************************************|  6293 KiB  947.00 KiB/s    00:00 ETA
226 Transfer complete.
6445030 bytes received in 00:06 (931.46 KiB/s)
ftp> exit
221 Goodbye.

============================================================
Exit Code : 0
Duration  : 21.87s
Status    : SUCCESS
============================================================
```

### Why this works now

v1.1.0 forwards the real terminal's stdin to the child's pty (with the local terminal in raw mode), so `ftp`'s username/password prompts — and any other interactive program's prompts — receive input exactly as if you'd run the command directly. See the [CHANGELOG](../CHANGELOG.md#110---2026-07-09) for the full technical explanation.
