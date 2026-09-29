# what the network is made up of
from dataclasses import dataclass, field
from ipaddress import ip_address
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
        print(self.permissions)


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
    users: dict # store a list of users... still haven't decided if adding admin users via group is cool
    ip_address: str
    filesystem: Directory = field(
        default_factory=lambda: Directory(name="/", owner="root"))
    process_list: dict = field(default_factory=dict)


# holds the networked pc's
@dataclass
class Network:
    network: dict # hostname: [computer, ip_addr]

    def add_computer(self,computer: Computer) -> None:
        self.network[computer.ip_address] = computer

    def resolve_target(self, user_input_ip_addr: str) -> Computer | None:
        if user_input_ip_addr in self.network:
            return self.network[self.network[user_input_ip_addr]]

        return None
