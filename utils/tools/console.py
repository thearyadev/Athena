from rich.console import Console as rich_console
from datetime import datetime
import inspect
import os


class Console(rich_console):
    """
    Uses rich.console.Console() to make standardized logging for the bot.
    """

    def __init__(self):
        super().__init__(log_time=False, log_path=False, )
        self.root_console = super(self.__class__, self)  # accessible if the original console is required.

    def server_log(self, *objects):
        self.log(
            f"[blue][{self.__get_time__()}][/blue] [bold][yellow][SERVER][/bold][/yellow]", *objects)

    def info_log(self, *objects):
        self.log(
            f"[blue][{self.__get_time__()}][/blue] [bold][magenta][INFO][/bold][/magenta]", *objects)

    def error_log(self, *objects):
        self.log(f"[blue][{self.__get_time__()}][/blue] [bold][red][ERROR][/bold][/red]",
                 *objects)

    @staticmethod
    def __get_time__():
        return datetime.now().strftime('%H:%M:%S')
