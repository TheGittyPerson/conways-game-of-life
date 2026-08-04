from typing import TYPE_CHECKING

import pygame
from pygame.sprite import Sprite

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife

CELL_CLICKED = pygame.event.custom_type()


class Cell(Sprite):
    """Represent a single cell."""
    def __init__(self, cgol: ConwaysGameOfLife, posx: int, posy: int,
                 gridx: int, gridy: int,) -> None:
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

    def update(self) -> None:
        """Update the state and color of this cell."""
        if self.cgol.paused:
            return
        neighbors: int = self._count_living_neighbors()
        if neighbors < 2:
            self.die()
        elif neighbors == 3:
            self.live()
        elif neighbors > 3:
            self.die()
        self._update_color()

    def _update_color(self) -> None:
        """Update the color of this cell."""
        self.color = self.settings.cell.alive_color if self.alive \
            else self.settings.cell.dead_color
        self.image.fill(self.color)

    def live(self) -> None:
        """Set ``alive`` to ``True``."""
        self.alive = True

    def die(self) -> None:
        """Set ``alive`` to ``False``."""
        self.alive = False

    @classmethod
    def is_alive(cls, cell: Cell) -> bool:
        """Check if this cell is alive."""
        return cell.alive

    def _count_living_neighbors(self) -> int:
        """Count number of adjacent living neighbors."""
        return len(list(filter(self.is_alive, [
            self.cgol.grid.get_cell(self.posx + dx, self.posy + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == dy == 0)
        ])))

    def detect_click(self, mouse_pos: tuple[int, int]) -> None:
        """Check if clicked and raise a custom event."""
        if self.rect.collidepoint(mouse_pos):
            event_data = {"gridx": self.gridx, "gridy": self.gridy}
            cell_event = pygame.event.Event(CELL_CLICKED, event_data)
            pygame.event.post(cell_event)
