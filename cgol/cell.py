from typing import TYPE_CHECKING

import pygame
from pygame.sprite import Sprite

if TYPE_CHECKING:
    from . import ConwaysGameOfLife


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
        self.grid = self.cgol.grid
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

    def update_next_alive_state(self, neighbors: int) -> None:
        """Update ``next_alive_state`` based on the # of living neighbors.

        ``next_alive_state`` is updated, NOT ``alive``.
        """
        if neighbors < 2:
            self.die()
        elif neighbors == 3:
            self.live()
        elif neighbors > 3:
            self.die()

    def use_next_alive_state(self) -> None:
        """Set ``alive`` to ``next_alive_state``, update population count.

        Of the Grid, this method updates:
            - Population count
            - Living cells set
        """
        if self.alive != self.next_alive_state:
            if self.next_alive_state:
                self.grid.population += 1
                self.grid.living_cells.add(self)
            else:
                self.grid.population -= 1
                if self in self.grid.living_cells:
                    self.grid.living_cells.remove(self)
            self.alive = self.next_alive_state

    def update_color(self) -> None:
        """Update the color of this cell and fill its image."""
        self.color = self.settings.cell.alive_color if self.alive \
            else self.settings.cell.dead_color
        self.image.fill(self.color)

    def live(self) -> None:
        """Set ``next_alive_state`` to ``True``."""
        self.next_alive_state = True

    def die(self) -> None:
        """Set ``next_alive_state`` to ``False``"""
        self.next_alive_state = False

    def kill(self) -> None:
        """Alias for ``die()``."""
        self.die()
