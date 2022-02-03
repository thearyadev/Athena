from utils.tools import Athena
from utils.tools.Configuration import configuration
server = Athena()
server.configs.token = "YOUR TOKEN HERE"
server.initialize(mode="-d")
