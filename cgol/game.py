import pygame

from . import Settings, Grid, EventHandler, ControlPanel


class ConwaysGameOfLife:
    """Control and manage a new Game of Life."""

    def __init__(self):
        """Initialize attributes"""
        pygame.init()

        self.clock = pygame.time.Clock()
        self.settings: Settings = Settings()

        self.screen = pygame.display.set_mode(
            self.settings.screen.dimensions,
            flags=pygame.RESIZABLE if self.settings.screen.resizable else 0
        )
        pygame.display.set_caption(self.settings.title)
        # For elements that need opacity
        self.alpha_canvas = pygame.Surface(
            self.settings.screen.dimensions, flags=pygame.SRCALPHA
        )

        self.grid = Grid(self)
        self.events: EventHandler = EventHandler(self)
        self.control_panel = ControlPanel(self)

        self.running: bool = False

    def run(self) -> None:
        """Run the main event loop."""
        self.running = True

        self.screen.fill(self.settings.screen.bg_color)
        self.grid.create_grid()
        while self.running:
            self.events.handle_events()
            self._update_screen()

            self.clock.tick(self.settings.max_fps)

        self._stop()

    def _update_screen(self) -> None:
        """Update the screen."""
        self.screen.fill(self.settings.screen.bg_color)
        self.alpha_canvas.fill((0, 0, 0, 0))
        self.grid.update_all_cells()
        self.grid.draw_all_cells()
        if self.control_panel.show:
            self.control_panel.draw()
        self.screen.blit(self.alpha_canvas, (0, 0))

        pygame.display.flip()

    @staticmethod
    def _stop():
        """Stop the game."""
        pygame.quit()
