from utils.tools import Athena

server = Athena()
server.configs.rich_presence = "MAINTENANCE MODE"
server.configs.refresh()
server.initialize(mode="-t")
