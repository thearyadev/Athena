import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
from ..tools.PugTools import PugSession, Player
import asyncio
from ..tools.Athena import Athena


class TeamPromptView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=2000)
        self.session = None
        self.prompt = None
        self.client = None
        self.Tank = None
        self.DPS = None
        self.Support = None

    @nextcord.ui.button(label="Start Round", style=nextcord.ButtonStyle.green)
    async def start_round(self, button: nextcord.ui.button, interaction: nextcord.Interaction):

        if interaction.user == self.session.lobby_manager:
            self.regenerate_teams.disabled = True
            button.disabled = True

            embed = self.prompt.embeds[0]
            embed.color = embeds.SUCCESS
            await interaction.response.edit_message(view=self, embed=embed)
            await interaction.channel.send("Starting round...")

            self.stop()
            m = self.session.map_pick
            if m:
                await self.prompt.reply(f"{self.session.team1_voice.mention} picks map.")
            else:
                await self.prompt.reply(f"{self.session.team2_voice.mention} picks map.")

            for _, member in self.session.team1.items():
                try:
                    self.client.console.info_log(f"Moved {member.user} to team 1 voice channel.")
                    await member.user.move_to(self.session.team1_voice)
                    await asyncio.sleep(1)
                except:
                    pass

            for _, member in self.session.team2.items():
                try:
                    self.client.console.info_log(f"Moved {member.user} to team 2 voice channel.")
                    await member.user.move_to(self.session.team2_voice)
                    await asyncio.sleep(1)
                except:
                    pass
            self.client.console.info_log(f"Incrementing Games Played.")
            self.session.inc_games_played()

    @nextcord.ui.button(label="Regenerate Teams", style=nextcord.ButtonStyle.secondary)
    async def regenerate_teams(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.session.lobby_manager:
            self.session.generate()
            embed = nextcord.Embed(color=embeds.DISCORD_BLUE)
            embed.add_field(name="[ --- TEAM 1 --- ]",
                            value=self.session.parse_to_string(1, self.Tank, self.DPS, self.Support))
            embed.add_field(name="[ --- TEAM 2 --- ]",
                            value=self.session.parse_to_string(2, self.Tank, self.DPS, self.Support))
            embed.add_field(name="[ --- PENDING --- ]",
                            value=self.session.parse_to_string(3, self.Tank, self.DPS, self.Support))
            await self.prompt.edit(embed=embed, view=self)


class PugSessionManagerTools(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.session = None
        self.client = None

    @nextcord.ui.button(label="Mute All", style=nextcord.ButtonStyle.blurple)
    async def mute(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if self.session and interaction.user == self.session.lobby_manager:
            for user in self.session.lobby_voice.members:
                await user.edit(mute=True)
                self.client.console.info_log(f"{user.name} has been server muted.")

    @nextcord.ui.button(label="Unmute All", style=nextcord.ButtonStyle.blurple)
    async def unmute(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if self.session and interaction.user == self.session.lobby_manager:
            for user in self.session.lobby_voice.members:
                await user.edit(mute=False)
                self.client.console.info_log(f"{user.name} has been server unmuted.")
                if user == self.client.user:
                    await user.edit(mute=True)

    @nextcord.ui.button(label="End Round", style=nextcord.ButtonStyle.blurple)
    async def return_to_lobby(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if self.session and interaction.user == self.session.lobby_manager:
            await interaction.response.send_message("Moving all users. ")
            for user in self.session.team1_voice.members:
                await user.move_to(self.session.lobby_voice)
                await asyncio.sleep(1)
            for user in self.session.team2_voice.members:
                await user.move_to(self.session.lobby_voice)
                await asyncio.sleep(1)


class role_select_view(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.roles = []
        self.src_message: nextcord.Message = None
        self.sender: nextcord.Member = None

    @nextcord.ui.button(label="Tank", style=nextcord.ButtonStyle.blurple)
    async def tank(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.sender:
            if "flex" in self.roles: self.roles.remove("flex")

            if "tank" in self.roles:
                self.roles.remove("tank")
            else:
                self.roles.append("tank")
            await self.update_prompt()
        else:
            await self.throw_error(interaction)

    @nextcord.ui.button(label="DPS", style=nextcord.ButtonStyle.blurple)
    async def dps(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.sender:
            if "flex" in self.roles: self.roles.remove("flex")
            if "dps" in self.roles:
                self.roles.remove("dps")
            else:
                self.roles.append("dps")
            await self.update_prompt()
        else:
            await self.throw_error(interaction)

    @nextcord.ui.button(label="Support", style=nextcord.ButtonStyle.blurple)
    async def support(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.sender:
            if "flex" in self.roles: self.roles.remove("flex")
            if "support" in self.roles:
                self.roles.remove("support")
            else:
                self.roles.append("support")
            await self.update_prompt()
        else:
            await self.throw_error(interaction)

    @nextcord.ui.button(label="Flex", style=nextcord.ButtonStyle.blurple)
    async def flex(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.sender:
            if "flex" in self.roles:
                self.roles.remove("flex")
            else:
                self.roles = []
                self.roles.append("flex")

            await self.update_prompt()
        else:
            await self.throw_error(interaction)

    @nextcord.ui.button(label="Confirm Selections", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if interaction.user == self.sender:
            if self.roles:
                embed = self.src_message.embeds[0]
                embed.color = embeds.SUCCESS
                await self.src_message.edit(embed=embed)
                await interaction.response.send_message(f"Your role selection has been submitted.", ephemeral=True)
                self.stop()
            else:
                await interaction.response.send_message(f"You did not select a role.", ephemeral=True)
        else:
            await self.throw_error(interaction)

    async def update_prompt(self):
        embed: nextcord.Embed = self.src_message.embeds[0]
        if self.roles:
            embed.set_field_at(0, name="Roles Selected", value="\n".join(r.upper() for r in self.roles))
        else:
            embed.set_field_at(0, name="Roles Selected", value="____")
        await self.src_message.edit(embed=embed)

    @staticmethod
    async def throw_error(interaction):
        await interaction.response.send_message("This prompt is not yours.", ephemeral=True)


class pugs(commands.Cog, embeds):
    """
    Manages PUGs. This section is undocumented as it is mostly user prompt stuff.
    See /tools/PugTools for more details on PugSession & Player classes.
    """
    LOAD = True
    NAME = "PUGs"

    def __init__(self, client: Athena):
        self.client = client
        self.session: PugSession = None

    @commands.has_permissions(manage_channels=True)
    @commands.command("pugsession_create", aliases=['psc'])
    async def create_pug_session(self, ctx,
                                 lobby_voice: nextcord.VoiceChannel,
                                 team1_voice: nextcord.VoiceChannel,
                                 team2_voice: nextcord.VoiceChannel
                                 ):

        tank = nextcord.utils.get(ctx.guild.emojis, name="Tank")
        support = nextcord.utils.get(ctx.guild.emojis, name="Support")
        dps = nextcord.utils.get(ctx.guild.emojis, name="DPS")
        if not tank:
            await ctx.guild.create_custom_emoji(name="Tank", image=open("./graphics/tank.gif", "rb").read(), reason="!ATHENA COMMAND UTILITY")

        if not tank:
            await ctx.guild.create_custom_emoji(name="Support", image=open("./graphics/support.gif", "rb").read(),
                                          reason="!ATHENA COMMAND UTILITY")

        if not tank:
            await ctx.guild.create_custom_emoji(name="DPS", image=open("./graphics/dps.gif", "rb").read(), reason="!ATHENA COMMAND UTILITY")

        if self.session:
            raise Exception("Unable to make new pug session. Please end previous pug session")

        self.session = PugSession(manager=ctx.author,
                                  lobby_voice=lobby_voice,
                                  team1_voice=team1_voice,
                                  team2_voice=team2_voice)

        embed = nextcord.Embed(
            title="Pug Session: Create",
            description=f"Pug Session has successfully been created. Please see below to "
                        f"ensure the channels are correct. Players may now join the player "
                        f"pool.",
            color=self.SUCCESS
        )

        embed.add_field(name="Lobby Voice", value=self.session.lobby_voice.mention, inline=True)
        embed.add_field(name="Team 1 Voice", value=self.session.team1_voice.mention, inline=True)
        embed.add_field(name="Team 2 Voice", value=self.session.team2_voice.mention, inline=True)
        embed.add_field(name="Session ID", value=self.session.session_id, inline=False)
        embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")

        await ctx.send(embed=embed)
        self.client.console.info_log(f"Pug session created. ID={self.session.session_id}")
        try:
            await self.session.lobby_voice.connect(reconnect=True)
        except:
            pass

        self.client.console.info_log(f"Joined Pug Lobby Voice Channel")

    @commands.has_permissions(manage_channels=True)
    @commands.command("pugsession_delete", aliases=['psd'])
    async def delete_pug_session(self, ctx):
        if not self.session:
            raise Exception("There is no active pug session.")

        self.session = None
        embed = nextcord.Embed(title="Pug Session: Delete", description="Pug session has been deleted.",
                               color=self.SUCCESS)
        embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
        await ctx.send(embed=embed)

        self.client.console.info_log(f"Pug Session Deleted")

    @commands.command("play", aliases=["p"])
    async def register_player(self, ctx):
        if ctx.channel.name == "lobby":
            dm = await ctx.author.create_dm()
            await dm.send("Please do not use commands in the PUGs lobby text channel.")
            await ctx.message.delete()
            return 0

        if self.session:
            embed = nextcord.Embed(
                title="PUGs Player Registration",
                description="Please select the roles you would like to play. "
                            "if you would like to remove a selected role, please click the button again."
                            "\nRemember that the roles you select are not guaranteed",
                color=self.DISCORD_BLUE
            )
            embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")

            role_view = role_select_view()

            embed.add_field(name="Roles Selected", value="____")
            role_view.src_message = await ctx.send(embed=embed)
            role_view.sender = ctx.author
            await role_view.src_message.edit(view=role_view)
            await role_view.wait()
            await role_view.src_message.edit(view=None)
            added_player = self.session.add_player(user=ctx.author, roles=tuple(role_view.roles))
            print(added_player)
            self.client.console.info_log(
                f"Player added to Pug Session player pool: Player={added_player.user}, Roles={added_player.roles}")
        else:
            raise Exception("There is no active pug session.")

    @commands.command("generateteams", aliases=['gts'])
    async def generate_teams(self, ctx):
        if self.session:
            if self.session.lobby_manager == ctx.author:
                self.client.console.info_log(f"Generating teams")
                Tank = nextcord.utils.get(ctx.guild.emojis, name='Tank')
                DPS = nextcord.utils.get(ctx.guild.emojis, name='DPS')
                Support = nextcord.utils.get(ctx.guild.emojis, name='Support')
                self.session.generate()
                embed = nextcord.Embed(color=self.DISCORD_BLUE)
                embed.add_field(name="[ --- TEAM 1 --- ]", value=self.session.parse_to_string(1, Tank, DPS, Support))
                embed.add_field(name="[ --- TEAM 2 --- ]", value=self.session.parse_to_string(2, Tank, DPS, Support))
                embed.add_field(name="[ --- PENDING --- ]", value=self.session.parse_to_string(3, Tank, DPS, Support))
                view = TeamPromptView()
                view.session = self.session
                view.client = self.client
                view.Tank = Tank
                view.DPS = DPS
                view.Support = Support
                view.prompt = await ctx.send(embed=embed, view=view)
            else:
                raise PermissionError("Only the lobby manager may run this command.")
        else:
            raise Exception("There is no active pug session")

    @commands.command("showtools", aliases=['st'])
    async def show_lobby_manager_tools(self, ctx):
        if self.session:
            if ctx.author == self.session.lobby_manager:
                tools = PugSessionManagerTools()
                tools.session = self.session
                tools.client = self.client
                await ctx.send("PUG Session Tools: ", view=tools)
            else:
                raise PermissionError("Only the lobby manager can run this command.")
        else:
            raise Exception("There is no active pug session.")

    @commands.command("switchmanager", aliases=["sm"])
    async def switch_manager(self, ctx, new: nextcord.Member = None):
        if self.session:
            if self.session.lobby_manager == ctx.author:
                if isinstance(new, nextcord.Member):
                    self.session.lobby_manager = new

                    embed = nextcord.Embed(
                        title="Switch Lobby Manager",
                        description=f"Manager has been set to {new.mention}",
                        color=self.SUCCESS
                    )
                    await ctx.send(embed=embed)
                    self.client.console.info_log(
                        f"Session: {self.session.session_id} manager changed to {self.session.lobby_manager}")
                else:
                    raise Exception("Invalid entry. ")
            else:
                raise PermissionError("Only lobby manager may run this command.")
        else:
            raise Exception("There is no active pug session.")
