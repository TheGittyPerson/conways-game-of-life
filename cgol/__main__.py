from . import ConwaysGameOfLife


def main() -> None:
    print("Initializing simulation...")
    cgol = ConwaysGameOfLife()
    print("Starting...")
    try:
        cgol.run()
    except KeyboardInterrupt:
        pass
    print("Done!")


if __name__ == "__main__":
    main()
