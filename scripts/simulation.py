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

    def authorised(self, username: str, action: str) -> bool:
        if username == self.owner:
            return bool(self.permissions["owner"][action])
        return bool(self.permissions["others"][action])

    def get_path(self) -> str:
        """walk backwards to root to find the path of the file."""
        path_parts = []
        current = self.parent
        while current is not None:
            if current.name:  # Skip empty/root name
                path_parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(path_parts))

    def get_permissions(self) -> str:
        """returns a string with the permissions of the
        File or Directory + Owner name in format `-rwxrwx root`"""



@dataclass
class Directory(FSNode):
    children: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=lambda: {
        "owner": {"read": 1, "write": 1},
        "others": {"read": 1, "write": 0}
    })

    def make_child_directory(self, name, user):
        if len(name) < 1:
            raise ValueError("Cannot have unnamed directory.")
        if self.authorised(user, "write"):
            child = Directory(name=name,parent=self, owner=user)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")

    def make_child_file(self, name, user, contents=""):
        if len(name) < 1:
            raise ValueError("Cannot have unnamed file.")
        if self.authorised(user, "write"):
            child = File(name=name, parent=self, owner=user, contents=contents)
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
    - [x] path <- from parent class
    - [ ] contents
    - [ ] permissions <- from parent class)
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
    filesystem: Directory = field(
        default_factory=lambda: Directory(name="/", owner="root"))
    process_list: dict = field(default_factory=dict)
    is_compromise: bool = False


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
