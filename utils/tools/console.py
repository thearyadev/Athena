from rich.console import Console as rich_console
from datetime import datetime


class Console(rich_console):
    def __init__(self):
        super().__init__(log_time=False, )
        self.root_console = super(self.__class__, self)

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


if __name__ == "__main__":
    console = Console()
    console.server_log("hello world")
    console.info_log("hello world")
    console.error_log("hello world")

    console.root_console.log("hi")
