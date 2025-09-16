# Muninn Voice Assistant

A family voice assistant that records and plays back personal stories/memories. Named after the Norse raven of memory, this device captures family stories for posterity as a 70th birthday gift.

## Hardware Requirements

- Raspberry Pi 5 (8GB RAM)
- Adafruit Voice Bonnet (I2S audio, dual microphones)
- 3W 4Ω enclosed speaker
- NeoPixel LED strip (60 LED/meter, 0.5m)
- Custom 3D printed cylindrical case

## Setup on Raspberry Pi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your Picovoice access key
```

### 3. Place Wake Word Model
Ensure your custom trained wake word model is in the project root:
- `munin_en_raspberry-pi_v3_0_0.ppn`

### 4. Run Muninn
```bash
python main.py
```

## Voice Commands

- **"Munin, remember this"** → Start recording a message
- **"Munin, play [family_member]'s messages"** → Play messages for specific family member
- **"Munin, stop"** → Stop current operation

## Family Members

The system supports messages for: CARRIE, CASSIE, SCOTT, BEAU, LIZZIE, JEAN, NICK, DAKOTA, BEA, CHARLIE, ALLIE, LUKE, LYRA, TUI, SEVRO

## Future Enhancements

See `FUTURE_FEATURES.md` for planned UI companion app that will allow:
- Web/mobile interface for browsing stored memories
- "Get a Memory" button for random story/joke/quote retrieval
- Family member filtering and memory categorization
- Remote access for family members anywhere

## Project Structure

```
muninn/
├── main.py                   # Application entry point
├── munin_en_raspberry-pi_v3_0_0.ppn  # Custom wake word model
├── .env                      # Environment configuration
├── config/
│   ├── settings.py          # Configuration management
│   └── family_names.py      # Family member definitions
├── audio/
│   ├── wake_word.py         # Porcupine wake word detection
│   ├── recorder.py          # Audio recording
│   ├── player.py           # Audio playback
│   └── speech_to_text.py   # Command parsing
├── led/
│   ├── controller.py       # NeoPixel management
│   └── animations.py       # LED effects
├── storage/
│   ├── database.py         # SQLite operations
│   └── file_manager.py     # Audio file organization
└── state/
    └── machine.py          # Application state management
```

## Expected Workflow

1. **Wake Word**: Say "Munin" → LED strip shows listening animation
2. **Command**: Give voice command → System processes and responds
3. **Recording**: "Remember this" → LED turns red, records until silence
4. **Playback**: "Play [name]'s messages" → Illuminates family member's LED section, plays messages
5. **Sleep**: Returns to idle mode with slow cycling family name colors

## Features

- Custom trained wake word detection
- Voice Activity Detection for automatic recording stop
- Family member-specific LED illumination
- SQLite database for message metadata
- Automatic hardware detection (Pi vs development)
- Graceful fallbacks for missing components

## Development Mode

When run on non-Pi hardware, automatically uses mock interfaces for testing the core logic without real hardware dependencies.