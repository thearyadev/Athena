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


class admin_configs(commands.Cog, embeds):
    """
    Admin config commands for the bot. Only works in DM channel from the bot owner.
    """
    LOAD = True
    NAME = "Admin Configs"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def version(self, ctx, *new_version):
        if new_version:
            self.client.configs.version = " ".join(new_version)
            await general.athena(context=self, ctx=ctx)
        else:
            raise ValueError("No version provided")

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def upgrade_date(self, ctx, *new_date):
        if new_date:
            self.client.configs.version = " ".join(new_date)
            await general.athena(context=self, ctx=ctx)
        else:
            raise ValueError("No date provided")

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def prefix(self, ctx, *new_prefix):
        if new_prefix:
            self.client.configs.version = " ".join(new_prefix)
            await ctx.send("Version updated to " + " ".join(new_prefix))
        else:
            raise ValueError("No prefix provided")

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def rich(self, ctx, *new_rich):
        if new_rich:
            await self.client.change_presence(
                status=nextcord.Status.dnd,
                activity=nextcord.Game(" ".join(new_rich))
            )
            await ctx.send("Rich presence updated to " + " ".join(new_rich))
        else:
            raise ValueError("No date provided")

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        self.client.configs.refresh()
        sys.exit(-1)

    @commands.command(name="gdd")
    @commands.dm_only()
    @commands.is_owner()
    async def get_data_dir(self, ctx):
        src = "./data"
        dst = f"./temp/{uuid4().hex}"
        shutil.make_archive(dst, "zip", src)
        await ctx.send(file=nextcord.File(dst + ".zip"))
        os.remove(dst + ".zip")

    @commands.command("authorize")
    @commands.guild_only()
    @commands.is_owner()
    async def authorize_bot_usage(self, ctx):

        self.client.configs.find_guild(ctx.guild.id).authorized = True
        self.client.configs.refresh()
        embed = nextcord.Embed(title="Guild Authorization",
                               description="This guild has been authorized. All commands are now activated. ",
                               color=self.SUCCESS)
        await ctx.send(embed=embed)

    @commands.command("deactivate")
    @commands.guild_only()
    @commands.is_owner()
    async def deactivate_bot_usage(self, ctx):
        self.client.configs.find_guild(ctx.guild.id).authorized = False
        self.client.configs.refresh()
        embed = nextcord.Embed(title="Guild Authorization",
                               description="This guild has been unauthorized. All commands are now deactivated. ",
                               color=self.SUCCESS)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def configure_manual(self, ctx):

        self.client.configs.add_guild(ctx.guild.id)
        embed = nextcord.Embed(title="Guild Configuration",
                               description="This guild has been configured.",
                               color=self.SUCCESS)
        await ctx.send(embed=embed)
