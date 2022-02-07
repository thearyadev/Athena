import pickle
import os
from nextcord.ext.commands import CommandError


class configuration:
    """
    Handles configuration of the bot. All of this data is serialized using Pickle and is loaded in when the bot starts.
    the pkl file contains all the data here in the class
    """
    def __init__(self):
        self.prefix = "!"
        self.token = ""
        self.testing_token = ""
        self.rich_presence = "!Athena"
        self.version = "4.3.0 [DEV]"
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

    @classmethod
    def deserialize(cls, pickle_path):
        return pickle.load(open(pickle_path, "rb+"))

    def serialize(self, pickle_path):
        pickle.dump(self, open(pickle_path, "wb+"))


