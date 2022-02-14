from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import nextcord
from ..tools.Embeds import embeds
import os
import sys
from uuid import uuid4
import shutil
import asyncio
from . import general
from ..tools import Guild
from ..tools.Athena import Athena

class database_modifiers(commands.Cog, embeds):
    """
    This is user-editable commands which link to the database.
    """
    LOAD = True
    NAME = "Database Modifiers"

    def __init__(self, client: Athena):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setratioemoji(self, ctx, emoji: nextcord.Emoji):
        guild = self.client.database.get(ctx.guild.id)
        guild.ratio_emoji = emoji.id
        self.client.database.update_guild(guild)
        await ctx.message.add_reaction(emoji=emoji)

