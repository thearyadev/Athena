import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
from ..tools.Configuration import configuration
from nextcord.ext.commands.errors import CommandError
import sys
import shutil
from uuid import uuid4
import os


class general(commands.Cog, embeds):
    def __init__(self, client):
        self.client = client
        self.client.check(self.check_authorized)

    def check_authorized(self, ctx):
        """
        Only authorized servers may use commands in this bot.
         This checks that the guild is authorized before allowing commands go go through.
        :param ctx:
        :return:
        """

        if isinstance(ctx.message.channel, nextcord.DMChannel):
            if ctx.message.author.id == 305024830758060034:
                return True  # does not apply to DM channels from the bot owner.

        if "configure_manual" in ctx.message.content:
            return True  # does not apply if the bot owner is trying to configure the bot

        if ctx.message.author.id == 305024830758060034 and "authorize" in ctx.message.content:
            return True  # does not apply if the bot owner is trying to authorize the bot

        if "authorized" in self.client.configs.find_guild(ctx.guild.id).__dict__.keys():
            # does checks for the authorized state, raises an error if unauthorized.
            if not self.client.configs.find_guild(ctx.guild.id).__dict__['authorized']:
                raise CommandError(
                    "This server has not been authorized. Please contact the bot owner to authorize this server")
        else:
            raise CommandError(
                "This server has not been authorized. Please contact the bot owner to authorize this server")
        return True

    @commands.command(name="athena")
    async def athena(self, ctx):
        """
        info about the bot
        :param ctx:
        :return:
        """

        embed = nextcord.Embed(title="Hi! My name is Athena.",
                               description="I'm Athena, "
                                           "I am bot designed to help with team management, "
                                           "discord server moderation, and event management.\n Use `!help` to "
                                           "see my commands. ",
                               color=self.SUCCESS)
        embed.set_image(url="https://raw.githubusercontent.com/thearyadev/Athena/main/graphics/athena.png")
        embed.set_thumbnail(url=self.client.user.display_avatar)
        embed.add_field(name="Version", value=f"{self.client.configs.version}", inline=True)
        embed.add_field(name="Date of last upgrade", value=self.client.configs.upgrade_date, inline=True)

        await ctx.send(embed=embed)

    @commands.command("help")
    async def help(self, ctx, category=None):
        """
        :param category:
        :param ctx:
        :return:
        """
        if not category:
            await ctx.send(file=nextcord.File("./graphics/help.png"))
        else:
            category = category.lower()
            if category == "collections":
                await ctx.send(file=nextcord.File("./graphics/collections.png"))
            elif category == "moderation":
                await ctx.send(file=nextcord.File("./graphics/moderation.png"))
            elif category == "pugs":
                await ctx.send(file=nextcord.File("./graphics/pugs.png"))
            elif category == "general":
                await ctx.send(file=nextcord.File("./graphics/general.png"))
            elif category == "rsvp":
                await ctx.send(file=nextcord.File("./graphics/rsvp.png"))
            elif category == "scrim":
                await ctx.send(file=nextcord.File("./graphics/scrim.png"))
            else:
                raise ValueError(f"Invalid command category: '{category}'")

    @commands.command()
    async def setratioemoji(self, ctx, emoji: nextcord.Emoji):
        guild = self.client.configs.find_guild(ctx.guild.id)
        guild.ratio_emoji = emoji.id
        self.client.configs.refresh()
        await ctx.message.add_reaction(emoji=emoji)

