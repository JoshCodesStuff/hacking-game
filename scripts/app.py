from simulation import Computer, File, Network

# from user import User


def setup_user_machine() -> Network:
    network = Network()

    # Create computers
    player_home = Computer(
        hostname="home-pc",
        ip_address="192.168.1.100",
        filesystem=File(name="root", type=FSNodeType.DIR),
    )

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
