#!/usr/bin/env python3
import json
import time
import requests
import pyttsx3
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
API_URL = "http://0.0.0.0:8000/api/last_games"
GEMINI_API_KEY = "AIzaSyDTKBca5SbNL2mjWGPuk3EubeEogN9snC8"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
POLL_INTERVAL = 5  # seconds

# Initialize text-to-speech engine
engine = pyttsx3.init()

def poll_games_api() -> Optional[List[Dict]]:
    """Poll the games API and return the JSON response."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error polling API: {e}")
        return None

def send_to_gemini(prompt: str) -> Optional[str]:
    """Send a prompt to Gemini API and return the response."""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        # Extract text from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None

def speak_announcement(text: str):
    """Use text-to-speech to announce the given text."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error with text-to-speech: {e}")

def parse_gemini_response(response: str) -> tuple[str, str]:
    """Parse Gemini response to extract announcement and context sections."""
    # Look for announcement and context sections
    announcement = ""
    context = ""
    
    lines = response.split('\n')
    current_section = None
    
    for line in lines:
        lower_line = line.lower().strip()
        if 'announcement' in lower_line and ':' in line:
            current_section = 'announcement'
            # Try to get text after the colon on the same line
            parts = line.split(':', 1)
            if len(parts) > 1:
                announcement = parts[1].strip()
        elif 'context' in lower_line and ':' in line:
            current_section = 'context'
            # Try to get text after the colon on the same line
            parts = line.split(':', 1)
            if len(parts) > 1:
                context = parts[1].strip()
        elif current_section == 'announcement' and line.strip():
            if announcement:
                announcement += " " + line.strip()
            else:
                announcement = line.strip()
        elif current_section == 'context' and line.strip():
            if context:
                context += " " + line.strip()
            else:
                context = line.strip()
    
    return announcement, context

def process_game_data(games_data: List[Dict]):
    """Process game data through a loop with Gemini AI."""
    print(f"\nProcessing {len(games_data)} game(s)...")
    
    # Initial prompt setup
    initial_prompt = f"""You are a game announcer AI. You've received game server data:
{json.dumps(games_data, indent=2)}

TODO: Additional command output will be inserted here in the future.

Please provide:
1. An announcement (1-2 sentences) about the game state that would be interesting for players to hear
2. Context for the next prompt that summarizes what you've learned

Format your response as:
Announcement: [Your announcement here]
Context: [Context for next iteration here]"""
    
    context = ""
    iteration = 0
    max_iterations = 3  # Limit iterations for now
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")
        
        # Prepare prompt with context
        if context:
            prompt = f"{context}\n\nBased on the previous context, provide:\n1. A new announcement about the game\n2. Updated context for the next prompt\n\nFormat your response as:\nAnnouncement: [Your announcement here]\nContext: [Context for next iteration here]"
        else:
            prompt = initial_prompt
        
        # Send to Gemini
        print("Sending to Gemini...")
        response = send_to_gemini(prompt)
        
        if response:
            print(f"\nGemini Response:\n{response}")
            
            # Parse response
            announcement, context = parse_gemini_response(response)
            
            if announcement:
                print(f"\nAnnouncement: {announcement}")
                speak_announcement(announcement)
            else:
                print("No announcement found in response")
            
            if not context:
                print("No context found for next iteration, ending loop")
                break
                
            # Small delay between iterations
            time.sleep(2)
        else:
            print("Failed to get response from Gemini")
            break
    
    print("\nGame processing complete")

def main():
    """Main loop that polls for games and processes them."""
    print("Starting game announcer...")
    print(f"Polling {API_URL} every {POLL_INTERVAL} seconds")
    
    processed_games = set()
    
    while True:
        try:
            # Poll for games
            games_data = poll_games_api()
            
            if games_data:
                # Check for new games (simple approach using datetime)
                new_games = []
                for game in games_data:
                    game_id = game.get('datetime', '')
                    if game_id and game_id not in processed_games:
                        new_games.append(game)
                        processed_games.add(game_id)
                
                if new_games:
                    print(f"\nFound {len(new_games)} new game(s)")
                    process_game_data(new_games)
                else:
                    print(".", end="", flush=True)
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nStopping game announcer...")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()