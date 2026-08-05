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

        self.mouse_down = False

    def handle_events(self):
        """Check for and respond to key presses and clicks"""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.cgol.running = False
                case pygame.KEYDOWN:
                    self._handle_keydown_events(event)
                case pygame.MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    self._handle_mousedown_events(event)
                case pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
                # case pygame.MOUSEMOTION
                case cell.CELL_CLICKED:
                    self._handle_cell_clicked(event)

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
        """Respond to mouse click events."""
        self.cgol.grid.detect_all_clicked_cells(event.pos, event.button)

    def _handle_cell_clicked(self, event: pygame.event.Event) -> None:
        """Respond to a cell clicked event."""
        gridx = event.dict["gridx"]
        gridy = event.dict["gridy"]
        target_cell = self.cgol.grid.get_cell(gridx, gridy)
        if event.button == pygame.BUTTON_LEFT:
            target_cell.live(instant=True)
        elif event.button == pygame.BUTTON_RIGHT:
            target_cell.die(instant=True)
