import pygame

from grid import Grid
from event_handler import EventHandler
from settings import Settings


class ConwaysGameOfLife:
    """Control and manage a new Game of Life."""

    def __init__(self):
        """Initialize attributes"""
        pygame.init()

        self.clock = pygame.time.Clock()
        self.settings: Settings = Settings()
        self.event_handler: EventHandler = EventHandler(self)

        self.window = pygame.Window(
            title=self.settings.title,
            size=self.settings.window.dimensions,
        )
        self.screen = self.window.get_surface()

        self.grid = Grid(self)

        self.running: bool = False
        self.paused: bool = True  # Start paused

    def run(self) -> None:
        """Run the main event loop."""
        self.running = True

        self.screen.fill(self.settings.window.bg_color)
        self.grid.create_grid()
        while self.running:
            self.event_handler.handle_events()
            self._update_screen()

            self.clock.tick(self.settings.max_fps)

        self._stop()

    def _update_screen(self) -> None:
        """Update the screen."""
        self.screen.fill(self.settings.window.bg_color)
        self.grid.update_all_cells()

        self.window.flip()

    @staticmethod
    def _stop():
        """Stop the game."""
        pygame.quit()
