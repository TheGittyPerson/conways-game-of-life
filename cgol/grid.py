from typing import TYPE_CHECKING

import pygame

from cell import Cell

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife


class Grid:
    """Represent and control the grid of cells."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.cgol = cgol
        self.settings = cgol.settings

        self.cells_group = pygame.sprite.Group()
        self.cells_array: list[list[Cell]] = [[]]

    def update_all_cells(self) -> None:
        """Update the cells."""
        self.draw_all_cells()

    def create_grid(self) -> None:
        """Create a grid of cells.

        Fills the entire screen. Grid is centered so that any remaining
        margins are equal.
        """
        cell_width, cell_height = self.settings.cell.dimensions
        screen_width, screen_height = pygame.display.get_window_size()

        x_total_margin: int = screen_width % cell_width
        y_total_margin: int = screen_height % cell_height
        x_single_margin: int = x_total_margin // 2
        y_single_margin: int = y_total_margin // 2

        current_posx, current_posy = x_single_margin, y_single_margin
        current_gridx, current_gridy = 0, 0
        while current_posy < (screen_height - y_single_margin):
            while current_posx < (screen_width - x_single_margin):
                self._create_cell(
                    current_posx, current_posy, current_gridx, current_gridy
                )
                current_posx += cell_width
                current_gridx += 1

            current_posx = x_single_margin
            current_gridx = 0

            current_posy += cell_height
            current_gridy += 1

    def draw_all_cells(self) -> None:
        """Draw all cells."""
        self.cells_group.draw(self.cgol.screen)

    def get_cell(self, gridx: int, gridy: int) -> Cell:
        """Get the cell at the given grid position."""
        return self.cells_array[gridy][gridx]

    def handle_cell_clicked(self, event: pygame.event.Event) -> None:
        """Respond to a cell clicked event."""
        gridx = event.dict["gridx"]
        gridy = event.dict["gridy"]
        target_cell = self.get_cell(gridx, gridy)
        if event.button == pygame.BUTTON_LEFT:
            target_cell.live()
        elif event.button == pygame.BUTTON_RIGHT:
            target_cell.die()

    def detect_all_clicked_cells(self, mouse_pos: tuple[int, int]) -> None:
        """Detect for clicks on all cells."""
        for row in self.cells_array:
            for cell in row:
                cell.detect_click(mouse_pos)

    def _create_cell(self, posx: int, posy: int,
                     gridx: int, gridy: int) -> None:
        """Create a new cell."""
        new_cell = Cell(self.cgol, posx, posy, gridx, gridy)
        self.cells_group.add(new_cell)
        try:
            self.cells_array[gridy].append(new_cell)
        except IndexError:
            self.cells_array.append([new_cell])
