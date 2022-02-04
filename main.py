from utils.tools import Athena

server = Athena()
server.configs.rich_presence = "MAINTENANCE MODE"
server.configs.token = ""
server.configs.testing_token = ""
server.configs.refresh()
server.initialize(mode="-t")
