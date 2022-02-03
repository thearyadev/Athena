from utils.tools import Athena
from utils.tools.Configuration import configuration
server = Athena()
server.configs.rich_presence = "MAINTENANCE MODE"
server.initialize(mode="-d")
