# AI Voice Assistant 🎙️

## Overview

AI Voice Assistant is a Python-based desktop assistant that listens to voice commands and performs various tasks such as searching Wikipedia, opening websites, telling the current time, and generating jokes using voice responses.

## Features

* 🎤 Voice Recognition
* 🔊 Text-to-Speech Response
* 📚 Wikipedia Search
* 🌐 Open Google
* ▶️ Open YouTube
* 🎬 Open Hotstar
* ⏰ Tell Current Time
* 😂 Tell Jokes
* 🚪 Exit Using Voice Commands

## Technologies Used

* Python
* SpeechRecognition
* Pyttsx3
* Wikipedia
* PyJokes
* Webbrowser
* Datetime

## Project Structure

AI-Voice-Assistant/

├── voice_assistant.py

├── requirements.txt

├── README.md

└── screenshots/

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AI-Voice-Assistant.git
cd AI-Voice-Assistant
```

### Install Required Libraries

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pyttsx3
pip install SpeechRecognition
pip install wikipedia
pip install pyjokes
pip install pyaudio
```

## Run the Project

```bash
python voice_assistant.py
```

## Voice Commands Supported

| Command           | Action                |
| ----------------- | --------------------- |
| Open YouTube      | Opens YouTube         |
| Open Google       | Opens Google          |
| Open Hotstar      | Opens Disney+ Hotstar |
| Wikipedia + Topic | Searches Wikipedia    |
| Time              | Tells Current Time    |
| Joke              | Tells a Random Joke   |
| Exit / Stop       | Closes Assistant      |

## Example

User: Open YouTube

Assistant: Opening YouTube

User: What is Python on Wikipedia

Assistant: Searching Wikipedia...

User: Tell me a joke

Assistant: (Speaks a random joke)

## Future Improvements

* Weather Updates
* Open Applications
* Email Sending
* WhatsApp Messaging
* AI Chat Integration
* News Headlines
* Music Playback

## Author

Pratap Bondar

## License

This project is licensed under the MIT License.
