import sys
from uwapi import UwapiLibrary
from bot3 import ObserverBot


def main():
    """Main entry point that can accept server and port arguments"""
    server = None
    port = None

    # Parse command line arguments - require server and port
    if len(sys.argv) == 3:
        server = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid port number: {sys.argv[2]}")
            print("Usage: python main_observer.py <server> <port>")
            return
    else:
        print("Usage: python main_observer.py <server> <port>")
        print("Example: python main_observer.py 127.0.0.1 53448")
        print("")
        print("This observer bot requires a server and port to connect to.")
        print("Start a game server first, then use this bot to observe it.")
        return

    # Create and run the observer bot within UwapiLibrary context
    with UwapiLibrary():
        bot = ObserverBot(server, port)
        success = bot.run()

        if success:
            print("Observer bot finished")
        else:
            print("Observer bot failed to start")


if __name__ == "__main__":
    main()