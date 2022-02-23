from nextcord.ext import commands, tasks
from ..tools.Embeds import embeds
import os
from uuid import uuid4
import shutil
import requests
import zipfile
from ..tools.Athena import Athena


class backup(commands.Cog, embeds):
    """
    Backs up configs to a local storage server.
    This module will not work for you without modifications, and an HTTP server
    """
    try:
        requests.get("http://10.0.0.189:1200/upload", timeout=2)  # do check if backup server is available
    except requests.exceptions.ConnectTimeout:
        LOAD = False  # dont load module if it isnt
    else:
        LOAD = True  # load if it is
    NAME = "Backup"

    def __init__(self, client: Athena):
        self.client = client
        if self.client.mode == Athena.DISTRIBUTION:  # only backup if we're in distribution mode.
            # No need to keep backing up empty directories
            self.backup.start()

    @commands.command(name="dobackup")
    @commands.is_owner()
    async def do_backup(self, ctx):
        try:
            await ctx.send("Creating archive.")
            archive = await self.create_archives()
            with open(f"{archive}/athena.zip", "rb") as data:

                if self.client.mode == Athena.DISTRIBUTION:
                    r = requests.post("http://10.0.0.189:1200/upload",
                                      headers={"authorization": "aac9e5e85ec5450b84f697055b2c9c55", "folder": "athena"},
                                      data=data)
                elif self.client.mode == Athena.TESTING:
                    r = requests.post("http://10.0.0.189:1200/upload",
                                      headers={"authorization": "aac9e5e85ec5450b84f697055b2c9c55",
                                               "folder": "athena-testing"},
                                      data=data)
                if r.status_code != 200:
                    raise Exception("Server error")
            await ctx.send("Backup complete.")
            shutil.rmtree(archive)
        except Exception as e:
            await ctx.send(f"Backup error: {e}")

    @tasks.loop(hours=3)
    async def backup(self):
        try:
            self.client.console.info_log("Backing up active files to server...")
            archive = await self.create_archives()
            with open(f"{archive}/athena.zip", "rb") as data:
                r = requests.post("http://10.0.0.189:1200/upload",
                                  headers={"authorization": "aac9e5e85ec5450b84f697055b2c9c55", "folder": "athena"},
                                  data=data)
                if r.status_code != 200:
                    raise Exception("Server error")
            self.client.console.info_log("Backup complete.")
            shutil.rmtree(archive)
        except Exception as e:
            await self.send_error_message(e)

    async def create_archives(self):
        archive_name = uuid4().hex
        path = "./temp/" + archive_name
        os.mkdir(path)
        with zipfile.ZipFile(f"{path}/athena.zip", "w") as zf:
            for f in self.get_paths("./data"):
                zf.write(f)
        return path

    async def send_error_message(self, error):
        try:
            arya = await self.client.fetch_user(305024830758060034)
            channel = await arya.create_dm()
            await channel.send(f"Backup error: {error}")
        except:
            self.client.console.error_log("Unable to create send DM to bot owner.")

    @staticmethod
    def get_paths(directory):
        paths = list()
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                paths.append(filepath)
        return paths
