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
        p = 0
        match action:
            case 'read' | 'r':
                p=0
            case 'write' | 'w':
                p=1
            # case 'exec'|'execute'|'x':
            #     p=2
            case _:
                raise ValueError

        if username == self.owner:
            return bool(self.permissions["owner"][p])
        return bool(self.permissions["others"][p])

    def get_path(self) -> str:
        """walk backwards to root to find the path of the file."""
        path_parts = []
        current = self.parent
        while current is not None:
            if current.name:  # Skip empty/root name
                path_parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(path_parts))

    def get_permissions(self):
        """returns a string with the permissions of the
        File or Directory + Owner name in format `-rwxrwx root`"""
        print(self.permissions)


@dataclass
class Directory(FSNode):
    children: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=lambda: {
        "owner": [1,1],
        "others": [1,0]
    })

    # create dir
    def make_dir(self, name, user):
        """create a child directory"""
        if len(name) < 1:
            raise ValueError("Cannot have unnamed directory.")
        if self.authorised(user, "write"):
            child = Directory(name=name,parent=self, owner=user)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")

    # create file
    def make_file(self, name, user, contents=""):
        """create a file in a directory. prevents a file being a parent of a file"""
        if len(name) < 1:
            raise ValueError("Cannot have unnamed file.")
        if self.authorised(user, "write"):
            child = File(name=name, parent=self, owner=user, contents=contents)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")

    # delete file
    def del_file(self, name, user, contents=""):
        """create a file in a directory. prevents a file being a parent of a file"""
        if len(name) < 1:
            raise ValueError("Cannot have unnamed file.")
        if self.authorised(user, "write"):
            child = File(name=name, parent=self, owner=user, contents=contents)
            self.children[name]=child
        else:
            raise PermissionError("Permission denied, no write access")

    # read dir
    # update dir
    # delete dir


@dataclass
class File(FSNode):
    contents: str = ""
    permissions: dict = field(default_factory=lambda: {
        "owner": [1,1],
        "others": [0,0]
    })

    # read file
    # update file
    # delete file


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
