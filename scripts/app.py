from simulation import Computer, FileSystemNode, FileType, Network
from user import User


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


def main():
    user = User()
    print("=== Hacknet Clone ===")
    print(f"You start at: {user.current_location.hostname}")

    while True:
        try:
            prompt = f"[{user.current_location.hostname}]> "
            user_input = input(prompt)
            output = user.execute_command(user_input)
            print(output)
        except KeyboardInterrupt:
            print("\nGoodbye.")
            break

if __name__ == "__main__":
    main()
