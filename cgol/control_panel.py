from typing import Any, TYPE_CHECKING

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
            _GameSpeedMeter(cgol),
            _FramerateMeter(cgol),
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
                 color: pygame.Color | None, longest: Any) -> None:
        """Initialize attributes.

        ``longest`` is the longest possible text (as in physical length on
        screen, not character count) that will be shown. Assumptions will
        inevitably have to be made. This prevents longer text from
        overflowing past the widget's initial Rect passed to ``ControlPanel``
        (control panel dimensions are static).
        """
        self.cgol = cgol  # Initialize first cuz `_get_surface` or the
        #                   methods it calls might need it.
        self.dynamic_settings = cgol.settings.dynamic

        self.font: pygame.Font = font
        self.color: pygame.Color = color or pygame.Color(0, 0, 0)

        self.longest: Any = longest
        super().__init__(cgol, self._get_surface(self.longest).size)

    @property
    def surface(self) -> pygame.Surface:
        """Get the ``Surface`` of this text widget."""
        return self._get_surface()

    def _get_surface(self, text: Any | None = None) -> pygame.Surface:
        """Get the ``Surface`` of this text widget.

        If ``text`` is ``None``, the actual value to render will be used.
        Otherwise, use the given string as the text. (This is so that the
        max possible length of this widget can be passed to ``ControlPanel``.
        See super() call in __init__.)
        """
        return self.font.render(
            self._get_text_to_render(text),
            antialias=True, color=self.color,
        )

    def _get_text_to_render(self, text: Any | None = None) -> str:
        """Get the text to render on screen."""
        raise NotImplementedError


class _GameSpeedMeter(_TextWidget):
    """Manage the game speed meter widget on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.gsm_settings = cgol.settings.control_panel.game_speed_meter
        self.dynamic_settings = cgol.settings.dynamic

        super().__init__(cgol,
                         font=self.gsm_settings.font,
                         color=self.gsm_settings.font_color,
                         longest=self.dynamic_settings.min_game_speed)

    def _get_text_to_render(self, speed: float | None = None) -> str:
        """Get the text to render on screen.

        If ``speed`` is ``None``, the actual game speed will be used.
        Otherwise, use the given number as the speed.
        """
        numer, denom = (
            self.dynamic_settings.game_speed.as_integer_ratio()
            if speed is None else speed.as_integer_ratio()
        )
        num: str = str(numer) if denom == 1 else f"{numer}/{denom}"
        return f"{num} generation{"s" if numer/denom != 1 else ""}/sec"


class _FramerateMeter(_TextWidget):
    """Manage the framerate meter widget on the control panel.

    Framerate is computed by averaging the last ten calls to `Clock.tick()`.
    """

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.frm_settings = cgol.settings.control_panel.framerate_meter

        self.max_fps = cgol.settings.max_fps
        self.dp = self.frm_settings.framerate_decimal_places
        self.warning_threshold = self.frm_settings.warning_threshold

        self.normal_color = self.frm_settings.font_color
        self.warning_color = self.frm_settings.warning_font_color

        super().__init__(cgol, color=None, font=self.frm_settings.font,
                         longest=f"{self.max_fps}.{"0" * self.dp}")

    def _get_surface(self, text: Any | None = None) -> pygame.Surface:
        """Get the ``Surface`` of this text widget.

        If ``text`` is ``None``, the actual value to render will be used.
        Otherwise, use the given string as the text. (This is so that the
        max possible length of this widget can be passed to ``ControlPanel``.
        See super() call in __init__.)
        """
        if self.max_fps - self.cgol.clock.get_fps() < self.warning_threshold:
            color = self.normal_color
        else:
            color = self.warning_color
        return self.font.render(
            self._get_text_to_render(text),
            antialias=True, color=color,
        )

    def _get_text_to_render(self, rate: str | None = None) -> str:
        """Get the text to render on screen.

        If ``rate`` is ``None``, the actual game speed will be used.
        Otherwise, use the given string as the speed.
        """
        return f"{round(self.cgol.clock.get_fps(), self.dp)} fps"
