from uuid import uuid4
import nextcord
from typing import Type, List, Tuple
import random
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


from dataclasses import dataclass, astuple, asdict, field
import discord
from typing import Type, List, Tuple
import inspect
from rich import print


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

    console = Console()
    results = [0, 0, 0, 0]
    role_density = [0, 0, 0]


    def eval_generation_quality(generation):
        for role, player in generation.items():
            role = role[:-1]
            try:  # try and find the role they were placed in, in their preferred roles
                results[player.roles.index(role)] += 1
            except:
                results[3] += 1

            for r in player.roles:
                if r == "tank":
                    role_density[0] += 1

                if r == "dps":
                    role_density[1] += 1

                if r == "support":
                    role_density[2] += 1


    def main():
        session = PugSession(None, None, None, None)
        total = 50000
        pcount = 0
        for i in track(range(total), description="Calculating..."):
            session.random_sample_players(16)
            session.generate()
            eval_generation_quality(session.team1)
            eval_generation_quality(session.team2)
            pcount += 12

        console.rule("RESULTS")
        print(f"First preferred role: {results[0]} | [red]{(results[0] / pcount) * 100}%[/red]")
        print(f"Second preferred role: {results[1]} | [red]{(results[1] / pcount) * 100}%[/red]")
        print(f"Third preferred role: {results[2]} | [red]{(results[2] / pcount) * 100}%[/red]")
        print(f"Did not get preferred role: {results[3]} | [red]{(results[3] / pcount) * 100}%[/red]")
        print(f"Role Density: Tank {role_density[0]} DPS {role_density[1]} Support {role_density[2]}")


    def main2():
        session = PugSession(None, None, None, None)
        # session.random_sample_players(300)
        # session.generate()
        # print(session.pending)
        print(session.parse_to_string(1, 2, 3, 4))


    main2()
