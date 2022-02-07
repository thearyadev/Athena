from abc import ABC
import nextcord
from nextcord.ext import commands
import logging
from rich.logging import RichHandler

from ..commands.RSVP import rsvp_options
from ..tools.Configuration import configuration
import sys
from .console import Console
from .STDERRredirect import Redirect
from .Database import GuildDatabase

import inspect


class Athena(commands.Bot, ABC):
    """
    Client object for Discord bot. This class initializes the bot and loads all the Cogs.
    """

    def __init__(self, *args, **kwargs):

        self.console = Console()
        self.configs = configuration.deserialize("./data/configuration/config.pkl")  # loads config from serialized file
        self.console.info_log("Deserialized Configuration Data")
        super().__init__(*args, **kwargs, command_prefix="!>!")
        self.remove_command("help")
        self.console.info_log("Logging Configured: ./data/logs/nextcord.log")
        nc_logger = logging.getLogger("nextcord")  # nextcord logger
        nc_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=r'./data/logs/nextcord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        nc_logger.addHandler(handler)
        self.command_prefix = self.configs.prefix
        self.console.info_log(f"Command prefix set to {self.configs.prefix}")
        self.persistent_views_added = False
        self.__load_extensions__()  # loads extensions
        self.console.info_log(f"Cogs loaded successfully")
        sys.stderr = Redirect(file_path="./data/logs/errors.log", print=False, console=self.console)
        self.console.info_log("__stderr__ redirected to ./data/logs/error.log")
        self.database: GuildDatabase = GuildDatabase("./data/guilds/guilds.db", console=self.console)

    async def on_ready(self):
        if not self.persistent_views_added:
            from ..commands.RSVP import rsvp_options
            # register persistent views
            # self.add_view(rsvp_options())
            self.persistent_views_added = True

    def initialize(self, mode="-t"):
        if mode == "-t":
            self.console.info_log("Starting bot in [red]TESTING[/red] mode.")
            self.run(self.configs.testing_token)
        elif mode == "-d":
            self.console.info_log("Starting bot in [red]DISTRIBUTION[/red] mode.")
            self.run(self.configs.token)

    def __load_extensions__(self):
        from .. import commands
        for name, extension in inspect.getmembers(commands):
            if inspect.isclass(extension):
                if hasattr(extension, "LOAD"):
                    if extension.LOAD:
                        self.add_cog(extension(self))
                        if hasattr(extension, "NAME"):
                            self.console.info_log(f"Loaded extension [yellow]>> {extension.NAME}[yellow]")
                        else:
                            self.console.info_log(f"Loaded extension [yellow]>> {name}[yellow]")
                    else:
                        self.console.info_log(f"Skipping module [red]>> {name}[red]")
                else:
                    self.console.error_log(f"Unknown module imported [red]>> {name}[red]")
