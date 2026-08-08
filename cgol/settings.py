from pathlib import Path

from pygame import Color, font, Font


class Settings:
    """Manage settings for the Game of Life."""

    def __init__(self):
        self.title: str = "Conway's Game of Life"
        self.max_fps: int = 60

        self.screen: _ScreenSettings = _ScreenSettings()
        self.dynamic: _GameSpeedSettings = _GameSpeedSettings()
        self.cell: _CellSettings = _CellSettings()
        self.control_panel: _ControlPanelSettings = _ControlPanelSettings()


class _ScreenSettings:
    def __init__(self):
        # When not in full screen
        self.width: int = 1200  # Columns of cells
        self.height: int = 700  # Rows of cells
        self.min_width: int = 500
        self.min_height: int = 300

        self.bg_color: Color = Color(50, 50, 50)

        self.resizable: bool = True

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _CellSettings:
    def __init__(self):
        self.width: int = 4
        self.height: int = 4

        self.alive_color: Color = Color(255, 255, 255)
        self.dead_color: Color = Color(0, 0, 0)

    @property
    def dimensions(self) -> tuple[int, int]:
        return self.width, self.height


class _GameSpeedSettings:
    def __init__(self):
        # Number of generations per frame (to start the game with).
        # 1.0 is around 60 gen/sec on a regular computer (if FPS is set to 60).
        self._game_speed: float = 1.0
        self.max_game_speed: float = 10.0
        self.min_game_speed: float = 1/64

    @property
    def game_speed(self) -> float:
        """Game speed in generations per frame."""
        return min(
            max(self._game_speed, self.min_game_speed),
            self.max_game_speed
        )

    @game_speed.setter
    def game_speed(self, game_speed: float) -> None:
        """Game speed in generations per frame."""
        self._game_speed = min(
            max(game_speed, self.min_game_speed),
            self.max_game_speed
        )

    def increase_game_speed(self):
        """Increase game speed.

        Game speed is measured in generations per frame.
        Game speeds less than one increment by 0.25.
        """
        if self.game_speed >= 1:
            self.game_speed += 1
        elif self.game_speed >= 0.5:
            self.game_speed += 0.25
        else:
            self.game_speed *= 2

    def decrease_game_speed(self):
        """Decrease game speed.

        Game speed is measured in generations per frame.
        Game speeds less than one decrement by 0.25
        """
        if self.game_speed < 0.5:
            self.game_speed /= 2
        elif self.game_speed <= 1:
            self.game_speed -= 0.25
        else:
            self.game_speed -= 1


class _ControlPanelSettings:
    def __init__(self):
        self.screen_align: str = "bottomleft"
        self.padding: int = 20
        self.margin: int = 20  # Only applies to non-center alignments
        self.gap: int = 30  # Gap between widgets
        self.color: Color = Color(80, 80, 80, 200)

        self.paused_icon = _PausedIconWidgetSettings()
        self.game_speed_widget = _GameSpeedMeterWidgetSettings()
        self.generations_widget = _GenerationCounterWidgetSettings()
        self.population_widget = _PopulationCounterWidgetSettings()
        self.other_info = _OtherGameInfoWidgetSettings()


class _PausedIconWidgetSettings:
    def __init__(self):
        self.paused_img_path: Path = (Path(__file__).parent.parent
                                      / "assets/paused.png").resolve()
        self.unpaused_img_path: Path = (Path(__file__).parent.parent
                                        / "assets/unpaused.png").resolve()
        self.width: int = 30


class _GameSpeedMeterWidgetSettings:
    def __init__(self):
        self.font: Font = font.SysFont(name="monospace", size=20,
                                       bold=True, italic=False)
        self.font_color: Color = Color(255, 255, 255)


class _GenerationCounterWidgetSettings:
    def __init__(self):
        self.font: Font = font.SysFont(name="monospace", size=20,
                                       bold=False, italic=False)
        self.font_color: Color = Color(255, 255, 255)

        self.counter_cap: int = 9999999


class _PopulationCounterWidgetSettings:
    def __init__(self):
        self.font: Font = font.SysFont(name="monospace", size=20,
                                       bold=False, italic=False)
        self.font_color: Color = Color(255, 255, 255)


class _OtherGameInfoWidgetSettings:
    def __init__(self):
        self.font: Font = font.SysFont(name="monospace", size=15,
                                       bold=False, italic=False)
        self.font_color: Color = Color(200, 200, 200)

        # Framerate Widget
        self.fps_warning_threshold: int = 35  # warns when FPS drops below this
        self.fps_warning_font_color: Color = Color(255, 70, 70)
        self.framerate_decimal_places: int = 1

        # Generation Rate Widget
        self.gen_rate_decimal_places: int = 1
