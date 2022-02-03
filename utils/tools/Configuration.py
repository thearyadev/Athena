import pickle
import os
from nextcord.ext.commands import CommandError


class configuration:
    def __init__(self):
        self.prefix = "!"
        self.token = "ODQyODc2ODEyMTIwMTYyMzc0.YJ7sMw.KyYZce9QlKPcsq7F3qoItwfLLGk"
        self.guilds = list()
        self.rich_presence = "!Athena"
        self.version = "4.0.0 [DEV]"
        self.upgrade_date = "December 20, 2021"
        self.valid_maps = (
            'busan',
            'ilios',
            'lijiang tower',
            'nepal',
            'oasis',
            'hanamura',
            'horizon lunar colony',
            'paris',
            'temple of anubis',
            'volskaya industries',
            'dorado',
            'havana',
            'junkertown',
            'rialto',
            'route 66',
            'watchpoint: gibraltar',
            'blizzard world',
            'eichenwalde',
            'hollywood',
            'king\'s row',
            'numbani'
        )

    def refresh(self):
        self.serialize("./data/configuration/config.pkl")

    def add_guild(self, guild_id):
        for g in self.guilds:
            if g.id == guild_id:
                raise CommandError(f"Guild {guild} already in database")
        self.guilds.append(guild(guild_id))
        self.refresh()

    def remove_guild(self, guild_id):
        for i, g in enumerate(self.guilds):
            if g.id == guild_id:
                self.guilds.pop(i)
        self.refresh()

    def find_guild(self, guild_id):
        for g in self.guilds:
            if g.id == guild_id:
                return g
        raise CommandError(f"Guild {guild_id} not found.")

    @classmethod
    def deserialize(cls, pickle_path):
        return pickle.load(open(pickle_path, "rb+"))

    def serialize(self, pickle_path):
        pickle.dump(self, open(pickle_path, "wb+"))


class guild:
    def __init__(self, guild_id):
        self.id = guild_id


#
if __name__ == "__main__":
    x = configuration()
    # x.serialize(r"C:\Users\Compu\Documents\Athena-V4\data\configuration\config.pkl")
    l = x.deserialize(r"C:\Users\Compu\Documents\Athena-V4\data\configuration\config.pkl")
    print(l)
