import sqlite3
from dataclasses import dataclass
import json
from rich import print
import time
import sys


@dataclass
class Guild:
    _id: int
    authorized: bool
    mentionable: list
    ratio_emoji: int

    @property
    def id(self):
        return self._id

    def reset(self):
        self.mentionable = list()
        self.ratio_emoji = 0


class GuildDatabase:
    def __init__(self, path, console):
        self.console = console
        self.connection = sqlite3.connect(path)
        self.console.info_log("Database connection successful.")
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guilds'")
        self.guilds: list[Guild] = list()

        if not self.cursor.fetchone():
            self.console.info_log("Unable to find data table. Creating new guild table.")
            self.create_table()

        self.load_guilds()
        # self.console.info_log(f"Memory Usage: GuildDatabase={sys.getsizeof(self)} bytes Guild={sys.getsizeof(self.guilds[0])} bytes")

    def add_guild(self, guild: Guild):
        self.cursor.execute(f"SELECT * FROM guilds WHERE id={guild.id}")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"""
                INSERT INTO guilds VALUES (
                {guild.id},
                {guild.authorized},
                '{json.dumps(guild.mentionable)}',
                {guild.ratio_emoji}
                )
                """
            )
            self.connection.commit()
            self.guilds.append(guild)

    def get(self, guild_id):
        for g in self.guilds:
            if g.id == guild_id:
                return g

    def update_guild(self, guild: Guild):

        self.cursor.execute(f"UPDATE guilds SET authorized = {guild.authorized} WHERE id = {guild.id}")
        self.cursor.execute(f"UPDATE guilds SET mentionable = '{json.dumps(guild.mentionable)}' WHERE id = {guild.id}")
        self.cursor.execute(f"UPDATE guilds SET ratio_emoji = {guild.ratio_emoji} WHERE id = {guild.id}")
        self.connection.commit()

    def load_guilds(self):
        start = time.time()
        self.console.info_log("Loading guilds from database.")
        self.cursor.execute("SELECT * FROM guilds")
        for row in self.cursor.fetchall():
            self.guilds.append(Guild(
                _id=row[0],
                authorized=bool(row[1]),
                mentionable=eval(row[2]),
                ratio_emoji=row[3]
            ))
        end = time.time()

        self.console.info_log(f"Guilds loaded successfully. count={len(self.guilds)}")
        self.console.info_log(f"Load Execution Time: {end - start} seconds")

    def create_table(self):
        self.cursor.execute("""
                            CREATE TABLE guilds (
                            id integer,
                            authorized integer,
                            mentionable text,
                            ratio_emoji integer
                            )""")
        self.connection.commit()
