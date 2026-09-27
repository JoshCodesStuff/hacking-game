# what the network is made up of
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# literally just allows us to check the file type using type()
class FileType(Enum):
    FILE="file"
    DIR="dir"


@dataclass # fancy wrapper to make things less verbose
class FileSystemNode:
    name: str
    type: FileType
    contents: str = ""
    parent: Optional['FileSystemNode'] = None
    child: dict = field(default_factory=dict)
    # permissions: int=0o644
    # macb etc?
    def get_path(self) -> str:
        if self.parent is None:
            return f"/{self.name}"
        return f"{self.parent.get_path()}/{self.name}"


# the nodes which reside within the network map
@dataclass
class Computer:
    hostname: str
    ip_address: str
    filesystem: FileSystemNode
    process_list: dict = field(default_factory=dict)
    is_compromise: bool = False

    def __post_init__(self):
        if self.filesystem is None:
            self.filesystem = FileSystemNode(
                name="",
                type=FileType.DIR
            )

    def get_file(self, path: str) -> FileSystemNode|None:
        parts = [p for p in path.split("") if p]
        current = self.filesystem

        for part in parts:
            if part in current.child:
                current=current.child[part]
            else:
                return None
        return current


# holds the pc network
class Network:
    def __init__(self) -> None:
        self.computers: dict = {} # hostname -> computer
        self.ip_map: dict = {} # ipaddress -> hostname (DNS???)
        self.connections: set[tuple[str,str]] = set() # (hostname1, hostname2)

    def add_computer(self,computer: Computer) -> None:
        self.computers[computer.hostname] = computer
        self.ip_map[computer.ip_address] = computer.hostname

    def resolve_target(self, user_input: str) -> Optional[Computer]:
        if user_input in self.computers:
            return self.computers[user_input]
        if user_input in self.ip_map:
            return self.computers[self.ip_map[user_input]]

        matches = [c for hostname, c in self.computers.items() if hostname.startswith(user_input)]
        if len(matches) == 1:
            return matches[0]

        return None

    def connect(self, hostname1: str, hostname2: str):
            """Add edge between two computers"""
            self.connections.add((hostname1, hostname2))
            self.connections.add((hostname2, hostname1))  # Bidirectional

    def get_neighbors(self, hostname: str) -> list[Computer]:
        """Get computers directly connected"""
        neighbors = []
        for h1, h2 in self.connections:
            if h1 == hostname:
                neighbors.append(self.computers[h2])
        return neighbors
