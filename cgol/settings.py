from pygame import Color


class Settings:
    """Manage settings for the Game of Life."""

    def __init__(self):
        self.screen: _ScreenSettings = _ScreenSettings()
        self.dynamic: _DynamicSettings = _DynamicSettings()
        self.cell: _Cell = _Cell()

        self.max_fps: int = 60


class _ScreenSettings:
    def __init__(self):
        # When not in full screen
        self.width: int = 1000
        self.height: int = 700

        self.bg_color: Color = Color(0, 0, 0)

        self.start_fullscreen: bool = False

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _Cell:
    def __init__(self):
        # Individual
        self.width: int = 5
        self.height: int = 5

        self.alive_color: Color = Color(40, 180, 255)
        self.dead_color: Color = Color(0, 0, 0)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _DynamicSettings:
    def __init__(self):
        self.game_speed: int = 1  # Number of updates per game iteration.
