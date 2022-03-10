from abc import ABC
import nextcord
from nextcord.ext import commands
import logging
from rich.logging import RichHandler
from ..tools.Configuration import configuration
import sys
from .console import Console
from .STDERRredirect import Redirect
from .Database import GuildDatabase
import inspect


class Athena(commands.Bot):
    """
    Client object for Discord bot. This class initializes the bot and loads all the Cogs.
    """

    DISTRIBUTION = "-d"
    TESTING = "-t"
    INACTIVE = "-i"

    def __init__(self, *args, **kwargs):
        self.mode = self.INACTIVE
        self.console = Console()
        self.configs: configuration = configuration.deserialize(
            "./data/configuration/config.pkl")  # loads config from serialized file
        self.console.info_log("Deserialized Configuration Data")
        intents = nextcord.Intents.all()
        intents.members = True
        super().__init__(*args, **kwargs, command_prefix="!>!", intents=intents)
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
        self.console.info_log(f"Extensions loaded successfully")
        sys.stderr = Redirect(file_path="./data/logs/errors.log", print=False,
                              console=self.console)  # start redirecting stderr
        self.console.info_log("__stderr__ redirected to ./data/logs/error.log")

        self.database: GuildDatabase = GuildDatabase("./data/guilds/guilds.db", console=self.console)

    async def on_ready(self):
        if not self.persistent_views_added:
            from ..commands.RSVP import rsvp_options
            from ..commands.General import Verify
            # register persistent views

            self.add_view(Verify(self.console))
            self.add_view(rsvp_options(self.console, reloaded=True))
            self.persistent_views_added = True

    def initialize(self, mode=TESTING):
        if mode == self.TESTING:
            self.mode = self.TESTING
            self.console.info_log("Starting bot in [red]TESTING[/red] mode.")
            self.run(self.configs.testing_token)

        elif mode == self.DISTRIBUTION:
            self.mode = self.DISTRIBUTION
            self.console.info_log("Starting bot in [red]DISTRIBUTION[/red] mode.")
            self.run(self.configs.token)

    def __load_extensions__(self):
        from .. import commands  # loads all available commands from commands packaged
        for name, extension in inspect.getmembers(commands):  # inspects all members of this reference
            if inspect.isclass(extension):  # checks if the member is a class
                if hasattr(extension, "LOAD"):  # If the class is a commands object then it will have the LOAD attribute
                    if extension.LOAD:  # if LOAD is true
                        self.add_cog(extension(self))  # add the cog, pass in Athena as the client object
                        if hasattr(extension, "NAME"):
                            self.console.info_log(f"Loaded extension [yellow]>> {extension.NAME}[yellow]")
                        else:
                            self.console.info_log(f"Loaded extension [yellow]>> {name}[yellow]")
                    else:
                        self.console.info_log(f"Skipping module [red] >> {extension.NAME}[red]")
                else:
                    self.console.error_log(f"Unknown module imported [red]>> {name}[red]")
