from nextcord.ext import commands
from ..tools.Embeds import embeds
from ..tools.Athena import Athena
import requests
import nextcord
import uuid


class DefinitionPages(nextcord.ui.View):
    def __init__(self, console, word_list, ctx):
        super().__init__(timeout=None)
        self.console = console
        self.word_list = word_list
        self.ctx = ctx
        self.current_page = 0
        self.prompt = None

    async def update_prompt(self):
        try:
            word = self.word_list[self.current_page]
            embed = nextcord.Embed(
                title=f"Define: {word['word']}",
                description=word['definition'],
                color=embeds.SUCCESS
            )
            embed.set_footer(
                text=f"Command issued by {self.ctx.message.author.name}#{self.ctx.message.author.discriminator}")

            embed.add_field(name="Example", value=word['example'] if word['example'] else 'No examples.')
            embed.add_field(name="Page",
                            value=f"{self.current_page}/{len(self.word_list)}")
        except:
            embed = nextcord.Embed(
                title="Error",
                description="Unable to define. Please try to skip to next definition",
                color=embeds.FAIL
            )
            embed.add_field(name="Page",
                            value=f"{self.current_page}/{len(self.word_list)}")
            embed.set_footer(
                text=f"Command issued by {self.ctx.message.author.name}#{self.ctx.message.author.discriminator}")

        if not self.prompt:
            self.prompt = await self.ctx.send(embed=embed, view=self)

        if self.current_page == 0:
            self.previous_page.disabled = True
        else:
            self.previous_page.disabled = False

        if self.current_page == (len(self.word_list) - 1):
            self.next_page.disabled = True
        else:
            self.next_page.disabled = False

        await self.prompt.edit(embed=embed, view=self)

    @nextcord.ui.button(label="Previous Page", style=nextcord.ButtonStyle.red, custom_id=uuid.uuid4().hex)
    async def previous_page(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.current_page -= 1
        await self.update_prompt()

    @nextcord.ui.button(label="Next Page", style=nextcord.ButtonStyle.green, custom_id=uuid.uuid4().hex)
    async def next_page(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        self.current_page += 1
        await self.update_prompt()


class urban_dictionary(commands.Cog, embeds):
    """
    Provides urban dictionary word definitions
    """
    LOAD = True
    NAME = "Urban Dictionary"

    def __init__(self, client: Athena):
        self.client = client
        self.API_ENDPOINT = "https://api.urbandictionary.com/v0/define?term="

    @commands.command(name="define")
    async def define_word(self, ctx, *word):
        try:
            data = requests.get(self.API_ENDPOINT + " ".join(word)).json()['list']
            assert len(data) > 0
        except KeyError:
            # send api broken error
            raise Exception("Urban dictionary API returned an invalid response.")
        except AssertionError:
            # send word not found error
            await ctx.send(f"Word `{' '.join(word)}` not found.")
        else:
            view = DefinitionPages(self.client.console,
                                   word_list=data,
                                   ctx=ctx)
            await view.update_prompt()
