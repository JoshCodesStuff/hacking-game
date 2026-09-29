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


I've added a permission model:

```py
permissions: dict ={
        f"{owner}":[1,0,0],
        f"{group}":[1,0,0],
        "others":[1,0,0]
    }
```

This will allow the user to read and write files they own, read files they don't own, and won't be able to execute anything unless it is approved.