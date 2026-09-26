from simulation import Computer, FileSystemNode, FileType, Network
from typing import Optional


def setup_sample_network() -> Network:
    network = Network()

    # Create computers
    player_home = Computer(
        hostname="home-pc",
        ip_address="192.168.1.100",
        filesystem=FileSystemNode(name="root", type=FileType.DIR),
    )

    target = Computer(
        hostname="admin-server",
        ip_address="10.0.1.50",
        filesystem=FileSystemNode(name="root", type=FileType.DIR),
    )

    # Add some files to the target
    target.filesystem.child["etc"] = FileSystemNode(
        name="etc",
        type=FileType.DIR,
        parent=target.filesystem
    )
    target.filesystem.child["etc"].child["shadow"] = FileSystemNode(
        name="shadow",
        type=FileType.FILE,
        contents="admin:$2b$12$...",  # Hashed password
        parent=target.filesystem.child["etc"]
    )

    network.add_computer(player_home)
    network.add_computer(target)

    return network


class GameEngine:
    def __init__(self):
        self.network = setup_sample_network()
        self.current_location: Computer = self.network.computers["home-pc"]
        self.session_log: list[str] = []

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

    def _cmd_cat(self, filepath: Optional[str]) -> str:
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


def main():
    engine = GameEngine()
    print("=== Hacknet Clone ===")
    print(f"You start at: {engine.current_location.hostname}")

    while True:
        try:
            prompt = f"[{engine.current_location.hostname}]> "
            user_input = input(prompt)
            output = engine.execute_command(user_input)
            print(output)
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
