from typing import TYPE_CHECKING

import pygame

import cell

if TYPE_CHECKING:
    from cgol import ConwaysGameOfLife


class EventHandler:
    """Handle all pygame events."""
    def __init__(self, cgol: ConwaysGameOfLife) -> None:
        self.cgol = cgol
        self.settings = cgol.settings

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
                case cell.CELL_CLICKED:
                    self.cgol.grid.handle_cell_clicked(event)

    def _handle_keydown_events(self, event: pygame.event.Event) -> None:
        """Respond to keydown events."""
        match event.key:
            # Toggle pause
            case pygame.K_k:
                self.cgol.paused = not self.cgol.paused

            # Full screen control
            case pygame.K_ESCAPE if pygame.display.is_fullscreen():
                pygame.display.toggle_fullscreen()
            case pygame.K_f if not pygame.display.is_fullscreen():
                pygame.display.toggle_fullscreen()

            # Quit
            case pygame.K_q:
                self.cgol.running = False

    def _handle_mousedown_events(self, event: pygame.event.Event) -> None:
        """Respond to mouse click events."""
        self.cgol.grid.detect_all_clicked_cells(event.pos)
