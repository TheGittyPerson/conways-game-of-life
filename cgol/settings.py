from pathlib import Path

from pygame import Color


class Settings:
    """Manage settings for the Game of Life."""

    def __init__(self):
        self.title: str = "Conway's Game of Life"

        self.screen: _ScreenSettings = _ScreenSettings()
        self.dynamic: _DynamicSettings = _DynamicSettings()
        self.cell: _CellSettings = _CellSettings()
        self.control_panel: _ControlPanelSettings = _ControlPanelSettings()

        self.max_fps: int = 60


class _ScreenSettings:
    def __init__(self):
        # When not in full screen
        self.width: int = 1200
        self.height: int = 700

        self.bg_color: Color = Color(50, 50, 50)

        self.resizable: bool = True

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _CellSettings:
    def __init__(self):
        self.width: int = 5
        self.height: int = 5

        self.alive_color: Color = Color(255, 255, 255)
        self.dead_color: Color = Color(0, 0, 0)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _ControlPanelSettings:
    def __init__(self):
        self.screen_align: str = "bottomleft"
        self.padding: int = 20
        self.margin: int = 20  # Only applies to non-center alignments
        self.gap: int = 30  # Gap between control items
        self.color: Color = Color(255, 255, 255, 0)

        self.paused_indicator = _PausedIndicatorSettings()


class _PausedIndicatorSettings:
    def __init__(self):
        self.paused_img_path: Path = (Path(__file__).parent
                                      / "assets/paused.png").resolve()
        self.unpaused_img_path: Path = (Path(__file__).parent
                                        / "assets/unpaused.png").resolve()
        self.width: int = 30


class _GameSpeedBarSettings:
    def __init__(self):
        self.font: str
        self.font_size: int = 20
        self.font_color: Color = Color(255, 255, 255)


class _DynamicSettings:
    def __init__(self):
        self.game_speed: int = 60  # Number of grid updates per second.
