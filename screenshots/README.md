# Screenshots

| File | Command | Shows |
|---|---|---|
| [`logcmd_smbclient.png`](logcmd_smbclient.png) | `logcmd "smbclient -L //<target> -N" smb.txt` | Live output + `[+] Log saved ->` confirmation |
| [`logcmd_nxc.png`](logcmd_nxc.png) | `logcmd 'nxc smb <target> -u Anonymous -p Anonymous --shares' nxc.txt` | Live colored NetExec output + save confirmation |
| [`logcmd_nmap_html.png`](logcmd_nmap_html.png) | `logcmd "nmap -p135,139,445 -sV -sC <target>" nmap.html --format html` | HTML output rendered in-browser |
