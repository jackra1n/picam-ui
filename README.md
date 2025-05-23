# picam-ui

Simple terminal interface for rapid photo capture with Raspberry Pi camera module.

## Features

- 🎨 Clean interface with optional Rich styling
- 📊 Live statistics and photo tracking
- 📸 One-key photo capture (spacebar)
- 📁 Automatic timestamped filenames
- 🕒 Recent photos display

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install picamera2 rich
   ```

2. **Run the application**:
   ```bash
   python3 main.py
   ```

3. **Take photos**:
   - Press **SPACEBAR** to capture
   - Press **R** to refresh stats
   - Press **Q** to quit

## Usage

### Basic Usage
```bash
python3 main.py
```
Photos saved to `photos/` directory.

### Custom Output Directory
```bash
python3 main.py /path/to/custom/directory
```

### File Naming
Photos are automatically named:
```
photo_YYYYMMDD_HHMMSS_XXX.jpg
```

Example:
```
photos/
├── photo_20241215_143022_001.jpg
├── photo_20241215_143025_002.jpg
└── photo_20241215_143028_003.jpg
```

## Controls

| Key | Action |
|-----|--------|
| `SPACEBAR` | Take a picture |
| `R` | Refresh statistics |
| `Q` | Quit application |
| `Ctrl+C` | Force quit |

## Requirements

- Raspberry Pi with camera module
- Python 3.7+
- picamera2
- rich (optional, for styling)

## Installation

```bash
pip install picamera2 rich
```

Or install from requirements:
```bash
pip install -r requirements.txt
```

## Interface

The interface shows:
- Camera status with initialization progress
- Session and total photo counts
- Last photo taken
- Recent photos list (last 5)
- Capture status indicator