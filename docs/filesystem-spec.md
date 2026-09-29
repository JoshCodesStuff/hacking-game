The file system uses the Unix FHS as a guide for naming and file default locations:

```txt
/var/log
/sys
/var/bin
/home
```

Within folders like `/var/bin` you would find the following binaries:

```txt
ls <- list directory
cd <- change directory
mv <- move + rename
nano <- text editor
rm <- delete file
grep <- print lines that match patterns
pwd <- print current/working directory
scp <- copy (shorten)
ssh <- remote login
pslist <- report current running processes
help <- prints help text
```

**The Filesystem/Program Model**

- How do you represent a "program"? Is it bytecode? AST? Just a string that gets interpreted line-by-line?
- When a program runs, what's the execution context? (Does it have stdin/stdout? Environment variables? Working directory?)
- How does memory actually work? Is it per-process, per-user, or per-computer?
- Can multiple programs run simultaneously on one computer, or is it single-threaded?


I've added a permission model (updated):

```python
# directories
permissions = {
    "owner": {"read": 1, "write": 1},
    "others": {"read": 1, "write": 0}
}

# files
permissions: dict = field(default_factory=lambda: {
	"owner": {"read": 1, "write": 1},
	"others": {"read": 0, "write": 0}
}
```

and a function to check authorisation which takes the owner and action (`rw`) intended to be performed, which can be called against the filesystem object, first the `pwd` then the `target` file. If both resolve true, we are golden, user can do whatever they want:

```python
def authorised(self, username: str, action: str) -> bool:
	if username == self.owner:
		return bool(self.permissions["owner"][action])
	return bool(self.permissions["others"][action])
```

This permission design allows the user to read and write files they own. They will be able to read on directories to see files exist, but won't be able to view the file's contents if they are not an owner. 

> [!NOTE] 
> I haven't got to a point where execute (`x`) is worth adding yet. This is intended so that users can guard files when (if) an attacker is on their computer.


