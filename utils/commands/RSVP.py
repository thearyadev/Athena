import nextcord
from nextcord.ext import commands
import uuid
from ..tools.Embeds import embeds
import os
import asyncio
from ..tools.Athena import Athena

class Dropdown(nextcord.ui.Select):
    """
    Creates UI for folder selection
    """

    def __init__(self, roles):
        options = [
            nextcord.SelectOption(label=f"{role.name}  ::  {role.id}", description=None) for role in roles
        ]
        super().__init__(placeholder='Select a role', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        self.view.stop()  # stops accepting responses


class DropdownView(nextcord.ui.View):
    def __init__(self, roles):
        super().__init__()
        self.add_item(Dropdown(roles=roles))


class rsvp_options(nextcord.ui.View):
    def __init__(self, console, reloaded=False):
        super().__init__(timeout=None)
        self.joined = list()
        self.declined = list()
        self.deciding = list()
        self.console = console
        self.reloaded = reloaded

    @nextcord.ui.button(label="I will be there.", style=nextcord.ButtonStyle.green, custom_id="persistent_view:join")
    async def join(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        # await interaction.response.send_message(
        #     f"You are now attending: **{interaction.message.embeds[0].title.replace('RSVP: ', '')}**", ephemeral=True)
        await self.add_rsvp(interaction.user, "joined", interaction.message, interaction)

    @nextcord.ui.button(label="I will not be there.", style=nextcord.ButtonStyle.red,
                        custom_id="persistent_view:decline")
    async def decline(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        # await interaction.response.send_message(
        #     f"You have declined: **{interaction.message.embeds[0].title.replace('RSVP: ', '')}**", ephemeral=True)
        await self.add_rsvp(interaction.user, "declined", interaction.message, interaction)

    @nextcord.ui.button(label="Still deciding...", style=nextcord.ButtonStyle.grey,
                        custom_id="persistent_view:deciding")
    async def deciding(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        # await interaction.response.send_message(
        #     f"You are still deciding: **{interaction.message.embeds[0].title.replace('RSVP: ', '')}**", ephemeral=True)
        await self.add_rsvp(interaction.user, "deciding", interaction.message, interaction)

    async def add_rsvp(self, user, action, message, interaction):
        await interaction.response.send_message("Response has been added.", ephemeral=True)

        if self.reloaded:  # if bot restarted,
            # read whats already in the view

            joined_ids = ["".join([n for n in unparsed_id if n.isnumeric()]) for unparsed_id in
                          message.embeds[0].fields[0].value.split("\n")]
            declined_ids = ["".join([n for n in unparsed_id if n.isnumeric()]) for unparsed_id in
                            message.embeds[0].fields[1].value.split("\n")]
            pending_ids = ["".join([n for n in unparsed_id if n.isnumeric()]) for unparsed_id in
                           message.embeds[0].fields[2].value.split("\n")]

            for u_id in joined_ids:
                if u_id:
                    u = nextcord.utils.get(message.guild.members, id=int(u_id))
                    if u:
                        self.joined.append(u)
            for u_id in declined_ids:
                if u_id:
                    u = nextcord.utils.get(message.guild.members, id=int(u_id))
                    if u:
                        self.declined.append(u)
            for u_id in pending_ids:
                if u_id:
                    u = nextcord.utils.get(message.guild.members, id=int(u_id))
                    if u:
                        self.deciding.append(u)
            self.reloaded = False

        self.console.info_log(f"Received RSVP entry from {user.name}")
        for reacted_user in self.joined:
            if reacted_user == user:
                self.joined.remove(reacted_user)

        for reacted_user in self.declined:
            if reacted_user == user:
                self.declined.remove(reacted_user)

        for reacted_user in self.deciding:
            if reacted_user == user:
                self.deciding.remove(reacted_user)

        if action == "joined":
            self.joined.append(user)
        elif action == "declined":
            self.declined.append(user)
        elif action == "deciding":
            self.deciding.append(user)

        old_embed = message.embeds[0]
        message.embeds[0].clear_fields()
        joined, declined, deciding = "", "", ""

        for user in self.joined:
            joined += user.mention + "\n"

        for user in self.declined:
            declined += user.mention + "\n"

        for user in self.deciding:
            deciding += user.mention + "\n"

        if not joined: joined = "____"
        if not declined: declined = "____"
        if not deciding: deciding = "____"

        old_embed.add_field(name=f"Attending ({len(self.joined)})", value=joined)
        old_embed.add_field(name=f"Declined ({len(self.declined)})", value=declined)
        old_embed.add_field(name=f"Pending ({len(self.deciding)})", value=deciding)

        await message.edit(embed=old_embed)
        self.console.info_log(f"RSVP Notification edited.")


class rsvp(commands.Cog, embeds):
    """
    creates rsvp notifications
    """
    LOAD = True
    NAME = "RSVP"

    def __init__(self, client: Athena):
        self.client = client

    @commands.command(name="amr")
    @commands.has_permissions(manage_guild=True)
    async def add_mentionable_role(self, ctx, role: nextcord.Role):

        """
        adds a mentionable role to the list of mentionable roles for each guild.
        :param ctx:
        :param role:
        :return:
        """
        guild = self.client.database.get(ctx.guild.id)

        if len(guild.mentionable) < 25:
            guild.mentionable.append(role.id)
        else:
            raise Exception("Role limit exceeded.")

        self.client.database.update_guild(guild)

        embed = nextcord.Embed(title="Mentionable role added",
                               description="Role has been added to list of mentionable roles.",
                               color=self.SUCCESS)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Manager")
    async def rsvp(self, ctx, channel: nextcord.TextChannel, *title):
        """
        sends notification to specified channel
        :param ctx:
        :param channel:
        :param title:
        :return:
        """
        try:
            roles = list()
            for r_id in self.client.database.get(ctx.guild.id).mentionable:
                r = nextcord.utils.get(ctx.guild.roles, id=r_id)
                if r:
                    roles.append(r)
            if not roles:
                raise AttributeError
            view = DropdownView(roles)
            view_message = await ctx.send("Please select a role to mention", view=view)
        except AttributeError:
            raise Exception("This guild has not configured any mentionable roles. Please run `amr <role>` first.")
        await view.wait()

        try:
            role = nextcord.utils.get(ctx.guild.roles, id=int(view.children[0].values[0].split("  ::  ")[1].strip()))
        except:
            await view_message.delete()
            return

        embed = nextcord.Embed(
            title=f"RSVP: {' '.join(title)}",
            description=f"{role.mention} Click one of the buttons below to join this event.",
            color=self.SUCCESS
        )
        embed.add_field(name="Attending (0)", value="____")
        embed.add_field(name="Declined (0)", value="____")
        embed.add_field(name="Pending (0)", value="____")
        embed.set_footer(
            text=f"RSVP Notification issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
        view = rsvp_options(self.client.console)
        # view.console = self.client.console
        announcement = await channel.send(role.mention, view=view, embed=embed)
        await announcement.edit("")
        self.client.console.info_log(f"RSVP '{' '.join(title)}' created and sent.")
