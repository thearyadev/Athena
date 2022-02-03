import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
from ..tools.Configuration import configuration
from nextcord.ext.commands.errors import CommandError
import sys


class general(commands.Cog, embeds):
    def __init__(self, client):
        self.client = client
        self.client.check(self.check_authorized)

    def check_authorized(self, ctx):
        if "configure_manual" in ctx.message.content:
            return True

        if ctx.message.author.id == 305024830758060034 and "authorize" in ctx.message.content:
            return True

        if "authorized" in self.client.configs.find_guild(ctx.guild.id).__dict__.keys():
            if not self.client.configs.find_guild(ctx.guild.id).__dict__['authorized']:
                raise CommandError(
                    "This server has not been authorized. Please contact the bot owner to authorize this server")
        else:
            raise CommandError(
                "This server has not been authorized. Please contact the bot owner to authorize this server")
        return True

    @commands.command(name="athena")
    async def athena(self, ctx):
        embed = nextcord.Embed(title="Hi! My name is Athena.",
                               description="Hi. I'm Athena, "
                                           "I am bot designed to help with team management, "
                                           "discord server moderation, and event management.\n Use `!help` to "
                                           "see my commands. ",
                               color=self.SUCCESS)
        embed.add_field(name="Version", value=f"**{self.client.configs.version}**", inline=True)
        embed.add_field(name="Date of last upgrade", value=self.client.configs.upgrade_date, inline=True)

        await ctx.send(embed=embed)

    @commands.command("updateconfig", aliases=["uc"])
    @commands.is_owner()
    async def update_config(self, ctx, query, *value):

        if query in ['version', 'upgrade_date']:
            value = " ".join(value)
            if not value: raise ValueError("No value provided.")
            setattr(self.client.configs, query, value)
            self.client.configs.serialize("./data/configuration/config.pkl")
            self.client.configs = configuration.deserialize("./data/configuration/config.pkl")
            await self.athena(ctx)
            self.client.console.info_log(f"Application configuration updated. Changes: attr={query}; value={value}")
        else:
            raise ValueError("Unable to modify selected attribute for security and stability reasons.")

    @commands.command("command")
    async def commandlist(self, ctx):
        for command in self.client.walk_commands():
            print(command.name)

    @commands.command("authorize")
    async def authorize_bot_usage(self, ctx):
        if ctx.message.author.id == 305024830758060034:
            self.client.configs.find_guild(ctx.guild.id).authorized = True
            self.client.configs.refresh()
            embed = nextcord.Embed(title="Guild Authorization",
                                   description="This guild has been authorized. All commands are now activated. ",
                                   color=self.SUCCESS)
            await ctx.send(embed=embed)
        else:
            raise PermissionError(
                "Unauthorized usage of command 'authorize'. This command may only be used by the bot owner.")

    @commands.command("deactivate")
    async def deactivate_bot_usage(self, ctx):
        if ctx.message.author.id == 305024830758060034:
            self.client.configs.find_guild(ctx.guild.id).authorized = False
            self.client.configs.refresh()
            embed = nextcord.Embed(title="Guild Authorization",
                                   description="This guild has been unauthorized. All commands are now deactivated. ",
                                   color=self.SUCCESS)
            await ctx.send(embed=embed)
        else:
            raise PermissionError(
                "Unauthorized usage of command 'deactivate'. This command may only be used by the bot owner.")

    @commands.command()
    async def configure_manual(self, ctx):
        if ctx.message.author.id == 305024830758060034:
            self.client.configs.add_guild(ctx.guild.id)
            embed = nextcord.Embed(title="Guild Configuration",
                                   description="This guild has been configured.",
                                   color=self.SUCCESS)
            await ctx.send(embed=embed)
        else:
            raise PermissionError("Only the bot owner may run this command.")

    @commands.command()
    async def terminate(self, ctx):
        if ctx.message.author.id == 305024830758060034:
            sys.exit(0)
