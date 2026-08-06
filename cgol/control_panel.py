from typing import TYPE_CHECKING

import pygame
import pygame.font

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife


class ControlPanel:
    """Display controls and game state/settings."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize default settings and control items."""
        self.cgol = cgol
        self.alpha_canvas: pygame.Surface = self.cgol.alpha_canvas
        self.settings = self.cgol.settings

        self.padding = self.settings.control_panel.padding
        self.margin = self.settings.control_panel.margin
        self.gap = self.settings.control_panel.gap
        self.color = self.settings.control_panel.color

        self.items: list[_ControlItem] = [
            _PausedIndicator(cgol)
        ]

        self.canvas_rect: pygame.Rect = self.alpha_canvas.get_rect()
        self.rect = self._get_rect()

        self.show = True

    def draw(self) -> None:
        """Draw this control panel and all its items to screen.

        Redefine ``self.Rect`` if window was resized.
        """
        if self.cgol.event_handler.window_resized:
            self.rect = self._get_rect()

        self.alpha_canvas.fill(self.color, self.rect)

        y = self.rect.y + self.padding
        current_x: int = self.rect.x + self.padding
        for count, item in enumerate(self.items, start=1):
            item_rect = item.rect
            item_rect.y = y

            item_rect.x = current_x
            current_x += item.width

            if count != len(self.items):
                current_x += self.gap

            self.alpha_canvas.blit(item.surface, item_rect)

    def _get_rect(self) -> pygame.Rect:
        """Calculate and return the control panel's ``Rect``.

        Based on paddings, margins, and relative screen locations
        defined in settings.
        """
        self.canvas_rect = self.alpha_canvas.get_rect()

        # Dimensions
        total_width = (
                sum(item.width for item in self.items)
                + self.padding * 2
                + self.gap * (len(self.items) - 1)
        )
        total_height = (
                max(item.height for item in self.items)
                + self.padding * 2
        )

        rect = pygame.Rect(0, 0, total_width, total_height)

        # Alignment
        align_name: str = self.settings.control_panel.screen_align
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


class _ControlItem:
    """Represents an individual item on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife, size: tuple[int, int]) -> None:
        """Initialize attributes."""
        self.cgol = cgol
        self.settings = self.cgol.settings

        self.width: int = size[0]
        self.height: int = size[1]
        self._rect = pygame.Rect(0, 0, self.width, self.height)

    @property
    def surface(self) -> pygame.Surface:
        """Return the ``Surface`` of this control item."""
        return pygame.Surface((self.width, self.height))

    @property
    def rect(self) -> pygame.Rect:
        """Return the ``Rect`` of this control item."""
        return self._rect


class _PausedIndicator(_ControlItem):
    """Manage the paused indicator on the control panel."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.settings = cgol.settings
        self.paused_img: pygame.Surface = pygame.image.load(
            self.settings.control_panel.paused_indicator.paused_img_path
        ).convert_alpha()
        self.unpaused_img: pygame.Surface = pygame.image.load(
            self.settings.control_panel.paused_indicator.unpaused_img_path
        ).convert_alpha()
        self._scale_images()

        super().__init__(cgol, self.paused_img.size)

    @property
    def surface(self) -> pygame.Surface:
        """Get the ``Surface`` of the paused indicator.

        Image depending on paused state of the game.
        Reminder: the Surface's Rect has no position.
        """
        return (self.paused_img
                if self.cgol.paused or self.cgol.event_handler.secondary_paused
                else self.unpaused_img)

    def _scale_images(self) -> None:
        """Scale the both images to fit the width defined in settings.

        Must be called in ``__init__()`` after defining the image surfaces.
        Both images will be the same size after calling.
        """
        ratio = self.paused_img.width / self.paused_img.height
        if ratio != self.unpaused_img.width / self.unpaused_img.height:
            raise RuntimeError("Images have different size ratios")

        target_width = self.settings.control_panel.paused_indicator.width
        target_height = target_width / ratio
        self.paused_img = pygame.transform.scale(
            self.paused_img, (target_width, target_height)
        )
        self.unpaused_img = pygame.transform.scale(
            self.unpaused_img, (target_width, target_height)
        )
