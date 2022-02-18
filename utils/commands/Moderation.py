import asyncio
import nextcord
from nextcord.ext import commands
from ..tools.Embeds import embeds
import uuid
import datetime
import os
from ..tools.Athena import Athena


class moderation(commands.Cog, embeds):
    LOAD = True
    NAME = "Moderation"

    def __init__(self, client: Athena):
        self.client = client

    @commands.command("archive")
    @commands.has_permissions(manage_guild=True)
    async def create_channel_history_archive(self, ctx, amount: int, channel: nextcord.TextChannel = None):
        """
        Creates a text file with all of the messages sent in a channel.
        :param ctx:
        :param amount:
        :param channel:
        :return:
        """

        async with ctx.channel.typing():
            if not channel: channel = ctx.channel
            embed = nextcord.Embed(
                title=f"Generating archive of: {channel.name}..."
            )
            message = await ctx.send(embed=embed)
            await asyncio.sleep(3)

            self.client.console.info_log(f"Archive of {channel.name} requested; amount = {amount}.")
            h = await channel.history(limit=amount).flatten()
            h = list(reversed(h))
            message_count = len([m for m in h if m.content])
            with open(
                    path := f"./temp/Archive_{datetime.datetime.now().strftime('%A-%B-%d-%Y')} {uuid.uuid4().hex[:4]}.txt",
                    "a+") as archive_file:
                archive_file.writelines(
                    f"[META] CREATED: {datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}; MESSAGE COUNT: {message_count}; CHANNEL: {channel.name} [/META]\n"
                )

                for message in h:
                    if message.content:
                        try:
                            archive_file.writelines(
                                f"[{message.created_at.strftime('%m/%d/%Y, %H:%M:%S')}]: {message.author.name}#{message.author.discriminator}: {message.content}\n")
                        except:
                            pass
            self.client.console.info_log(f"Archive of {channel.name} successfully created.")

            await ctx.send(file=nextcord.File(path))
            embed.title = f"Archive of: {channel.name}"
            await message.edit(embed=embed)
            self.client.console.info_log(f"Archive of {channel.name} sent to {ctx.channel.name}")
            os.remove(path)
            self.client.console.info_log(f"Archive of {channel.name} temporary file successfully deleted.")

    @commands.command("athpurge", aliases=['athp'])
    @commands.has_permissions(administrator=True)
    async def purge_channel(self, ctx, amount: int = 0):
        """
        deletes param:amount of messages from a channel
        :param ctx:
        :param amount:
        :return:
        """
        try:
            await ctx.channel.purge(limit=amount)
        except:
            pass
        embed = nextcord.Embed(title=f"Purged [{amount}] messages.", colour=self.SUCCESS)
        embed.set_footer(text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")
        await ctx.send(embed=embed)
