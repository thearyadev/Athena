from utils.tools import Athena

server = Athena()
server.configs.rich_presence = "MAINTENANCE MODE"
server.configs.token = "OTIzMzU3NDU3NTU0NzQzMzI4.YcO1pQ.HHFd6ma5FHJnrqSP38yy6_OMxzg"
server.configs.testing_token = "ODQyODc2ODEyMTIwMTYyMzc0.YJ7sMw.Hag483Jk0QTHp-k8IF5nU8Dhu34"
server.initialize(mode="-t")
