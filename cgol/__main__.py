from cgol import ConwaysGameOfLife


def main() -> None:
    print("Initializing Conway's Game of Life...")
    cgol = ConwaysGameOfLife()
    print("Starting...")
    cgol.run()


if __name__ == "__main__":
    main()
