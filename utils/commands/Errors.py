from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import nextcord
from ..tools.Embeds import embeds
import traceback
import os


class errors(commands.Cog, embeds):
    """
    Error handling & error output for discord.
    """
    LOAD = True
    NAME = "Errors"
    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            if not (ctx.message.content.replace(self.client.configs.prefix, "") in os.listdir("./data/media")):
                self.client.console.error_log(f"Command not found {ctx.message}") # for collections, since they arent valid commands.
            return
        else:
            embed = nextcord.Embed(title="Oh no! An error has occurred. ",
                                   description=f"The following error has occurred:\n```{error}```\nPlease contact your server administrator",
                                   colour=self.ERROR)
            embed.set_author(name=self.client.user.name,
                             icon_url=self.client.user.avatar)

            embed.add_field(name='Command Invoker', value=ctx.author)
            try:
                embed.set_footer(text='Error Report', icon_url=ctx.guild.icon_url)
            except:
                embed.set_footer(text='Error Report')
            # msg = str(error.original).replace('\n', '')
            try:
                tb = traceback.format_tb(error.original.__traceback__)[-1].replace("\n", '').strip()
                self.client.console.error_log(f"Exception Raised (Caught by Discord): {tb}")
            except:
                self.client.console.error_log(f"Unknown error occurred. Likely command args error. (Caught by "
                                              f"Discord): '{error}'") # uncaught errors

            await ctx.send(embed=embed)


