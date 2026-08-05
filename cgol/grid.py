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

    @property
    def rows(self) -> int:
        """Return the number of rows in this grid.

        Assume all rows are of the same length.
        """
        return len(self.cells_array)

    @property
    def columns(self) -> int:
        """Return the number of columns in this grid."""
        return len(self.cells_array[0])

    def update_all_cells(self) -> None:
        """Update all cell states and their colors.

        If the game is paused, next alive states will not be calculated.
        However, user-induced changes will always be registered (manually
        aliving/unaliving a cell will instantly update the cell's state and
        color).

        User-induced changes are detected and controlled in ``EventHandler``.
        """
        flattened = self.get_flattened_cells_array()
        paused = self.cgol.paused

        if not paused:
            for cell in flattened:
                cell.update_next_alive_state()
        for cell in flattened:
            if not paused:
                cell.use_next_alive_state()
            cell.update_color()

        self.draw_all_cells()

    def create_grid(self) -> None:
        """Create a grid of cells.

        Fill the entire screen. Grid is centered so that any remaining
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

    def get_cell(self, gridx: int, gridy: int) -> Cell | None:
        """Get the cell at the given grid position.

        Return ``None`` if the coordinate falls outside the grid.
        """
        if 0 <= gridx < self.columns and 0 <= gridy < self.rows:
            return self.cells_array[gridy][gridx]
        return None

    def detect_all_clicked_cells(self, mouse_pos: tuple[int, int],
                                 button: int) -> None:
        """Detect for clicks on all cells."""
        for row in self.cells_array:
            for cell in row:
                cell.detect_click(mouse_pos, button)

    def _create_cell(self, posx: int, posy: int,
                     gridx: int, gridy: int) -> None:
        """Create a new cell."""
        new_cell = Cell(self.cgol, posx, posy, gridx, gridy)
        self.cells_group.add(new_cell)
        try:
            self.cells_array[gridy].append(new_cell)
        except IndexError:
            self.cells_array.append([new_cell])

    def get_flattened_cells_array(self):
        return [cell for row in self.cells_array for cell in row]
