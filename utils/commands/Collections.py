from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
import nextcord
from ..tools import embeds
import traceback
import os
import requests
import uuid
import shutil
import urllib
import mimetypes
import random


class Dropdown(nextcord.ui.Select):
    """
    Creates UI for folder selection
    """

    def __init__(self):
        options = [
            nextcord.SelectOption(label=filename, description=None) for filename in os.listdir("./data/media")
        ]
        super().__init__(placeholder='Select a category', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        # await interaction.response.send_message(f'Media has been added to `{self.values[0]}`')
        self.view.stop()  # stops accepting responses


class DropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


class collections(commands.Cog, embeds):
    """
    Handles a folder system for storing images in different categories.
     Users can run a command and it will send a random image in the category they requested
    """

    def __init__(self, client):
        self.client = client
        self.media_path = "./data/media/"  # media path

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith(self.client.configs.prefix):  # if the user used the command prefix
            if message.author != self.client.user:  # and the user is not the bot
                queries = os.listdir(self.media_path)  # get a list of all the categories
                if message.content.replace(self.client.configs.prefix,
                                           "") in queries:  # if their request is a valid folder
                    try:  # try except in case the folder is empty
                        self.client.console.info_log(
                            f"Command Executed: '{message.content.replace('!', '')}' by {message.author} in {message.guild}")
                        await message.channel.send(
                            file=nextcord.File(  # pick a random file from the folder, and send it.
                                self.media_path + message.content.replace(self.client.configs.prefix, "") + "/" +
                                random.sample(os.listdir(
                                    self.media_path + message.content.replace(self.client.configs.prefix, "")), 1)[0]))
                        self.client.console.info_log(
                            f"Media sent from collection {message.content.replace(self.client.configs.prefix, '')}")
                    except ValueError:
                        self.client.console.info_log(
                            f"Collection: {message.content.replace(self.client.configs.prefix, '')} is empty.")

    @commands.command(name="addcollection")
    async def add_section(self, ctx, name):
        """
        Creates a folder

        :param ctx:
        :param name:
        :return:
        """

        try:
            self.client.console.info_log(f"Collection: {name} has been created")
            os.mkdir(f"{self.media_path}{name}")
        except FileExistsError:
            raise FileExistsError("This collection already exists.")
        else:
            embed = nextcord.Embed(
                title=f"Collection '{name}' has been created.",
                colour=self.SUCCESS
            )
            await ctx.send(
                embed=embed
            )

    @commands.command(name="addmedia")
    async def add_media(self, ctx):
        """
        Adds an image to a folder.
        :param ctx:
        :return:
        """

        if ctx.message.attachments:
            formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.get(ctx.message.attachments[0], stream=True)
            if r.headers['content-type'] in formats:
                view = DropdownView()
                prompt = await ctx.send("Please select a folder to add this image to:", view=view)
                await view.wait()  # waits until view is timed out or interacted with

                try:  # will raise IndexError if the view does not have a value
                    path = self.media_path + view.children[0].values[0] + "/"
                    extension = mimetypes.guess_extension(r.headers['content-type'])
                    filename = uuid.uuid4().hex
                    with open(path + filename + extension, "wb") as outfile:
                        shutil.copyfileobj(r.raw, outfile)
                except IndexError:
                    await prompt.delete()  # delete the prompt
                else:
                    embed = nextcord.Embed(
                        title="Add Media",
                        color=self.SUCCESS,
                        description=f"Media has successfully been added to `{view.children[0].values[0]}`"
                    )
                    embed.set_image(url=ctx.message.attachments[0])
                    embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar)
                    await prompt.delete()  # delete the prompt
                    embed.set_footer(
                        text=f"Command issued by {ctx.message.author.name}#{ctx.message.author.discriminator}")

                    await ctx.send(embed=embed)
                    self.client.console.info_log(f"Media has been added to Collection: {view.children[0].values[0]}")
            else:
                raise TypeError("Invalid media type. Please use PNG, JPG, OR JPEG.")
        else:
            raise ValueError("Please attach an image with the command.")
