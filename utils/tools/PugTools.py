from uuid import uuid4
import nextcord
from typing import Type, List, Tuple
import random
from rich import print
from dataclasses import dataclass, astuple, asdict, field
import discord
from typing import Type, List, Tuple
import inspect
from rich import print


class PugSession:
    def __init__(self,
                 manager: Type[nextcord.Member],
                 lobby_voice: Type[nextcord.VoiceChannel],
                 team1_voice: Type[nextcord.VoiceChannel],
                 team2_voice: Type[nextcord.VoiceChannel]):
        self._lobby_manager: Type[discord.Member] = manager
        self._session_id = uuid4().hex[:4].upper()
        self._players: List[Player] = []
        self._suspended: List[Player] = []
        self._pending: List[Player] = []
        self.lobby_voice: Type[nextcord.VoiceChannel] = lobby_voice
        self.team1_voice: Type[nextcord.VoiceChannel] = team1_voice
        self.team2_voice: Type[nextcord.VoiceChannel] = team2_voice
        # noinspection PyTypeChecker
        self.team1: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None, supportB=None)
        # noinspection PyTypeChecker
        self.team2: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None, supportB=None)

    @property
    def session_id(self):
        return self._session_id

    @property
    def pending(self):
        return self._pending

    @property
    def players(self):
        return self._players

    @property
    def suspended(self):
        return self._suspended

    @property
    def lobby_manager(self):
        return self._lobby_manager

    @lobby_manager.setter
    def lobby_manager(self, value: Type[nextcord.Member]):
        self._lobby_manager = value

    def add_player(self, user: Type[nextcord.Member], roles, games=0):
        for player_num, player in enumerate(self._suspended):  # check if player has suspended themselves
            if player.user == user:  # do this if they have
                self._players.append(player)  # if they are, re-add them
                self._suspended.pop(player_num)
                return True
        __plr__ = Player(user, games, roles=roles)
        self._players.append(__plr__)
        return __plr__

    def del_player(self, user: Type[nextcord.Member]):
        for player_num, player in enumerate(self._players):
            if player.user == user:
                self._players.pop(player_num)
                return True
        return False

    def suspend_player(self, user: Type[nextcord.Member]):
        for player_num, player in enumerate(self._players):
            if player.user == user:
                self._suspended.append(player)
                self._players.pop(player_num)
                return True
        return False

    def inc_games_played(self):
        plr: Type[Player]
        for pos, plr in self.team1.items():
            if plr:
                plr.inc_games()

        for pos, plr in self.team2.items():
            if plr:
                plr.inc_games()

        # noinspection PyTypeChecker
        self.team1: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None,
                                        supportB=None)
        # noinspection PyTypeChecker
        self.team2: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None,
                                        supportB=None)

    @staticmethod
    def map_pick() -> bool:
        r = random.randint(0, 500)
        return r % 2 == 0

    def __repr__(self):
        return f"PugSession({self._lobby_manager}, {self.lobby_voice.name}, {self.team1_voice.name}, {self.team2_voice.name})"

    def random_sample_players(self, amount):
        self._players = []

        roles_available = ("tank", "dps", "support", "flex")
        for _ in range(amount):
            roles_selected = []
            for i in range(random.randint(1, 3)):
                roles_selected.append(roles_available[random.randint(0, 2)])
            if "flex" in roles_selected:
                roles_selected = ("tank", "dps", "support")

            n_selected_roles = []
            for role in roles_selected:
                if role not in n_selected_roles:
                    n_selected_roles.append(role)
            random.shuffle(n_selected_roles)
            # if _ % 2 == 0:
            #     if "tank" in n_selected_roles:
            #         n_selected_roles.remove("tank")

            self._players.append(
                Player(user=f"Player #{_}", games=random.randint(0, 4), roles=tuple(n_selected_roles))
            )

    def generate(self):
        """
        1. Pick a role the available roles.
        2. Go through each player in least played order, and score them for placement quality.
        3. for that position, pick the player wit the highest placement quality.

        Defining Placement Quality:
        1. Number of games played.
        2. First preferred Role
        3. Second preferred role.
        4. Third Preferered role
        """
        # noinspection PyTypeChecker
        self.team1: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None, supportB=None)
        # noinspection PyTypeChecker
        self.team2: Type[Player] = dict(tankA=None, tankB=None, dpsA=None, dpsB=None, supportA=None, supportB=None)

        sorted_player_list = sorted(self._players, key=lambda p: p.games)
        for position in self.team1.keys():  # for each position
            scored = [
            ]
            for p in sorted_player_list:  # go through each player sorted by number of games played.
                scored.append((p, self.evaluate_priority(position[:-1], p)))
            sorted_by_score = list(reversed(sorted(scored, key=lambda x: x[1])))
            try:
                self.team1[position] = sorted_by_score[0][0]
            except:
                break

            sorted_player_list = [player[0] for player in sorted_by_score if
                                  player[0].user.name != sorted_by_score[0][0].user.name]

        for position in self.team2.keys():  # for each position
            scored = [
            ]
            for p in sorted_player_list:  # go through each player sorted by number of games played.
                scored.append((p, self.evaluate_priority(position[:-1], p)))
            sorted_by_score = list(reversed(sorted(scored, key=lambda x: x[1])))
            try:
                self.team2[position] = sorted_by_score[0][0]
            except:
                break
            sorted_player_list = [player[0] for player in sorted_by_score if
                                  player[0].user.name != sorted_by_score[0][0].user.name]

        # once both teams are full, sorted playerlist may have a few players left that did not get selected.

        # shuffle to make team gen random; just flip sides for a few players.
        """
        1. generate a random number between 1 and 6
        2. find [num] position on both teams
        3. switch them
        """

        for _ in range(2):
            index = random.randint(1, 6)
            if index == 1:
                temp = self.team1['tankA']
                self.team1['tankA'] = self.team2['tankA']
                self.team2['tankA'] = temp
            elif index == 2:
                temp = self.team1['tankB']
                self.team1['tankB'] = self.team2['tankB']
                self.team2['tankB'] = temp
            elif index == 3:
                temp = self.team1['dpsA']
                self.team1['dpsA'] = self.team2['dpsA']
                self.team2['dpsA'] = temp
            elif index == 4:
                temp = self.team1['dpsB']
                self.team1['dpsB'] = self.team2['dpsB']
                self.team2['dpsB'] = temp
            elif index == 5:
                temp = self.team1['supportA']
                self.team1['supportA'] = self.team2['supportA']
                self.team2['supportA'] = temp
            elif index == 6:
                temp = self.team1['supportB']
                self.team1['supportB'] = self.team2['supportB']
                self.team2['supportB'] = temp

        self._pending = sorted_player_list

    @staticmethod
    def evaluate_priority(role, player):
        temp_score = 0
        try:
            preference_value = player.roles.index(role)  # find the preference of that role
        except:
            preference_value = 3
        values = [35, 25, 15, 0]
        temp_score += values[preference_value]

        values = list(reversed(list(range(1, 6, 1))))
        #
        try:
            temp_score += values[player.games]
        except:
            raise RecursionError("Please recreate the pug lobby.")

        return temp_score

    def parse_to_string(self, team_number, tank, dps, support):
        _output = str()
        if team_number == 1:
            for position, player in self.team1.items():
                position = position[:-1]
                if position == "tank":
                    if player:
                        _output += f"{tank} {player.user.mention}\n"
                    else:
                        _output += f"{tank}\n"
                elif position == "dps":
                    if player:
                        _output += f"{dps} {player.user.mention}\n"
                    else:
                        _output += f"{dps}\n"
                elif position == "support":
                    if player:
                        _output += f"{support} {player.user.mention}\n"
                    else:
                        _output += f"{support}\n"
        elif team_number == 2:
            for position, player in self.team2.items():
                position = position[:-1]
                if position == "tank":
                    if player:
                        _output += f"{tank} {player.user.mention}\n"
                    else:
                        _output += f"{tank}\n"
                elif position == "dps":
                    if player:
                        _output += f"{dps} {player.user.mention}\n"
                    else:
                        _output += f"{dps}\n"
                elif position == "support":
                    if player:
                        _output += f"{support} {player.user.mention}\n"
                    else:
                        _output += f"{support}\n"
        elif team_number == 3:
            if self._pending:
                for p in self._pending:
                    _output += f"{p.user.mention}\n"
            else:
                _output += "____"
        # _output = _output.replace("None", "")
        return _output


@dataclass(order=True)
class Player:
    user: Type[nextcord.Member]
    games: int
    roles: tuple

    def inc_games(self):
        self.games += 1

    def update_roles(self, roles):
        self.roles = roles

    def __iter__(self):
        for elem in self.roles:
            yield elem

    def __repr__(self):
        if isinstance(self.user, discord.Member):
            return "Player(user=%s, games=%s, roles=%s)" % (
                self.user.name + "#" + self.user.discriminator, self.games, self.roles)
        else:
            return "Player(user=%s, games=%s, roles=%s)" % (
                self.user, self.games, self.roles)

    def __eq__(self, other):
        return self.user == other.user


if __name__ == "__main__":
    import random
    from rich import print
    from rich.console import Console
    from rich.progress import track

    class temp_user:
        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return self.name
    console = Console()
    session = PugSession(None, None, None, None)
    roles = ("tank", "dps", "support")
    for i in range(12):
        player = temp_user(name=f"Player {i}")

        num_selected_roles = random.randint(1, 3)
        selected_roles = [random.choice(roles) for _ in range(num_selected_roles)]
        session.add_player(user=player, roles=tuple(selected_roles))



