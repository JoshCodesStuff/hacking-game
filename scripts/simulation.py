# what the network is made up of
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FSNode:
    """Base class for filesystem entities because DRY"""
    name: str
    owner: str
    permissions: dict
    parent: Optional["FSNode"] = None

    def can_read(self, username: str) -> bool:
        """If can_read returns false: no viewing file contents."""
        if username == self.owner:
            return bool(self.permissions["owner"]["read"])
        return bool(self.permissions["others"]["read"])

    def can_write(self, username: str) -> bool:
        """If can_write returns false: no deleting, no editing, no chmod"""
        if username == self.owner:
            return bool(self.permissions["owner"]["write"])
        return bool(self.permissions["others"]["write"])

    def get_path(self) -> str:
        """walk backwards to root to find the path of the file."""
        path_parts = []
        current = self.parent
        while current is not None:
            if current.name:  # Skip empty/root name
                path_parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(path_parts))


@dataclass
class Directory(FSNode):
    children: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=lambda: {
        "owner": {"read": 1, "write": 1},
        "others": {"read": 1, "write": 0}
    })

    def make_child_directory(self, name, user):
        if self.can_write(user):
            child = Directory(name=name,parent=self, owner=user)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")

    def make_child_file(self, name, user, contents=""):
        if self.can_write(user):
            child = File(name=name, parent=self, owner=user)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")


@dataclass
class File(FSNode):
    contents: str = ""
    permissions: dict = field(default_factory=lambda: {
        "owner": {"read": 1, "write": 1},
        "others": {"read": 0, "write": 0}
    })

    """
    read (
    - path,
    - contents,
    - permissions)
    """
    # update (
    # - modify contents,
    # - permissions,
    # - path?)
    # delete


# the nodes which reside within the network map
@dataclass
class Computer:
    hostname: str
    ip_address: str
    filesystem: Directory
    process_list: dict = field(default_factory=dict)
    is_compromise: bool = False

    def __post_init__(self):
        if self.filesystem is None:
            self.filesystem = Directory(name="/", owner="root")

    def get_file(self, path: str) -> File|None:
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
