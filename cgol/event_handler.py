from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from . import ConwaysGameOfLife


class EventHandler:
    """Handle all pygame events."""
    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        self.cgol = cgol
        self.settings = cgol.settings

        self.paused: bool = True  # Start paused
        self.secondary_paused: bool = False
        self.mouse_button_down: int | None = None
        self.window_resized = False
        self.grid_size_synced = True  # With window size
        self.previous_mouse_pos: tuple[int, int] | None = None

    def handle_events(self):
        """Check for and respond to key presses and clicks"""
        window_just_resized = False
        for event in pygame.event.get():
            match event.type:
                case pygame.KEYDOWN:
                    self._handle_keydown_events(event)
                case pygame.MOUSEBUTTONDOWN:
                    self._handle_mousedown_events(event)
                case pygame.MOUSEBUTTONUP:
                    self._handle_mouseup_events()
                case pygame.MOUSEMOTION:
                    self._handle_mouse_movement_events(event)
                case pygame.WINDOWRESIZED:
                    window_just_resized = True
                    self._handle_window_resized_events()

                case pygame.QUIT:
                    self.cgol.running = False

            if not window_just_resized:
                self.window_resized = False

    def _handle_keydown_events(self, event: pygame.Event) -> None:
        """Respond to keydown events."""
        match event.key:
            # Toggle pause
            case pygame.K_SPACE:
                self.paused = not self.paused
            # Game speed
            case pygame.K_UP | pygame.K_RIGHT:
                self.settings.dynamic.increase_game_speed()
            case pygame.K_DOWN | pygame.K_LEFT:
                self.settings.dynamic.decrease_game_speed()
            # Reset grid
            case pygame.K_r:
                if not self.grid_size_synced:
                    self.cgol.grid.destroy()
                    self.cgol.grid.create_grid()
                    self.grid_size_synced = True
                else:
                    self.cgol.grid.clear_all_cells()
                self.paused = True
            # Show/hide control panel
            case pygame.K_c:
                self.cgol.control_panel.show = not self.cgol.control_panel.show

            # No key command for full screen for now.
            # There are two different types of "fullscreen" on macOS,
            # and it's very difficult to get around.

            # Quit
            case pygame.K_q:
                self.cgol.running = False

            # For debugging
            case pygame.K_d:
                pass

    def _handle_mousedown_events(self, event: pygame.Event) -> None:
        """Respond to mousedown events."""
        self.secondary_paused = True
        self.previous_mouse_pos = event.pos
        self.mouse_button_down = pygame.BUTTON_LEFT \
            if event.button == pygame.BUTTON_LEFT else pygame.BUTTON_RIGHT
        self._handle_manual_cell_editing(event)

    def _handle_mouseup_events(self) -> None:
        """Respond to mouseup events."""
        self.secondary_paused = False
        self.mouse_button_down = None

    def _handle_mouse_movement_events(self,
                                      event: pygame.Event) -> None:
        """Respond to mouse movement events."""
        if self.mouse_button_down is not None:
            self._handle_manual_cell_editing(event)
            self.previous_mouse_pos = event.pos

    def _handle_manual_cell_editing(self, event: pygame.Event) -> None:
        """Birth or kill cells based on mouse position and button pressed."""
        if self.mouse_button_down == pygame.BUTTON_LEFT:
            self.cgol.grid.birth_cells_on_line(self.previous_mouse_pos,
                                               event.pos)
        if self.mouse_button_down == pygame.BUTTON_RIGHT:
            self.cgol.grid.kill_cells_on_line(self.previous_mouse_pos,
                                              event.pos)

    def _handle_window_resized_events(self) -> None:
        """Respond to window resized events."""
        self.window_resized = True
        self.grid_size_synced = False

        new_width = max(self.settings.screen.min_width, self.cgol.screen.width)
        new_height = max(self.settings.screen.min_height,
                         self.cgol.screen.height)

        self.cgol.screen = pygame.display.set_mode(
            (new_width, new_height),
            flags=pygame.RESIZABLE if self.settings.screen.resizable else 0
        )
        self.cgol.alpha_canvas = pygame.Surface(
            self.cgol.screen.size, flags=pygame.SRCALPHA
        )

    def mouse_is_up(self) -> bool:
        """Check whether no mouse buttons are down."""
        return self.mouse_button_down is None

    def mouse_is_down(self):
        """Check whether any mouse button is down."""
        return self.mouse_button_down is not None
