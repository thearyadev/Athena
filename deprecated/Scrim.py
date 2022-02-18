from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import nextcord
from ..tools.Embeds import embeds
import traceback
import os
import requests
import uuid
import shutil
import urllib
import mimetypes
import random
import datetime
from ..tools.ScrimTools import ScrimLogs
from ..tools.Athena import Athena


class Dropdown(nextcord.ui.Select):
    """
    Creates UI for folder selection
    """

    def __init__(self, logs):
        options = [
            nextcord.SelectOption(label=log, description=None) for log in logs
        ]
        self.selection = None

        super().__init__(placeholder='Select a log to add to', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        # await interaction.response.send_message(f'Media has been added to `{self.values[0]}`')
        self.selection = self.values[0]
        self.view.stop()  # stops accepting responses


class DropdownView(nextcord.ui.View):
    def __init__(self, logs):
        super().__init__()
        self.dropdown = Dropdown(logs)
        self.add_item(self.dropdown)


class DateSelection(nextcord.ui.Select):
    def __init__(self):
        now = datetime.datetime.now()
        options = [
            nextcord.SelectOption(label=now.strftime("%A, %b %d, %Y"), description=None),
            nextcord.SelectOption(label=(now - datetime.timedelta(days=1)).strftime("%A, %b %d, %Y"), description=None),
            nextcord.SelectOption(label=(now - datetime.timedelta(days=2)).strftime("%A, %b %d, %Y"), description=None)
        ]
        self.selection = None

        super().__init__(placeholder='Select a date.', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        # await interaction.response.send_message(f'Media has been added to `{self.values[0]}`')
        self.selection = self.values[0]
        self.view.stop()  # stops accepting responses


class DateSelectionView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.dropdown = DateSelection()
        self.add_item(self.dropdown)


class MapSelection(nextcord.ui.Select):
    def __init__(self, client):
        options = [
            nextcord.SelectOption(label=m.capitalize(), description=None) for m in client.configs.valid_maps

        ]
        self.client = client
        self.replays = {

        }
        super().__init__(placeholder='Select a map', min_values=1, max_values=1, options=options)
        self.map_prompt = None

    async def callback(self, interaction: nextcord.Interaction):
        # await interaction.response.send_message(f'Media has been added to `{self.values[0]}`')

        selection = self.values[0]
        message = await interaction.response.send_message(
            f"Entry Accepted: **{selection}**. Please provide a replay code.")
        self.disabled = True
        self.placeholder = f"Please provide a replay code for: {selection}"
        self.view.done.disabled = True
        await self.map_prompt.edit(view=self.view)

        m = await self.client.wait_for("message", timeout=180.0,
                                       check=lambda m: m.author == interaction.user)

        self.replays[selection.lower()] = m.content
        self.disabled = False
        self.placeholder = "Select a map"
        self.view.done.disabled = False

        await self.map_prompt.edit(view=self.view)

        await interaction.channel.send(
            f"Entry Accepted: **{selection}: {m.content}**. Please press `Done` or select another map.")


class MapSelectionView(nextcord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.dropdown = MapSelection(client)
        self.add_item(self.dropdown)

    @nextcord.ui.button(label="Done", style=nextcord.ButtonStyle.green, )
    async def done(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        # await interaction.response.send_message(f"You are still deciding: **{interaction.message.embeds[0].title.replace('RSVP: ', '')}**", ephemeral=True)
        self.stop()


class ConfirmLog(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.validated = False

    @nextcord.ui.button(label="All good", style=nextcord.ButtonStyle.green, )
    async def done(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.validated = True
        self.stop()

    @nextcord.ui.button(label="Start again", style=nextcord.ButtonStyle.red, )
    async def wrong(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.stop()


class scrim(commands.Cog, embeds):
    """
    User prompts for adding scrims to the scrim log, and getting the full scrim log.
    """

    LOAD = False
    NAME = "Scrim"

    def __init__(self, client: Athena):
        self.client = client
        self.scrim_log = ScrimLogs("./data/scrims/", valid_maps=self.client.configs.valid_maps)
        self.client.console.info_log(
            f"Scrim logs loaded: [{', '.join([team.team_name for team in self.scrim_log.log])}]")

    @commands.command(name="log_scrim", aliases=["ls"])
    async def log_scrim(self, ctx):
        team_sheets = [team.team_name for team in self.scrim_log.log]
        if not team_sheets:
            return

        view = DropdownView(team_sheets)
        await ctx.send("Please select a log to access.", view=view)
        await view.wait()
        if view.dropdown.selection:
            team_name = view.dropdown.selection
            dt_view = DateSelectionView()
            await ctx.send("Please select a date: ", view=dt_view)
            await dt_view.wait()
            date = dt_view.dropdown.selection

            await ctx.send("Please provide a scrim contact.")
            message = await self.client.wait_for("message", timeout=180.0,
                                                 check=lambda m: m.author == ctx.message.author)
            contact = message.content
            mapview = MapSelectionView(self.client)

            mapview.dropdown.map_prompt = await ctx.send("Please enter the maps played.", view=mapview)
            await mapview.wait()

            embed = nextcord.Embed(
                title="Log Scrim",
                description=f"Please confirm if the information bellow is correct.\n\nAdd to: {team_name}\nDate: {date}\nContact: {contact}"
            )

            maps_str = ""
            replay_codes_str = ""
            replays = mapview.dropdown.replays
            for MAP, code in replays.items():
                maps_str += MAP.capitalize() + "\n"
                replay_codes_str += code + "\n"

            maps_str = "```\n" + maps_str + "```"
            replay_codes_str = "```\n" + replay_codes_str + "```"

            embed.add_field(name="Maps", value=maps_str, inline=True)
            embed.add_field(name="Replay Codes", value=replay_codes_str, inline=True)
            embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")

            confirm_view = ConfirmLog()
            await ctx.send(embed=embed, view=confirm_view)

            await confirm_view.wait()
            if confirm_view.validated:
                self.scrim_log.log_scrim(
                    team_name=team_name,
                    date=date,
                    contact=contact,
                    replays=replays
                )
                for channel in ctx.channel.category.channels:
                    if channel.name == "match-history":
                        embed = nextcord.Embed(
                            title=f"Scrim Log: {date}",
                        )
                        embed.add_field(name="Maps", value=maps_str, inline=True)
                        embed.add_field(name="Replay Codes", value=replay_codes_str, inline=True)
                        embed.set_footer(
                            text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
                        await channel.send(embed=embed)
            else:
                await ctx.send("Log has been deleted. Please start again.")
        else:
            pass

    @commands.command("add_team", aliases=['at'])
    async def add_team(self, ctx, *team_name):
        if team_name:
            self.scrim_log.add_team(" ".join(team_name))
            embed = nextcord.Embed(
                title=f"Team: {' '.join(team_name)} has been added.",
                colour=self.SUCCESS
            )
            embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
            await ctx.reply(embed=embed)
        else:
            raise ValueError("Invalid team name.")

    @commands.command("get_sheet", aliases=['gs'])
    async def get_team_sheet(self, ctx):
        team_sheets = [team.team_name for team in self.scrim_log.log]
        if not team_sheets:
            return
        team_view = DropdownView(team_sheets)
        await ctx.reply("Please select the team sheet you would like to access.", view=team_view)
        await team_view.wait()
        for team in self.scrim_log.log:
            if team.team_name == team_view.dropdown.selection:
                await ctx.reply("Please use a spreadsheet viewer to display this data.", file=nextcord.File(team.path))
                return
