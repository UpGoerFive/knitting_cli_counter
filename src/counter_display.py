#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Header, Footer, Static

class CounterDisplay(App):
    """
    Display an individual knitting counter.
    """
    CSS_PATH = "counter.tcss"
    BINDINGS = [
            ("d", "toggle_dark", "Toggle dark mode"),
            ("a", "add_counter", "Add"),
            ("r", "remove_stopwatch", "Remove")
            ("j", "decrement", "Decrease counter value")
            ("k", "increment", "Increase counter value")
            ]

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        yield Header()
        yield Footer()
        yield ScrollableContainer(ProjectSettings())


    def action_toggle_dark(self) -> None:
        """
        An action to toggle dark mode.
        """
        self.dark = not self.dark





if __name__=="__main__":
    app = CounterDisplay()
    app.run()
