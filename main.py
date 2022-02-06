from utils.tools import Athena


def main():
    server = Athena()
    server.configs.token = "YOUR TOKEN HERE"
    server.configs.version = "4.1.0"
    server.initialize(mode="-d")


if __name__ == '__main__':
    main()
