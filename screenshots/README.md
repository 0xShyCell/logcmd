## Screenshots

### SMBClient

**Command**

```bash
logcmd "smbclient -L //<target> -N" smb.txt
```

![SMBClient](logcmd_smbclient.png)

---

### NetExec

**Command**

```bash
logcmd "nxc smb <target> -u Anonymous -p Anonymous --shares" nxc.txt
```

![NetExec](logcmd_nxc.png)

---

### HTML Output

**Command**

```bash
logcmd "nmap -p135,139,445 -sV -sC <target>" nmap.html --format html
```

![HTML Output](logcmd_nmap_html.png)
