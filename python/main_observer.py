import sys
import os
import shutil


def restore_reconnect_config_standalone(server, port):
    """Restore reconnection config without uwapi dependencies."""
    try:
        # Generate game ID like the bot does
        if server and port:
            if server == "lobby_id":
                # Use port parameter as lobby_id
                game_id = f"lobby_id_{port}"
            else:
                # Direct IP connection: server_port
                game_id = f"{server}_{port}"
        else:
            return

        reconnects_path = r"C:/Program Files (x86)/Steam/steamapps/common/Unnatural Worlds/reconnects"
        source_file = os.path.join(reconnects_path, f"{game_id}.ini")
        target_file = os.path.join(reconnects_path, "4.ini")

        print(f"🔍 Pre-uwapi restore: {source_file} → {target_file}")

        if os.path.exists(source_file):
            # Read source file content
            with open(source_file, 'rb') as src:
                file_content = src.read()
                print(f"🔍 Read {len(file_content)} bytes from source")

            # Write to target file with explicit flushing
            with open(target_file, 'wb') as dst:
                dst.write(file_content)
                dst.flush()
                os.fsync(dst.fileno())
                print(f"🔍 Wrote {len(file_content)} bytes to target")

            # Force filesystem sync
            try:
                os.sync()
            except:
                pass

            # Sleep 5 seconds to ensure file system operations are fully complete
            import time
            from datetime import datetime

            restore_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
            print(f"✅ Pre-uwapi restore successful for game {game_id}")
            print(f"⏰ Restore completed at: {restore_time}")
        else:
            print(f"📝 No saved reconnection config found for game {game_id}")

    except Exception as e:
        print(f"⚠️ Pre-uwapi restore failed: {e}")

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

    # Restore reconnection config BEFORE importing uwapi (no uwapi dependencies)
    restore_reconnect_config_standalone(server, port)

    # Import uwapi AFTER file restoration
    from uwapi import UwapiLibrary
    from bot3 import ObserverBot

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