Logging is used as a game mechanic to leave a trace of actions performed on a system. The mechanics should be designed such that the player typically deletes all logs from a system. 


> [!INFO] Game mechanic idea
> It could be interesting to use logs that exist on a system as a story telling device. In HackNet, the player is asked to clear logs off a system that their mentor was previously doing things on. This seems like a missed opportunity. Instead, seeing what people previously did, who previously auth'd to a system and where they came from could be used.

Logging on my fedora system stores:

` joshh : TTY=pts/1 ; PWD=/home/joshh/Projects/hacking-game/scripts ; USER=root ; COMMAND=/usr/sbin/dnf install gnome-logs`

Don't care about the TTY part, but where they were, what they ran, who ran it, what it was run as would all be good. Although if we see:

1. `session opened for user root(uid=0) by joshh(uid=1000)`
2. `PWD=/home/joshh/Projects/hacking-game/scripts ; USER=root ; COMMAND=/usr/sbin/dnf install gnome-logs`
3. `session closed for user joshh`

Then this covers what I am trying to do nicely.

I'd reformat to have something standardised I think, so the following table structure would be good:

| sess_id | User  | pwd                   | command                                      |
| ------- | ----- | --------------------- | -------------------------------------------- |
| 1       | joshh | /home/joshh/Downloads | curl "hxxps[://]malware[.]com/malware[.]exe" |

SSH looks awful in regular unix systems - poor forensicators:

`AUDIT1112 pid=35168 uid=0 auid=4294967295 ses=4294967295 subj=system_u:system_r:sshd_session_t:s0-s0:c0.c1023 msg='op=login acct="joshh" exe="/usr/libexec/openssh/sshd-session" hostname=? addr=192.168.0.107 terminal=ssh res=failed'`

We can clean this up by modifying the above lines to drastically simplify the logs.

1. `remote session opened for user joshh by <remote_ip_addr,hostname>`
2. `remote session opened for user root by joshh`
3. `PWD=/home/joshh/Projects/hacking-game/scripts ; USER=root ; COMMAND=/usr/sbin/dnf install gnome-logs`
4. `remote session closed for user root`

Looks good, tells a story, I think a session id would be good with it all.