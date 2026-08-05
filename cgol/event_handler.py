from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife


class EventHandler:
    """Handle all pygame events."""
    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        self.cgol = cgol
        self.settings = cgol.settings

        self.mouse_button_down: int | None = None

    def handle_events(self):
        """Check for and respond to key presses and clicks"""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.cgol.running = False
                case pygame.KEYDOWN:
                    self._handle_keydown_events(event)
                case pygame.MOUSEBUTTONDOWN:
                    self._handle_mousedown_events(event)
                case pygame.MOUSEBUTTONUP:
                    self._handle_mouseup_events()
                case pygame.MOUSEMOTION:
                    self._handle_mouse_movement_events(event)

    def _handle_keydown_events(self, event: pygame.event.Event) -> None:
        """Respond to keydown events."""
        match event.key:
            # Toggle pause
            case pygame.K_SPACE:
                self.cgol.paused = not self.cgol.paused

            # Full screen control
            case pygame.K_ESCAPE:
                self.cgol.window.set_windowed()
            case pygame.K_f:
                self.cgol.window.set_fullscreen()

            # Quit
            case pygame.K_q:
                self.cgol.running = False

    def _handle_mousedown_events(self, event: pygame.event.Event) -> None:
        """Respond to mousedown events."""
        self.mouse_button_down = pygame.BUTTON_LEFT \
            if event.button == pygame.BUTTON_LEFT else pygame.BUTTON_RIGHT
        self._handle_manual_cell_editing(event)

    def _handle_mouseup_events(self) -> None:
        """Respond to mouseup events."""
        self.mouse_button_down = None

    def _handle_mouse_movement_events(self,
                                      event: pygame.event.Event) -> None:
        """Respond to mouse movement events."""
        self._handle_manual_cell_editing(event)

    def _handle_manual_cell_editing(self, event: pygame.event.Event) -> None:
        """Birth or kill cells based on mouse position and button pressed."""
        if self.mouse_button_down == pygame.BUTTON_LEFT:
            self.cgol.grid.birth_cell_at_pos(event.pos)
        if self.mouse_button_down == pygame.BUTTON_RIGHT:
            self.cgol.grid.kill_cell_at_pos(event.pos)

    def mouse_is_up(self) -> bool:
        """Check whether no mouse buttons are down."""
        return self.mouse_button_down is None

    def mouse_is_down(self):
        """Check whether any mouse button is down."""
        return self.mouse_button_down is not None
