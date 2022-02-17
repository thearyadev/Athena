from utils.tools import Athena


def main():
    server = Athena()
    server.configs.token = "YOUR TOKEN HERE"
    server.initialize(mode=Athena.DISTRIBUTION)


if __name__ == '__main__':
    main()
