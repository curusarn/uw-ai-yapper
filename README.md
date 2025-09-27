# UW-AI-Yapper

An AI-powered game announcer/commentator system for [Unnatural Worlds](https://store.steampowered.com/app/2369780/Unnatural_Worlds/) that provides real-time commentary using Google's Gemini AI and text-to-speech.

## Overview

UW-AI-Yapper automatically monitors active games on Unnatural Worlds servers, deploys observer bots to collect game state information, and generates engaging AI commentary that's announced via text-to-speech. The system maintains context between announcements to create coherent, story-like game narration.

## Features

- **Automatic Game Discovery**: Continuously polls game servers for active matches
- **Intelligent Observer Bots**: Deploys bots that join games as observers to collect detailed state information
- **AI-Generated Commentary**: Uses Google Gemini 2.0 Flash to create contextual, engaging game commentary
- **Text-to-Speech Announcements**: Announces game events using pyttsx3 and gTTS
- **Comprehensive Game Tracking**: Monitors force compositions, unit movements, battles, buildings, and economy
- **Multi-Language API Support**: Game integration available in Python, C++, and C#

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Game Servers   │────►│ Poll & Launch    │────►│  Observer Bots  │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Text-to-Speech │◄────│   AI Yapper      │◄────│   Game State    │
│                 │     │  (Gemini AI)     │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

- Python 3.x
- Google Cloud account with Gemini API access
- Unnatural Worlds game (Steam App ID: 2369780)
- Windows with WSL (for cross-platform bot execution)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/uw-ai-yapper.git
cd uw-ai-yapper
```

2. Install Python dependencies:
```bash
pip install requests pyttsx3 gtts google-generativeai
```

3. Set up your Google Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

4. Configure the game server URL in `ai_yapper.py`:
```python
url = 'http://your-game-server:port/api/getGames'
```

## Usage

### Running the AI Announcer

```bash
python ai_yapper.py
```

This will:
- Poll for active games
- Generate AI commentary for ongoing matches
- Announce game events via text-to-speech

### Running the Bot Launcher

```bash
python poll_and_launch_bot.py
```

This will:
- Monitor for new games
- Automatically deploy observer bots
- Manage multiple bot processes

### Running Observer Bots Manually

```bash
python python/main_observer.py --server <server-address> --port <port>
```

## Project Structure

```
uw-ai-yapper/
├── ai_yapper.py              # Main AI commentator
├── poll_and_launch_bot.py    # Automated bot launcher
├── python/
│   ├── bot3/                 # Observer bot implementation
│   │   ├── bot_observer.py   # Core observer logic
│   │   └── game_state.py     # Game state tracking
│   ├── uwapi/                # Python game API bindings
│   └── main_observer.py      # Observer entry point
├── c/                        # C++ API bindings
├── csharp/                   # C# API bindings
└── sphinx/                   # Documentation
```

## Configuration

### AI Yapper Settings

- `polling_interval`: Time between game checks (default: 10 seconds)
- `announcement_interval`: Time between AI announcements (default: 30 seconds)
- `max_context_length`: Maximum context history for AI (default: 10 announcements)

### Observer Bot Settings

- `report_interval`: How often bots report game state (default: 30 seconds)
- `reconnect_attempts`: Number of reconnection attempts (default: 3)

## Development

### Building Documentation

```bash
cd sphinx
make html
```

### Running Tests

```bash
python -m pytest tests/
```

## API Documentation

The `uwapi` directory contains game API bindings for:
- **Python**: Full-featured bindings with event callbacks
- **C++**: High-performance native bindings
- **C#**: .NET-compatible bindings

See the [API documentation](sphinx/build/html/index.html) for detailed usage.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Unnatural Worlds development team
- Google Gemini AI team
- Contributors and testers

## Contact

For questions or support, please open an issue on GitHub.