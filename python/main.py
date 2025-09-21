from uwapi import UwapiLibrary
from bot import Bot

if __name__ == "__main__":
    with UwapiLibrary():
        Bot().run()
