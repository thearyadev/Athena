import asyncio
import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
import uuid
import datetime
import os
from ..tools.Athena import Athena


class RoleSelectUI(nextcord.ui.View):
    def __init__(self, console):
        super().__init__(timeout=None)
        self.console = console

    @nextcord.ui.button(label="PUGs", style=nextcord.ButtonStyle.green, custom_id='persistent_view:rs_pugs')
    async def pugs(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.user.add_roles(nextcord.utils.get(interaction.guild.roles, id=951251211628204142))
        self.console.info_log(f"Gave PUGs role to {interaction.user.name}")


class role_select(commands.Cog, embeds):
    LOAD = True
    NAME = "Role Select"

    def __init__(self, client: Athena):
        self.client = client

    @commands.command("showrs")
    @commands.has_permissions(administrator=True)
    async def show_role_select_prompt(self, ctx):
        embed = nextcord.Embed(title="Select your roles!",
                               description="Click the buttons below to select your roles.",
                               colour=embeds.SUCCESS
                               )
        await ctx.send(embed=embed, view=RoleSelectUI(self.client.console))
