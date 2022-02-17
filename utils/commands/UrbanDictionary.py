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
        self.word_list = word_list  # list of the words & their data.
        self.ctx = ctx  # current context to send/edit message
        self.current_page = 0
        self.prompt = None  # when this initializes, the message that will hold the embed has not been created.

    async def update_prompt(self):
        try:
            """
            sets up the embed from the data in the current word (self.current_page).
            May raise an error if the data isn't what is expected.
            """

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
                            value=f"{self.current_page + 1}/{len(self.word_list) - 1}")
        except KeyError:
            """
            if there is a keyerror (where the data expected is not there),
            update that page to prompt the user that the page couldnt be loaded 
            """
            embed = nextcord.Embed(
                title="Error",
                description="Unable to define. Please try to skip to next definition",
                color=embeds.FAIL
            )
            embed.add_field(name="Page",
                            value=f"{self.current_page + 1}/{len(self.word_list) - 1}")
            embed.set_footer(
                text=f"Command issued by {self.ctx.message.author.name}#{self.ctx.message.author.discriminator}")

        if not self.prompt:  # if the prompt does not exist yet,
            self.prompt = await self.ctx.send(embed=embed, view=self)  # save it to self.prompt

        # page handler

        if self.current_page == 0:  # current page is zero,
            self.previous_page.disabled = True  # disable the back button
        else:
            self.previous_page.disabled = False  # re-enable if thats not the case

        if self.current_page == (len(self.word_list) - 1):  # last item in list of words
            self.next_page.disabled = True  # disable forward button
        else:
            self.next_page.disabled = False  # re-enable if thats not the case

        await self.prompt.edit(embed=embed,
                               view=self)  # edit that prompt to show the new page, and disable/enable buttons

    @nextcord.ui.button(label="Previous Page", style=nextcord.ButtonStyle.red, custom_id=uuid.uuid4().hex)
    async def previous_page(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        """
        Discord button for moving to the previous word.
        Decrements self.current_page & updates the prompt with the current page data
        :param button:
        :param interaction:
        :return:
        """
        self.current_page -= 1
        await self.update_prompt()

    @nextcord.ui.button(label="Next Page", style=nextcord.ButtonStyle.green, custom_id=uuid.uuid4().hex)
    async def next_page(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        """
        Discord button for moving to the next word.
        Increments self.current_page & updates the prompt with the current page data
        :param button:
        :param interaction:
        :return:
        """
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
            data = requests.get(self.API_ENDPOINT + " ".join(word)).json()[
                'list']  # gets the data from the UD endpoint.
            assert len(data) > 0  # if the word that is looked up isn't in the database, then the list will be empty.
        except KeyError:
            # send api broken error. If a key error is raised from the try block,
            # the data sent from the server is invalid/incompatible with this code
            raise Exception("Urban dictionary API returned an invalid response.")
        except AssertionError:
            # send word not found error
            await ctx.send(f"Word `{' '.join(word)}` not found.")
        else:
            view = DefinitionPages(self.client.console,  # handles pagnation for multiple words &
                                   word_list=data,  # sending/editing messages from discord.
                                   ctx=ctx)
            await view.update_prompt()  # starts the user interface in Discord.
