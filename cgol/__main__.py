from . import ConwaysGameOfLife


def main() -> None:
    print("Initializing Conway's Game of Life...")
    cgol = ConwaysGameOfLife()
    print("Starting...")
    try:
        cgol.run()
    except KeyboardInterrupt:
        pass
    print("Done!")


if __name__ == "__main__":
    main()
