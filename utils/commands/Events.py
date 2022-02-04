import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import traceback
from ..tools.Embeds import embeds
from ..commands.RSVP import rsvp_options


class events(commands.Cog, embeds):
    """
    Nextcord events
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.console.info_log(f"Connection to Discord successful. Athena has logged in as {self.client.user}")
        await self.client.change_presence(
            status=nextcord.Status.dnd,
            activity=nextcord.Game(self.client.configs.rich_presence)
        )  # sets rich presence to value defined in config.pkl

        self.client.console.info_log(f"Status set to {self.client.configs.rich_presence}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """
        logs all the commands that are used
        :param ctx:
        :return:
        """
        try:
            self.client.console.info_log(
                f"Command Executed: '{ctx.command.name}' by {ctx.author.name}#{ctx.author.discriminator} in {ctx.guild.name}")
        except AttributeError: # raises attribute error if the channel is a DM channel.
            self.client.console.info_log(
                f"Command Executed: '{ctx.command.name}' by {ctx.author.name}#{ctx.author.discriminator} in DM_CHANNEL")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        when the bot joins a guild, it updates the configs file by adding a guild so more server specific settings can be added.

        :param guild:
        :return:
        """
        self.client.configs.add_guild(guild.id)
        self.client.configs.refresh()
        self.client.console.info_log(f"Guild: {guild.id} successfully joined.")
