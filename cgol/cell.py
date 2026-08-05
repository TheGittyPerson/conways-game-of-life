from typing import TYPE_CHECKING

import pygame
from pygame.sprite import Sprite

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife

CELL_CLICKED = pygame.event.custom_type()


class Cell(Sprite):
    """Represent a single cell."""

    def __init__(self, cgol: ConwaysGameOfLife, posx: int, posy: int,
                 gridx: int, gridy: int, ) -> None:
        """Initialize the cell.

        `posx` and `posy` are the coordinates of the cell's top left corner.
        `gridx` and `gridy` represent the position of the cell in the cell
        grid. (0, 0) is the topmost and leftmost cell.
        """
        super().__init__()

        self.cgol = cgol
        self.settings = cgol.settings

        self.posx = posx
        self.posy = posy
        self.gridx = gridx
        self.gridy = gridy

        self.color = self.settings.cell.dead_color
        self._image = pygame.Surface(self.settings.cell.dimensions)
        self._image.fill(self.color)
        self._rect = pygame.Rect(
            (self.posx, self.posy), self.settings.cell.dimensions
        )

        self.alive: bool = False
        self.next_alive_state: bool = False

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @image.setter
    def image(self, value: pygame.Surface):
        self._image = value

    @property
    def rect(self) -> pygame.Rect | pygame.FRect:
        return self._rect

    @rect.setter
    def rect(self, value: pygame.Rect | pygame.FRect):
        self._rect = value

    def update_next_alive_state(self) -> None:
        """Update the ``next_alive_state`` of this cell based on neighbors.

        ``next_alive_state`` is updated, NOT ``alive``.
        """
        neighbors: int = self._count_living_neighbors()
        if neighbors < 2:
            self.die()
        elif neighbors == 2:
            self.next_alive_state = self.alive
        elif neighbors == 3:
            self.live()
        elif neighbors > 3:
            self.die()

    def use_next_alive_state(self) -> None:
        """Set ``alive`` to ``next_alive_state``."""
        self.alive = self.next_alive_state

    def update_color(self) -> None:
        """Update the color of this cell and fill its image."""
        self.color = self.settings.cell.alive_color if self.alive \
            else self.settings.cell.dead_color
        self.image.fill(self.color)

    def live(self, instant: bool = False) -> None:
        """Set ``alive`` to ``True``.

        If ``instant`` is ``False``, ``next_alive_state`` will be changed
        rather than ``alive``. ``alive`` is changed directly when
        ``instant`` is ``True``.
        """
        if instant:
            self.alive = True
        else:
            self.next_alive_state = True

    def die(self, instant: bool = False) -> None:
        """Set ``next_alive_state`` to ``False``.

        If ``instant`` is ``False``, ``next_alive_state`` will be changed
        rather than ``alive``. ``alive`` is changed directly when
        ``instant`` is ``True``.
        """
        if instant:
            self.alive = False
        else:
            self.next_alive_state = False

    @classmethod
    def is_alive(cls, cell: Cell | None) -> bool:
        """Check if this cell is alive.

        Accepts ``None`` (and returns ``False``) to support
        ``_count_living_neighbors()``.
        """
        if cell is None:
            return False
        return cell.alive

    def detect_click(self, mouse_pos: tuple[int, int], button: int) -> None:
        """Check if clicked and raise a custom event."""
        if self.rect.collidepoint(mouse_pos):
            event_data = {
                "gridx": self.gridx, "gridy": self.gridy,
                "button": button
            }
            cell_event = pygame.event.Event(CELL_CLICKED, event_data)
            pygame.event.post(cell_event)

    def _count_living_neighbors(self) -> int:
        """Count number of adjacent living neighbors."""
        return len(list(filter(self.is_alive, [
            self.cgol.grid.get_cell(self.gridx + dx, self.gridy + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == dy == 0)
        ])))
