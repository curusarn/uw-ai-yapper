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
│  Game Server    │────►│ Poll & Launch    │────►│  Observer Bot   │
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

### Running Observer Bot Manually

```bash
python python/main_observer.py <server-address> <port>
```

