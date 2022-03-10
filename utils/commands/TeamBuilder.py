import asyncio
import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
import uuid
import datetime
import os
from ..tools.Athena import Athena


class team_builder(commands.Cog, embeds):
    LOAD = True
    NAME = "Team Builder"

    def __init__(self, client: Athena):
        self.client = client

    @commands.command(name="addteam")
    async def add_team(self, ctx, *name):
        name = " ".join(name)
        category = await ctx.guild.create_category_channel(name=name)
        team_role = await ctx.guild.create_role(name=f"{name}")
        tryout_role = await ctx.guild.create_role(name=f"{name} Tryout")
        ringer_role = await ctx.guild.create_role(name=f"{name} Ringer")
        staff_role = await ctx.guild.create_role(name=f"{name} Staff")
        everyone = ctx.guild.default_role
        moderator = nextcord.utils.get(ctx.guild.roles, id=951245208287334410)

        await category.set_permissions(everyone, view_channel=False)
        await category.set_permissions(team_role, view_channel=True, connect=True)
        await category.set_permissions(tryout_role, view_channel=True, connect=True)
        await category.set_permissions(ringer_role, view_channel=True, connect=True)
        await category.set_permissions(staff_role, view_channel=True, connect=True)
        # await category.set_permissions(moderator, view_channel=True, connect=True)
        print("roles and cat permissions set")
        await category.create_text_channel(name="announcements")
        office_channel = await category.create_text_channel(name="office")
        await category.create_text_channel(name="replays")
        await category.create_text_channel(name="team-chat")
        await category.create_voice_channel(name="Scrim")
        meetings_voice = await category.create_voice_channel(name="Team Meetings")
        await office_channel.set_permissions(team_role, view_channel=False)
        await office_channel.set_permissions(tryout_role, view_channel=False)
        await office_channel.set_permissions(ringer_role, view_channel=False)

        await ctx.send("Team has been created")
