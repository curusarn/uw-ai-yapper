#!/usr/bin/env python3
import json
import time
import requests
import subprocess
import threading
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
API_URL = "http://0.0.0.0:8000/api/last_games"
POLL_INTERVAL = 5  # seconds

def poll_games_api() -> Optional[List[Dict]]:
    """Poll the games API and return the JSON response."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error polling API: {e}")
        return None

def launch_bot3_observer(server: str, port: int) -> subprocess.Popen:
    """Launch the bot3 observer directly"""

    # Run the bot3 directly from the python directory
    bot_script_path = "/home/simon/uw-ai-yapper/python/bot3_ai_yapper.py"

    cmd = [
        "python3",
        bot_script_path,
        server,
        str(port)
    ]

    print(f"Launching bot3 observer with command: {' '.join(cmd)}")

    try:
        # Start the process in the background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd="/home/simon/uw-ai-yapper/python"  # Set working directory
        )

        print(f"Bot3 observer started with PID: {process.pid}")
        return process

    except Exception as e:
        print(f"Failed to launch bot3 observer: {e}")
        return None

def monitor_bot_process(process: subprocess.Popen, game_info: Dict):
    """Monitor the bot process and report when it ends"""
    server = game_info.get('server', 'unknown')
    port = game_info.get('port', 'unknown')
    game_id = game_info.get('datetime', 'unknown')

    print(f"Monitoring bot3 for game {game_id} on {server}:{port}")

    try:
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        return_code = process.returncode

        print(f"Bot3 finished for game {game_id}")
        print(f"Exit code: {return_code}")

        if stdout:
            print("Bot3 stdout:")
            print(stdout)

        if stderr:
            print("Bot3 stderr:")
            print(stderr)

    except Exception as e:
        print(f"Error monitoring bot process: {e}")

def extract_game_info(game_data: Dict) -> Optional[Dict]:
    """Extract server and port information from game data"""

    # Look for server and port in the game data
    # The exact structure may vary, so we'll check common fields

    server = None
    port = None

    # Check various possible field names
    if 'server' in game_data:
        server = game_data['server']
    elif 'host' in game_data:
        server = game_data['host']
    elif 'address' in game_data:
        server = game_data['address']

    if 'port' in game_data:
        port = game_data['port']
    elif 'game_port' in game_data:
        port = game_data['game_port']

    # Try to extract from a combined address field
    if server is None and 'address' in game_data:
        address = game_data['address']
        if ':' in address:
            parts = address.split(':')
            if len(parts) == 2:
                server = parts[0]
                try:
                    port = int(parts[1])
                except ValueError:
                    pass

    # Default values if not found
    if server is None:
        server = "localhost"  # Default assumption

    if port is None:
        port = 7777  # Default game port

    return {
        'server': server,
        'port': port,
        'datetime': game_data.get('datetime', ''),
        'original_data': game_data
    }

def main():
    """Main loop that polls for games and launches bot3 observer"""
    print("Starting game poll and launch system...")
    print(f"Polling {API_URL} every {POLL_INTERVAL} seconds")

    processed_games = set()
    active_processes = {}  # game_id -> (process, thread)

    while True:
        try:
            # Poll for games
            games_data = poll_games_api()

            if games_data:
                # Check for new games
                new_games = []
                for game in games_data:
                    game_id = game.get('datetime', '')
                    if game_id and game_id not in processed_games:
                        new_games.append(game)
                        processed_games.add(game_id)

                if new_games:
                    print(f"\nFound {len(new_games)} new game(s)")

                    for game in new_games:
                        print(f"Processing new game: {json.dumps(game, indent=2)}")

                        # Extract server and port information
                        game_info = extract_game_info(game)
                        if game_info:
                            server = game_info['server']
                            port = game_info['port']
                            game_id = game_info['datetime']

                            print(f"Launching bot3 observer for game {game_id} on {server}:{port}")

                            # Launch the bot3 observer
                            process = launch_bot3_observer(server, port)

                            if process:
                                # Start monitoring thread
                                monitor_thread = threading.Thread(
                                    target=monitor_bot_process,
                                    args=(process, game_info),
                                    daemon=True
                                )
                                monitor_thread.start()

                                # Store the process and thread
                                active_processes[game_id] = (process, monitor_thread)

                                print(f"Bot3 observer launched successfully for game {game_id}")
                            else:
                                print(f"Failed to launch bot3 observer for game {game_id}")
                        else:
                            print(f"Could not extract server/port info from game data: {game}")

                else:
                    print(".", end="", flush=True)

            # Clean up finished processes
            finished_games = []
            for game_id, (process, thread) in active_processes.items():
                if process.poll() is not None:  # Process has finished
                    finished_games.append(game_id)

            for game_id in finished_games:
                print(f"\nBot3 observer for game {game_id} has finished")
                del active_processes[game_id]

            # Wait before next poll
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nStopping poll and launch system...")

            # Terminate any active bot processes
            for game_id, (process, thread) in active_processes.items():
                print(f"Terminating bot3 observer for game {game_id}")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing bot3 observer for game {game_id}")
                    process.kill()
                except Exception as e:
                    print(f"Error terminating process for game {game_id}: {e}")

            break

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()