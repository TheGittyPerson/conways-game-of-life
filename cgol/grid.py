from collections import Counter
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

    @property
    def x_single_margin(self) -> int:
        """Return the width of the left margin of the grid of cells."""
        cell_width = self.settings.cell.width
        screen_width = self.cgol.screen.get_width()
        x_total_margin = screen_width % cell_width
        return x_total_margin // 2

    @property
    def y_single_margin(self) -> int:
        """Return the height of the top margin of the grid of cells."""
        cell_height = self.settings.cell.height
        screen_height = self.cgol.screen.get_height()
        y_total_margin = screen_height % cell_height
        return y_total_margin // 2

    def update_all_cells(self) -> None:
        """Update all cell states and their colors and draw to screen.

        If the game is paused, next alive states will not be calculated.
        However, user-induced changes will always be registered (manually
        aliving/unaliving a cell will instantly update the cell's state and
        color).

        User-induced changes are detected and controlled in ``EventHandler``.
        """
        flattened = self.get_flattened_cells_array()
        paused = self.cgol.paused

        if not paused:
            self._update_all_next_alive_states()

        for cell in flattened:
            cell.use_next_alive_state()
            cell.update_color()

        self.draw_all_cells()

    def _update_all_next_alive_states(self):
        """Update the next alive states of all cells.

        Optimized to only check relevant cells that are alive or are next to
        living cells.
        """
        offset_coords: list[tuple[int, int]] = [
            (dx, dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == dy == 0)
        ]

        living_cells: list[Cell] = self.get_living_cells()
        neighbor_counter: Counter[Cell | None] = Counter(
            dict.fromkeys(living_cells, 0)
        )

        for cell in living_cells:
            for offset in offset_coords:
                neighbor_cell = self.get_cell(
                    cell.gridx + offset[0], cell.gridy + offset[1]
                )
                neighbor_counter[neighbor_cell] += 1

        for cell in neighbor_counter:
            if cell is None:
                continue
            cell.update_next_alive_state(neighbor_counter[cell])

    def create_grid(self) -> None:
        """Create a grid of cells.

        Fill the entire screen. Grid is centered so that any remaining
        margins are equal.
        """
        cell_width, cell_height = self.settings.cell.dimensions
        screen_width, screen_height = self.cgol.screen.get_size()

        current_posx, current_posy = self.x_single_margin, self.y_single_margin
        current_gridx, current_gridy = 0, 0
        while current_posy < (screen_height - self.y_single_margin):
            while current_posx < (screen_width - self.x_single_margin):
                self._create_cell(
                    current_posx, current_posy, current_gridx, current_gridy
                )
                current_posx += cell_width
                current_gridx += 1

            current_posx = self.x_single_margin
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

    def birth_cell_at_pos(self, mouse_pos: tuple[int, int]) -> None:
        """Make alive the cell in which the given mouse position lands.

        Do nothing if the mouse is outside the grid.
        """
        target_cell = self.get_cell_at_pos(mouse_pos)
        if target_cell is None:
            return
        target_cell.live()

    def kill_cell_at_pos(self, mouse_pos: tuple[int, int]) -> None:
        """Kill the cell in which the given mouse position lands.

        Do nothing if the mouse is outside the grid.
        """
        target_cell = self.get_cell_at_pos(mouse_pos)
        if target_cell is None:
            return
        target_cell.die()

    def get_cell_at_pos(self, mouse_pos: tuple[int, int]) -> Cell | None:
        """Get the cell in which the given mouse position lands.

        Return None if the mouse is outside the grid.
        """
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        gridx = (mouse_x - self.x_single_margin) // self.settings.cell.width
        gridy = (mouse_y - self.y_single_margin) // self.settings.cell.height
        cell = self.get_cell(gridx, gridy)
        return cell

    def _create_cell(self, posx: int, posy: int,
                     gridx: int, gridy: int) -> None:
        """Create a new cell."""
        new_cell = Cell(self.cgol, posx, posy, gridx, gridy)
        self.cells_group.add(new_cell)
        try:
            self.cells_array[gridy].append(new_cell)
        except IndexError:
            self.cells_array.append([new_cell])

    def get_living_cells(self) -> list[Cell]:
        """Get a list of living cells"""
        return [cell for cell in self.get_flattened_cells_array()
                if cell.alive]

    def get_flattened_cells_array(self):
        return [cell for row in self.cells_array for cell in row]
