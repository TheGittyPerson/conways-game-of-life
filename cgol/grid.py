from collections import Counter
from typing import TYPE_CHECKING

import pygame

from . import Cell

if TYPE_CHECKING:
    from . import ConwaysGameOfLife


class Grid:
    """Represent and control the grid of cells."""

    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        """Initialize attributes."""
        self.cgol = cgol
        self.settings = cgol.settings

        self.cells_group = pygame.sprite.Group()
        self.cells_array: list[list[Cell]] = []
        self.flat_cells_array: list[Cell] = []
        self.living_cells: set[Cell] = set()
        self.changed_cells: set[Cell] = set()
        self.population: int = 0
        self.num_rows: int = 0
        self.num_cols: int = 0

        self.update_accumulator: float = 0.0

    @property
    def x_single_margin(self) -> int:
        """Return the width of the left margin of the grid of cells."""
        cell_width = self.settings.cell.width
        # Dynamically changed in EventHandler window resized event
        screen_width = self.settings.screen.width
        x_total_margin = screen_width % cell_width
        return x_total_margin // 2

    @property
    def y_single_margin(self) -> int:
        """Return the height of the top margin of the grid of cells."""
        cell_height = self.settings.cell.height
        # Dynamically changed in EventHandler window resized event
        screen_height = self.settings.screen.height
        y_total_margin = screen_height % cell_height
        return y_total_margin // 2

    # ======================== MAIN GRID UPDATING LOOP ========================

    def update_all_cells(self) -> None:
        """Update all cell states and their colors and draw to screen.

        Also increment generation count.

        If the game is paused, next alive states will not be calculated.
        However, user-induced changes will always be registered (manually
        aliving/unaliving a cell will instantly update the cell's state and
        color).

        Resets changed cells set after updating.

        User-induced changes are detected and controlled in ``EventHandler``.
        """
        paused = self.cgol.events.paused or self.cgol.events.secondary_paused

        if not paused:
            self._increment_accumulator()
            while self.update_accumulator >= 1.0:
                self._compute_next_generation()
                for cell in self.changed_cells:
                    cell.use_next_alive_state()
                self.update_accumulator -= 1.0
                self.cgol.generations += 1

        for cell in self.changed_cells:
            cell.use_next_alive_state()
            cell.update_color()

        self.changed_cells = set()

    def _increment_accumulator(self) -> None:
        """Increment the accumulator by the game speed (gens per frame)."""
        self.update_accumulator += self.settings.dynamic.game_speed

    # ========================= CELL UPDATING/EDITING =========================

    # NATURAL GENERATION PROGRESSION

    def _compute_next_generation(self) -> None:
        """Update the next alive states of all cells.

        Optimized to only check relevant cells that are alive or are next to
        living cells. Update changed cells set.
        """
        offset_coords: list[tuple[int, int]] = [
            (dx, dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == dy == 0)
        ]

        neighbor_counter: Counter[Cell | None] = Counter(
            dict.fromkeys(self.living_cells, 0)
        )

        for cell in self.living_cells:
            for offset in offset_coords:
                neighbor_cell = self.get_cell(
                    cell.gridx + offset[0], cell.gridy + offset[1]
                )
                neighbor_counter[neighbor_cell] += 1

        neighbor_counter.pop(None, None)
        neighbor_counter: Counter[Cell]
        for cell in neighbor_counter:
            cell.update_next_alive_state(neighbor_counter[cell])
            self.changed_cells.add(cell)

    # USER EDITS

    def birth_cells_on_line(self, pos1: tuple[int, int],
                            pos2: tuple[int, int]) -> None:
        """Make alive all cells between the given coordinates."""
        for cell in self.get_cells_on_line(pos1, pos2):
            cell.live()
            self.changed_cells.add(cell)
            self.living_cells.add(cell)

    def kill_cells_on_line(self, pos1: tuple[int, int],
                           pos2: tuple[int, int]) -> None:
        """Kill all cells between the given coordinates."""
        for cell in self.get_cells_on_line(pos1, pos2):
            cell.die()
            self.changed_cells.add(cell)
            if cell in self.living_cells:
                self.living_cells.remove(cell)

    # ========================= GRID CREATION =========================

    def create_grid(self) -> None:
        """Initialize a grid of cells.

        Grid fills the entire screen. Grid is centered so that any remaining
        margins are equal.
        """
        cell_width, cell_height = self.settings.cell.dimensions
        screen_width, screen_height = self.settings.screen.dimensions

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
        self.num_rows = len(self.cells_array)
        self.num_cols += len(self.cells_array[0])

    def draw_all_cells(self) -> None:
        """Draw all cells."""
        self.cells_group.draw(self.cgol.screen)

    def _create_cell(self, posx: int, posy: int,
                     gridx: int, gridy: int) -> None:
        """Create a new cell and add it to the cells group and arrays."""
        new_cell = Cell(self.cgol, posx, posy, gridx, gridy)
        self.cells_group.add(new_cell)
        if len(self.cells_array) - 1 >= gridy:
            self.cells_array[gridy].append(new_cell)
        else:
            self.cells_array.append([new_cell])
        self.flat_cells_array.append(new_cell)

    # ========================= CELL-GETTING APIS =========================

    def get_cell(self, gridx: int, gridy: int) -> Cell | None:
        """Get the cell at the given grid position.

        Return ``None`` if the coordinate falls outside the grid.
        """
        if 0 <= gridx < self.num_cols and 0 <= gridy < self.num_rows:
            return self.cells_array[gridy][gridx]
        return None

    def get_cell_at_pos(self, pos: tuple[int, int]) -> Cell | None:
        """Get the cell in which the given coordinate lands.

        Return None if the coordinate is outside the grid.
        """
        mouse_x = pos[0]
        mouse_y = pos[1]
        gridx = (mouse_x - self.x_single_margin) // self.settings.cell.width
        gridy = (mouse_y - self.y_single_margin) // self.settings.cell.height
        cell = self.get_cell(gridx, gridy)
        return cell

    def get_cells_on_line(self, pos1: tuple[int, int],
                          pos2: tuple[int, int]) -> list[Cell]:
        """Return all cells that fall between the given coordinates."""
        coords: list[tuple[int, int]] = self._get_coords_on_line(pos1, pos2)
        return list(set([
            cell for pos in coords
            if (cell := self.get_cell_at_pos(pos)) is not None
        ]))

    @staticmethod
    def _get_coords_on_line(pos1: tuple[int, int],
                            pos2: tuple[int, int],
                            step_size: float = 1) -> list[tuple[int, int]]:
        """Return all coordinates that fall between the given points.

        ``step_size`` is the distance (in px) between each point to calculate.
        A smaller number means denser points and therefore a larger list of
        coordinates.
        """
        v1 = pygame.math.Vector2(pos1)
        v2 = pygame.math.Vector2(pos2)
        distance: float = v1.distance_to(v2)

        steps = int(distance / step_size) + 1

        coords: list[tuple[int, int]] = []
        for step_num in range(steps):
            current_dist_along_line = step_num / max(steps, 1)
            point: pygame.math.Vector2 = v1.lerp(v2, current_dist_along_line)
            coords.append((int(point.x), int(point.y)))

        return coords

    # ========================= CLEARING / RESETTING =========================

    def clear_all_cells(self) -> None:
        """Kill all cells and update colors, effectively resetting the grid.

        Also reset generation count and cached living cells count.
        """
        self.cgol.generations = 0
        self.population = 0
        self.changed_cells = set()
        for cell in self.living_cells:
            cell.alive = False
            cell.next_alive_state = False
            cell.update_color()
        self.living_cells = set()

    def destroy(self):
        """Empty cell Group and arrays to free memory immediately.

        Also reset generation count and cached living cells count.
        """
        self.cgol.generations = 0
        self.population = 0
        self.num_cols = self.num_rows = 0
        self._clear_cell_group_and_all_cell_arrays()

    def _clear_cell_group_and_all_cell_arrays(self):
        """Empty cell Group and arrays to free memory immediately."""
        self.cells_group.empty()
        self.cells_array.clear()
        self.flat_cells_array.clear()
        self.living_cells.clear()
        self.changed_cells.clear()
