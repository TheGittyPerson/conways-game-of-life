from math import prod
from typing import TYPE_CHECKING

import pygame
import pygame.font

if TYPE_CHECKING:
    from . import ConwaysGameOfLife


class ControlPanel:
    """Display controls and game state/settings."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize default settings and widgets."""
        self.cgol = cgol
        self.cp_settings = self.cgol.settings.control_panel

        self.padding = self.cp_settings.padding
        self.margin = self.cp_settings.margin
        self.gap = self.cp_settings.gap
        self.color = self.cp_settings.color

        self.widgets: list[_Widget] = [
            _PausedIcon(cgol),
            _GameSpeedWidget(cgol),
            _GenerationCounterWidget(cgol),
            _PopulationWidget(cgol),
            _FramerateWidget(cgol),
            _GenerationRateWidget(cgol),
        ]

        # DO NOT initialize own reference to `alpha_canvas`.
        # When the game window is resized, a new Surface instance is created
        self.canvas_rect: pygame.Rect = self.cgol.alpha_canvas.get_rect()
        self.rect = self._get_rect()

        self.show = True

    def draw(self) -> None:
        """Draw this control panel and all widgets to screen.

        Redefine ``self.Rect`` if window was resized.
        """
        if self.cgol.events.window_resized:
            self.rect = self._get_rect()

        self.cgol.alpha_canvas.fill(self.color, self.rect)

        current_x: int = self.rect.x + self.padding
        for count, widget in enumerate(self.widgets, start=1):
            widget_rect = widget.rect
            widget_rect.center = self.rect.center

            widget_rect.x = current_x
            current_x += widget.width

            if count != len(self.widgets):
                current_x += self.gap

            self.cgol.alpha_canvas.blit(widget.surface, widget_rect)

    def _get_rect(self) -> pygame.Rect:
        """Calculate and return the control panel's ``Rect``.

        Based on paddings, margins, and relative screen locations
        defined in settings.
        """
        self.canvas_rect = self.cgol.alpha_canvas.get_rect()

        # Dimensions
        total_width = (
                sum(widget.width for widget in self.widgets)
                + self.padding * 2
                + self.gap * (len(self.widgets) - 1)
        )
        total_height = (
                max(widget.height for widget in self.widgets)
                + self.padding * 2
        )

        rect = pygame.Rect(0, 0, total_width, total_height)

        # Alignment
        align_name: str = self.cp_settings.screen_align
        screen_pos: tuple[int, int] = getattr(self.canvas_rect, align_name)
        setattr(rect, align_name, screen_pos)

        # Margins
        self._include_margins(rect, self.margin, align_name)

        return rect

    # noinspection SpellCheckingInspection
    @staticmethod
    def _include_margins(rect: pygame.Rect, margin: int, align: str) -> None:
        """Add margins to the given ``Rect``, taking into account alignment.

        Examples:
            - If ``align='bottomleft'``, ``margin`` will be incremented
              to the Rect's ``x`` and subtracted from the Rect's ``y``.
            - If ``align='midtop'``, ``margin`` will only be incremented
              to the Rect's ``y``.
            - If ``align='center'``, no margins will be added.
        """
        if align not in [
            "center", "midbottom", "midtop", "midleft",
            "midright", "topleft", "topright", "bottomleft",
            "bottomright"
        ]:
            raise ValueError(f"Invalid align location: '{align}'")

        if "bottom" in align:
            rect.y -= margin
        if "top" in align:
            rect.y += margin
        if "left" in align:
            rect.x += margin
        if "right" in align:
            rect.x -= margin


class _Widget:
    """Represents an individual widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife, size: tuple[int, int]) -> None:
        """Initialize attributes."""
        self.cgol = cgol

        self.width: int = size[0]
        self.height: int = size[1]
        self._rect = pygame.Rect(0, 0, self.width, self.height)

    @property
    def surface(self) -> pygame.Surface:
        """Return the ``Surface`` of this widget."""
        raise NotImplementedError

    @property
    def rect(self) -> pygame.Rect:
        """Return the ``Rect`` of this widget."""
        return self._rect


class _PausedIcon(_Widget):
    """Manage the paused icon on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.pi_settings = cgol.settings.control_panel.paused_icon
        self.paused_img: pygame.Surface = pygame.image.load(
            self.pi_settings.paused_img_path
        ).convert_alpha()
        self.unpaused_img: pygame.Surface = pygame.image.load(
            self.pi_settings.unpaused_img_path
        ).convert_alpha()
        self._scale_images()

        super().__init__(cgol, self.paused_img.size)

    @property
    def surface(self) -> pygame.Surface:
        """Get the ``Surface`` of the paused icon.

        Image depending on paused state of the game.
        Reminder: the Surface's Rect has no position.
        """
        return (self.paused_img
                if self.cgol.events.paused or self.cgol.events.secondary_paused
                else self.unpaused_img)

    def _scale_images(self) -> None:
        """Scale the both images to fit the width defined in settings.

        Must be called in ``__init__()`` after defining the image surfaces.
        Both images will be the same size after calling.
        """
        ratio = self.paused_img.width / self.paused_img.height
        if ratio != self.unpaused_img.width / self.unpaused_img.height:
            raise RuntimeError("Images have different size ratios")

        target_width = self.pi_settings.width
        target_height = target_width / ratio
        self.paused_img = pygame.transform.scale(
            self.paused_img, (target_width, target_height)
        )
        self.unpaused_img = pygame.transform.scale(
            self.unpaused_img, (target_width, target_height)
        )


class _TextWidget(_Widget):
    """Represents a text widget."""

    def __init__(self, cgol: ConwaysGameOfLife, font: pygame.Font,
                 color: pygame.Color | None) -> None:
        """Initialize attributes."""
        self.cgol = cgol  # Initialize first cuz `_get_surface` or the
        #                   methods it calls might need it.
        self.dynamic_settings = cgol.settings.dynamic

        self.font: pygame.Font = font
        self.color: pygame.Color = color or pygame.Color(0, 0, 0)

        super().__init__(cgol, self.get_surface(use_longest=True).size)

    @property
    def surface(self) -> pygame.Surface:
        """Get the ``Surface`` of this text widget."""
        return self.get_surface()

    def get_surface(self, use_longest: bool = False) -> pygame.Surface:
        """Get the ``Surface`` of this text widget.

        If ``use_longest`` is True, the longest possible text (as in physical
        length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        return self.font.render(
            self.get_text_to_render(use_longest),
            antialias=True, color=self.color,
        )

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen."""
        raise NotImplementedError


class _GameSpeedWidget(_TextWidget):
    """Manage the game speed widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.gsm_settings = cgol.settings.control_panel.game_speed_widget
        self.dynamic_settings = cgol.settings.dynamic

        super().__init__(cgol,
                         font=self.gsm_settings.font,
                         color=self.gsm_settings.font_color)

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen.

        If ``use_longest`` is True, the longest possible text (as in physical
        length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        longest = self.dynamic_settings.min_game_speed

        numer, denom = (
            self.dynamic_settings.game_speed.as_integer_ratio()
            if not use_longest else longest.as_integer_ratio()
        )
        num: str = str(numer) if denom == 1 else f"{numer}/{denom}"
        return f"{num} generation{"s" if numer / denom != 1 else ""}/frame"


class _GenerationCounterWidget(_TextWidget):
    """Manage the generation count widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.cgol = cgol
        self.gcw_settings = cgol.settings.control_panel.generations_widget
        self.cap = self.gcw_settings.counter_cap

        super().__init__(cgol,
                         font=self.gcw_settings.font,
                         color=self.gcw_settings.font_color)

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen.

        If ``use_longest`` is True, the longest possible text (as in
        physical length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        if not use_longest and self.cgol.generations <= self.cap:
            return f"t={self.cgol.generations}"
        else:
            return f"t>{self.cap}"


class _PopulationWidget(_TextWidget):
    """Manage the population widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        self.cgol = cgol
        self.pw_settings = cgol.settings.control_panel.population_widget

        super().__init__(cgol,
                         font=self.pw_settings.font,
                         color=self.pw_settings.font_color)

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen.

        If ``use_longest`` is True, the longest possible text (as in
        physical length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        longest = prod(self.cgol.settings.screen.dimensions)
        count = self.cgol.grid.population \
            if not use_longest else longest
        return f"Population: {count}"


class _FramerateWidget(_TextWidget):
    """Manage the framerate widget on the control panel.

    Framerate is computed by averaging the last ten calls to `Clock.tick()`.
    """

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.oi_settings = cgol.settings.control_panel.other_info

        self.max_fps = cgol.settings.max_fps
        self.dp = self.oi_settings.framerate_decimal_places
        self.warning_threshold = self.oi_settings.fps_warning_threshold

        self.normal_color = self.oi_settings.font_color
        self.warning_color = self.oi_settings.fps_warning_font_color

        super().__init__(cgol, color=None, font=self.oi_settings.font)

    def get_surface(self, use_longest: bool = False) -> pygame.Surface:
        """Get the ``Surface`` of this text widget."""
        if self.cgol.clock.get_fps() > self.warning_threshold:
            color = self.normal_color
        else:
            color = self.warning_color
        return self.font.render(
            self.get_text_to_render(use_longest),
            antialias=True, color=color,
        )

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen.

        If ``use_longest`` is True, the longest possible text (as in
        physical length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        longest = self.max_fps

        return f"{self.cgol.clock.get_fps()
                  if not use_longest else longest:.{self.dp}f} fps"


class _GenerationRateWidget(_TextWidget):
    """Manage the generation rate widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.cgol = cgol
        self.oi_settings = cgol.settings.control_panel.other_info

        self.max_fps = cgol.settings.max_fps
        self.dp = self.oi_settings.gen_rate_decimal_places

        super().__init__(cgol, color=self.oi_settings.font_color,
                         font=self.oi_settings.font)

    def get_text_to_render(self, use_longest: bool = False) -> str:
        """Get the text to render on screen.

        If ``use_longest`` is True, the longest possible text (as in
        physical length on screen, not character count) will be used.
        Assumptions will inevitably have to be made. This prevents longer
        text from overflowing past the widget's initial Rect passed to
        ``ControlPanel`` (control panel dimensions are static).
        """
        longest = self.max_fps * self.cgol.settings.dynamic.max_game_speed

        game_speed = self.cgol.settings.dynamic.game_speed
        gens_per_sec = (
            (self.cgol.clock.get_fps() * game_speed)
        )
        if self.cgol.events.paused:
            gens_per_sec = 0
        return \
            f"{gens_per_sec if not use_longest else longest:.{self.dp}f} gen/s"
