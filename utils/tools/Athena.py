from abc import ABC
import nextcord
from nextcord.ext import commands
import logging
from rich.logging import RichHandler

from ..commands.RSVP import rsvp_options
from ..tools.Configuration import configuration
import sys
from .console import Console


class Athena(commands.Bot, ABC):
    """
    Client object for Discord bot. This class initializes the bot and loads all the Cogs.
    """

    def __init__(self, *args, **kwargs):

        self.console = Console()
        self.configs = configuration.deserialize("./data/configuration/config.pkl")  # loads config from serialized file

        self.console.info_log("Deserialized Configuration Data")
        super().__init__(*args, **kwargs, command_prefix="!>!")

        self.console.info_log("Logging Configured: './data/logs/nextcord.log'")
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
        from ..commands.Events import events
        self.add_cog(events(self))
        self.console.info_log("Loaded Module 'events'")
        from ..commands.Errors import errors
        self.add_cog(errors(self))
        self.console.info_log("Loaded Module 'errors'")
        from ..commands.Collections import collections
        self.add_cog(collections(self))
        self.console.info_log("Loaded Module 'collections'")
        from ..commands.Moderation import moderation
        self.add_cog(moderation(self))
        self.console.info_log("Loaded Module 'moderation'")
        from ..commands.General import general
        self.add_cog(general(self))
        self.console.info_log("Loaded Module 'general'")
        from ..commands.RSVP import rsvp
        self.add_cog(rsvp(self))
        self.console.info_log("Loaded Module 'rsvp'")
        from ..commands.RepairChannelOrder import repair_channel_order
        self.add_cog(repair_channel_order(self))
        self.console.info_log("Loaded Module 'repair_channel_order'")
        from ..commands.Scrim import scrim
        self.add_cog(scrim(self))
        self.console.info_log("Loaded Module 'scrim'")
        from ..commands.PUGs import pugs
        self.add_cog(pugs(self))
        self.console.info_log("Loaded Module 'pugs'")
        from ..commands.AdminConfigs import admin_configs
        self.add_cog(admin_configs(self))
        self.console.info_log("Loaded module 'admin_configs'")
