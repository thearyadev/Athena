from aiohttp.web_routedef import static
from nextcord.ext import commands, tasks
from nextcord.ext.commands import CommandNotFound
import nextcord
from ..tools.Embeds import embeds
import os
import sys
from uuid import uuid4
import shutil
import asyncio
from . import general
from ..tools import Guild
import shutil
import smtplib, ssl
import json


class backup(commands.Cog, embeds):
    """
    Handles backing up the files to bot owner DMS.
    """
    LOAD = False
    if "credentials.json" in os.listdir("./mail"):
        with open("./mail/credentials.json", "r") as file:
            if len(json.load(file).keys()):
                LOAD = True

    NAME = "Backup"

    def __init__(self, client):
        self.client = client
        self.backup.start()
        self.first = False

    @commands.command(name="dobackup")
    @commands.is_owner()
    async def do_backup(self, ctx):
        archive = await self.create_archives()
        for f in os.listdir(archive):
            try:
                await ctx.send(file=nextcord.File(archive + "/" + f))
                await asyncio.sleep(3)
            except:
                await ctx.send(f"File {f} is too large.")

        shutil.rmtree(archive)

    @tasks.loop(hours=6)
    async def backup(self):
        arya = await self.client.fetch_user(305024830758060034)
        if arya:
            if self.first:
                channel = await arya.create_dm()
                archive = await self.create_archives()
                for f in os.listdir(archive):
                    try:
                        await channel.send(file=nextcord.File(archive + "/" + f))
                        await asyncio.sleep(3)
                    except Exception as e:
                        await self.send_error_email(f, e)

                shutil.rmtree(archive)
            else:
                self.first = True
        else:
            self.client.console.error_log("Backup user `arya` not found.")

    @staticmethod
    async def create_archives():
        archive_name = uuid4().hex
        path = "./temp/" + archive_name
        os.mkdir(path)
        shutil.make_archive(path + "/configuration", "zip", "./data/configuration")
        shutil.make_archive(path + "/guilds", "zip", "./data/guilds")
        shutil.make_archive(path + "/logs", "zip", "./data/logs")
        shutil.make_archive(path + "/media", "zip", "./data/media")
        shutil.make_archive(path + "/scrims", "zip", "./data/scrims")

        return path

    @staticmethod
    async def send_error_email(file1, error):
        port = 465
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.privateemail.com", port, context=context) as server:
            with open("./mail/credentials.json", "r") as file:
                data = json.load(file)
                server.login(data['username'], data['password'])
            message = 'Subject: {}\n\n{}'.format("ATHENA BACKUP FAILED",
                                                 f"ATHENA BACKUP LOOP FAILED.\n{file1}\n{error}")
            server.sendmail("personal@aryankothari.dev", "personal@aryankothari.dev", message)
