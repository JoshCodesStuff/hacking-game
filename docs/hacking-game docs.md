**Contents:**

- [filesystem spec](/docs/filesystem-spec)
- [clanker's ramblings](docs/clanker's%20ramblings.md)
- [logging](docs/logging.md)

## Todo:

Build the file system so that it can be interacted with in a pseudo shell better than the one the LLM generated. We also need unit tests -> create, read, update, delete files + directories.

Unit Tests:

- [ ] create file
- [ ] read file
- [ ] update file
- [ ] delete file

- [ ] read dir
- [ ] create dir
- [x] update dir... (add child file, add child dir)
- [ ] delete dir

Then we can start moving from one computer to another, or potentially adding users to the computer the user is on.