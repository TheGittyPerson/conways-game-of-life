from pygame import Color


class Settings:
    """Manage settings for the Game of Life."""

    def __init__(self):
        self.title: str = "Conway's Game of Life"

        self.window: _WindowSettings = _WindowSettings()
        self.dynamic: _DynamicSettings = _DynamicSettings()
        self.cell: _Cell = _Cell()

        self.max_fps: int = 100


class _WindowSettings:
    """Window and Screen settings."""
    def __init__(self):
        # When not in full screen
        self.width: int = 1000
        self.height: int = 600

        self.bg_color: Color = Color(50, 50, 50)

        self.start_fullscreen: bool = False

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _Cell:
    def __init__(self):
        # Individual
        self.width: int = 5
        self.height: int = 5

        self.alive_color: Color = Color(255, 255, 255)
        self.dead_color: Color = Color(0, 0, 0)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _DynamicSettings:
    def __init__(self):
        self.game_speed: int = 1  # Number of updates per game iteration.
