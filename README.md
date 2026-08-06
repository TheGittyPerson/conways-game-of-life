# Conway's Game of Life <sub><sup>(v1.0.0)</sup></sub>

A simple [Conway's Game of Life][wiki] in Python, using the `pygame-ce` library.

## Game Info

- Developed with Python 3.14 (maybe it works on other versions? idk lol)
- Uses `pygame-ce` as main game library
- Compatible with macOS, Windows, Linux, and more!
- Default maximum framerate (or tick rate) is 60 FPS.
- Extremely light-weight and easy to use with a simple UI

## How to use

Install Run `python cgol/__main__.py` to start.

The game starts in a paused state.

- `Left-click + Drag`: temporarily pause and draw (activate cells)
- `Right-click + Drag`: temporarily pause and erase (kill cells)

Key commands:
- `Space`: Pause/Unpause
- `C`: Hide/Unhide control panel
- `R`: Reset grid (also resizes grid with more/fewwer pixels if window resized)
- `Q`: Quit

You can adjust initial settings in `settings.py`.

---

## License

This project is licensed under the [MIT License](LICENSE.txt).

[wiki]: https://conwaylife.com/wiki/Conway%27s_Game_of_Life
