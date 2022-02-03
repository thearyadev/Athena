import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import traceback
from ..tools.Embeds import embeds
from ..commands.RSVP import rsvp_options


class events(commands.Cog, embeds):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.console.info_log(f"Connection to Discord successful. Athena has logged in as {self.client.user}")
        await self.client.change_presence(
            status=nextcord.Status.dnd,
            activity=nextcord.Game(self.client.configs.rich_presence)
        )

        self.client.console.info_log(f"Status set to {self.client.configs.rich_presence}")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.client.console.info_log(
            f"Command Executed: '{ctx.command.name}' by {ctx.author.name}#{ctx.author.discriminator} in {ctx.guild.name}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.client.configs.add_guild(guild.id)
        self.client.configs.refresh()
        self.client.console.info_log(f"Guild: {guild.id} successfully joined.")

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     try:
    #         assert self.client.configs.find_guild(message.guild.id).__dict__['authorized'] == True
    #     except KeyError:
    #         raise PermissionError("This server has not been authorized yet.")
    #     except AssertionError:
    #         raise PermissionError("This server has not been authorized yet.")
