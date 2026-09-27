from typing import Optional

from simulation import Computer,FileType,FileSystemNode


class User:
    def __init__(self):
        # self.network = setup_sample_network()
        # self.current_location: Computer = self.network.computers["home-pc"]
        self.session_log: list[str] = []
        self.help = {
            "ls": "list directory contents",
            "whoami": "prints effective user name",
            "cd": "change directory",
            "mv": "move (rename) files",
            "rm": "remove files or directories",
            "cat": "concatenate files and print output",
            "scp": "secure file copy",
            "ssh": "remote login client"
        }

    def execute_command(self, command: str) -> str:
        """Parse and execute a command"""
        tokens = command.strip().split()
        if not tokens:
            return ""

        cmd = tokens[0].lower()

        if cmd == "ls":
            return self._cmd_ls()
        elif cmd == "connect":
            target = tokens[1] if len(tokens) > 1 else None
            return self._cmd_connect(target)
        elif cmd == "pwd":
            return self._cmd_pwd()
        elif cmd == "cat":
            filepath = tokens[1] if len(tokens) > 1 else None
            return self._cmd_cat(filepath)
        elif cmd == "scan":
            return self._cmd_scan()
        else:
            return f"Unknown command: {cmd}"

    def _cmd_ls(self) -> str:
        """List files in current directory"""
        root = self.current_location.filesystem
        items = list(root.child.keys())
        return "\n".join(items) if items else "(empty)"

    def _cmd_connect(self, target: Optional[str]) -> str:
        """Connect to a target computer"""
        if not target:
            return "Usage: connect [hostname|ip]"

        computer = self.network.resolve_target(target)
        if not computer:
            return f"Host not found: {target}"

        # Simple connectivity check (are they on the network?)
        if computer not in self.network.get_neighbors(self.current_location.hostname):
            return f"No route to host: {target}"

        self.current_location = computer
        return f"Connected to {computer.hostname} ({computer.ip_address})"

    def _cmd_pwd(self) -> str:
        """Print current location"""
        return self.current_location.hostname

    def _cmd_cat(self, filepath: str) -> str | None:
        """Read a file"""
        if not filepath:
            return "Usage: cat [filepath]"

        file_node = self.current_location.get_file(filepath)
        if not file_node:
            return f"cat: {filepath}: No such file or directory"

        if file_node.type == FileType.DIR:
            return f"cat: {filepath}: Is a directory"

        return file_node.contents

    def _cmd_scan(self) -> str:
        """Scan the network from current location"""
        neighbors = self.network.get_neighbors(self.current_location.hostname)
        if not neighbors:
            return "No connected hosts"

        lines = []
        for computer in neighbors:
            status = "COMPROMISED" if computer.is_compromised else "SECURE"
            lines.append(f"  {computer.hostname} ({computer.ip_address}) - {status}")
        return "\n".join(lines)
