from utils.tools import Athena


def main():
    server = Athena()
    server.configs.token = "ODQyODc2ODEyMTIwMTYyMzc0.YJ7sMw.CRY5zHxqfWNGPneWLQw1alQQ1Qw"
    server.initialize(mode=Athena.DISTRIBUTION)



if __name__ == '__main__':
    main()
