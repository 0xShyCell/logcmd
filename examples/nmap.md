# Example: nmap

Target: HackTheBox "Dancing" (easy, publicly documented training box).

### Before

```
noob@noob: ~ $ nmap -p135,139,445 -sV -sC $IP
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-03 04:17 IST
Nmap scan report for 10.129.74.71
Host is up (0.30s latency).

PORT    STATE SERVICE       VERSION
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
|_clock-skew: 3h59m59s
| smb2-time:
|   date: 2026-07-03T02:47:55
|_  start_date: N/A

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 38.59 seconds
```

### After

```
noob@noob: ~ $ logcmd "nmap -p135,139,445 -sV -sC $IP" nmap.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-03 04:20 IST
Nmap scan report for 10.129.74.71
Host is up (0.28s latency).

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

[+] Log saved -> nmap.txt (format: plain, exit: 0, duration: 36.55s)

noob@noob: ~ $ cat nmap.txt
============================================================
Timestamp : 2026-07-03 04:20:11 IST
User      : noob@noob
CWD       : /home/noob
Tool      : Nmap
Target    : 10.129.74.71
Command   : nmap -p135,139,445 -sV -sC 10.129.74.71
============================================================

Starting Nmap 7.95 ( https://nmap.org ) at 2026-07-03 04:20 IST
Nmap scan report for 10.129.74.71
Host is up (0.28s latency).

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

Raw captured log: [`nmap_dancing.txt`](nmap_dancing.txt)
