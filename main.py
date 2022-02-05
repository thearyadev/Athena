from utils.tools import Athena


def main():
    server = Athena()
    server.configs.rich_presence = "MAINTENANCE MODE"
    server.configs.refresh()
    server.initialize(mode="-t")


if __name__ == '__main__':
    main()
