from utils.tools import Athena


def main():
    server = Athena()
    server.configs.token = ""
    server.configs.testing_token = "smile"
    server.configs.version = "4.4.0"
    server.initialize(mode=Athena.TESTING)


if __name__ == '__main__':
    main()
