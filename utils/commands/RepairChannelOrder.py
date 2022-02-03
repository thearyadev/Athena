import nextcord
import asyncio
from nextcord.ext import commands, tasks

from nextcord import CategoryChannel
import datetime
import json
from ..tools.Embeds import embeds


class Confirm(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.confirmed = False
        self.confirmation_user = None

    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.confirmed = True
        self.confirmation_user = interaction.user
        self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red)
    async def Cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.confirmed = False
        self.stop()


class repair_channel_order(commands.Cog, embeds):
    """
    These commands are Starcity eSports Moderation commands. All commands are administrator only.
    """

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.running_context = None
        self.lcid = 774820103917273111
        self.log_channel = None

    @commands.command("sync")
    async def sync_server(self, ctx):
        self.client.console.info_log("Server sync requested.")
        with open("./data/configuration/channels.json", "r+") as channels_file:
            data = {}
            for c in ctx.guild.channels:
                if not isinstance(c, CategoryChannel):
                    data[int(c.category.id)] = [[chnl.id, chnl.position] for chnl in c.category.channels]
            channels_file.truncate(0)
            channels_file.seek(0)
            json.dump(data, channels_file)

        embed = nextcord.Embed(
            title="Sync",
            description="Channel order has been updated to current configuration",
            colour=self.SUCCESS
        )
        embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
        await ctx.send(
            embed=embed)

        self.client.console.info_log(f"Synced config file with server order.")

    @commands.command("repair")
    async def repair_prompts(self, ctx, args="start"):

        if args not in ('start', 'stop'): raise ValueError("Invalid arguments. Please enter start or stop.")

        if args == "start":
            if not self.running_context:

                embed = nextcord.Embed(
                    title="Repair Channel Order",
                    description="This will re-order all the channels in the "
                                "server according to the saved configuration. Please "
                                "press the button to confirm.",
                    colour=self.SUCCESS
                )
                embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
                view = Confirm()
                message = await ctx.send(embed=embed, view=view)
                await view.wait()
                if view.confirmed:
                    embed.title = "Repair Channel Order: Authorized"
                    embed.description = "Event Loop is now running."
                    embed.set_footer(
                        text=f"Confirmation issued by {view.confirmation_user.name}#{view.confirmation_user.discriminator}")
                    await ctx.send(embed=embed)
                    self.running_context = ctx

                    self.log_channel = nextcord.utils.get(ctx.guild.channels, id=self.lcid)
                    self.repair_channel_order.start()
                    self.client.console.info_log("Repair Task Started.")
                else:
                    await message.delete()
            else:
                raise Exception("This task is already running.")

        elif args == "stop":
            if self.running_context:
                self.running_context = None
                self.log_channel = None
                self.repair_channel_order.cancel()
                embed = nextcord.Embed(
                    title="Repair Channel Order: Stop",
                    description="Event loop has been stopped.",
                    color=self.SUCCESS
                )
                embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
                await ctx.send(embed=embed)
            else:
                raise ValueError("Not currently running")

    @tasks.loop(hours=12)
    async def repair_channel_order(self):
        self.client.console.info_log(f"Repairing channel order task begin.")
        with open("./data/configuration/channels.json", "r+") as channels_file:
            # confirm no new channels/categories have been added.
            data = json.load(channels_file)
            allids = []

            for cat, chlist in data.items():
                allids.append(int(cat))
                for ch in chlist:
                    allids.append(ch[0])

            for channel in self.running_context.guild.channels:
                if channel.id not in allids:
                    raise MemoryError(
                        "New channel is detected. Please manually reorganize channels, and run Sync command.")

            for cat, chlist in data.items():
                category = nextcord.utils.get(self.running_context.guild.categories, id=int(cat))

                for chdata in chlist:
                    channel = nextcord.utils.get(self.running_context.guild.channels, id=chdata[0])

                    if channel:
                        srcp = channel.position

                        src = f"```fix\nChannel Name: {channel.name}\nChannel Category: {channel.category}\nChannel ID: {channel.id}\nChannel Position: {channel.position}```"
                        await channel.edit(position=chdata[1], category=category)
                        dst = f"```fix\nChannel Name: {channel.name}\nChannel Category: {channel.category}\nChannel ID: {channel.id}\nChannel Position: {channel.position}```"
                        dstp = channel.position
                        embed = nextcord.Embed(
                            title="Repair Channel Order: Logging",
                            description="Logs for modified channels.",
                            colour=self.DISCORD_BLUE
                        )
                        embed.add_field(name="SOURCE", value=src, inline=False)
                        embed.add_field(name="DESTINATION", value=dst, inline=False)
                        embed.set_footer(text=f"Command issued by ADMINISTRATOR")
                        self.client.console.info_log(f"'{channel.name}' has been updated.")
                        await asyncio.sleep(3)
                        if src != dst:
                            try:
                                await self.log_channel.send(embed=embed)
                            except AttributeError:
                                pass
                            self.client.console.info_log(f"'{channel.name}' moved from {srcp} to {dstp}")
                            with open("./data/logs/move.json", "r+") as logfile:
                                data = json.load(logfile)
                                data['total_moves'] += 1
                                data['log'].append(
                                    {
                                        "time": datetime.datetime.now().strftime("%m/%d/%Y - %H:%M:%S"),
                                        "channel": {
                                            "name": channel.name,
                                            "category": channel.category.name
                                        },
                                        "from": srcp,
                                        "to": dstp
                                    }
                                )

                                logfile.truncate(0)
                                logfile.seek(0)
                                json.dump(data, logfile)
        self.client.console.info_log("Repair Task has completed.")

    @commands.command("repairlog")
    async def repair_log(self, ctx):
        with open("./data/logs/move.json", "r") as logfile:
            data = json.load(logfile)
            moves = data['total_moves']
            started = data['started']

        embed = nextcord.Embed(
            title="Repair Channel Order: Log Dump",
        )

        embed.add_field(name="Total Channels Moved", value=f"{moves} Channels Moved", inline=False)
        embed.add_field(name="Started Logging On: ", value=started, inline=False)
        embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
        self.client.console.info_log(f"Repair log request sent.")
        await ctx.send(embed=embed)
