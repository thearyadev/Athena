import os
import csv
from pathlib import Path


class ScrimLogs:
    def __init__(self, root_path, valid_maps):
        self.root_path = root_path
        self.csv_paths = [root_path + log_sheet_path for log_sheet_path in
                          os.listdir(root_path)]
        self.log: list[TeamScrim] = []
        self.valid_maps = valid_maps
        self.load_sheets()


    def load_sheets(self):
        for log_sheet_path in self.csv_paths:
            self.log.append(TeamScrim(log_sheet_path, self.valid_maps))

    def add_team(self, name):
        # with open(f"../static/logs/scrims/{name}.csv", "w") as file:
        #     return True
        name = "".join(x for x in name if x.isalnum() or x == " ")
        f = Path(f"{self.root_path}{name}.csv")
        f.touch(exist_ok=True)
        if f"{self.root_path}{name}.csv" not in self.csv_paths:
            self.csv_paths.append(f"{self.root_path}{name}.csv")
        self.log = []
        self.load_sheets()


    def log_scrim(self, team_name, date, contact, replays: dict):
        for team in self.log:
            if team_name == team.team_name:
                team.add_scrim(date, contact, replays)
                team.reload()
                break


class TeamScrim:
    def __init__(self, path, maps: list):
        self.maps = maps
        self.path = path
        self.team_name = os.path.basename(path).split(".")[0]
        self.scrims = []
        with open(self.path, newline="") as log_file:
            reader = csv.reader(log_file, delimiter=",")
            for row in list(reader):
                self.scrims.append(
                    Scrim(row[0], row[1],
                          {
                              m: row[row.index(m) + 1] for i, m in enumerate(row[2:]) if m in self.maps
                          })

                )

    def reload(self):
        self.scrims = []
        with open(self.path, newline="") as log_file:
            reader = csv.reader(log_file, delimiter=",")
            for row in list(reader):
                self.scrims.append(
                    Scrim(row[0], row[1],
                          {
                              m: row[row.index(m) + 1] for i, m in enumerate(row[2:]) if m in self.maps
                          })

                )

    def add_scrim(self, date, contact, replays):
        with open(self.path, "a", newline="") as logfile:
            writer = csv.writer(logfile, delimiter=",")
            new_row = [date, contact]

            for m, code in replays.items():
                new_row.append(m)
                new_row.append(code)
            writer.writerow(new_row)


class Scrim:
    def __init__(self, date, contact, replays: dict):
        self.replays = replays
        self.date = date
        self.contact = contact


if __name__ == "__main__":
    log = ScrimLogs("../static/logs/scrims/")
    for team in log.log:
        print(team.team_name)

