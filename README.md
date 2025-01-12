# Video Montage Generator

This Python project generates a video montage by extracting clips from YouTube videos based on input text. Optionally, it allows replacing all audio in the final video with a custom audio file.

## Features
- Parses input text from a file and searches for matching YouTube videos.
- Extracts video clips using text timestamps from YouTube transcripts.
- Compiles all clips into a final video.
- Optionally replaces all audio in the final video with a custom audio file.
- Verifies that the final video length is approximately equal to the text length or audio track length.
- Slows down each clip by 10 times for transformation.
- Applies an extreme low-pass filter to the audio.

## Requirements
- Python 3.7 or higher

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Dependencies
- `youtube_dl` or `yt_dlp` (for downloading YouTube videos)
- `opencv-python` (for video editing)
- `youtube_transcript_api` (for fetching YouTube transcripts)
- `requests` (for interacting with the YouTube API)
- `argparse` (standard library, for command-line interface)
- `nltk` (for natural language processing)
- `scipy` (for signal processing)

## Usage
Run the script using the following command:

```bash
python script.py <text_path> <output_file> [--audio_file <audio_file>]
```

### Positional Arguments
- `<text_path>`: Path to the input text file containing the text to process.
- `<output_file>`: Path to the output video file.

### Optional Arguments
- `--audio_file <audio_file>`: Path to an audio file to replace all audio in the final video.
- `--setup_api_key`: Guide to set up YouTube API key.

### Example
```bash
python script.py input_text.txt output_video.mp4 --audio_file background_audio.mp3
```

## How It Works
1. **Text Input**: The script reads text from a file specified by the user.
2. **YouTube Search**: It searches YouTube for videos matching sentences in the text.
3. **Video Clips**: Using YouTube transcripts, it extracts clips corresponding to the text.
4. **Video Compilation**: Combines all clips into a single video.
5. **Audio Replacement** (optional): Replaces the original audio of the final video with the specified audio file.
6. **Video Length Verification**: Ensures the final video length is approximately equal to the text length or audio track length.
7. **Clip Transformation**: Slows down each clip by 10 times and applies an extreme low-pass filter to the audio.

## Configuration
- Replace `YOUR_API_KEY` in the script with a valid YouTube Data API key to enable video searches.

## Notes
- Ensure that `youtube_dl` or `yt_dlp` is installed and working.
- The YouTube Data API has daily quota limits. Plan your usage accordingly.
- This project aims to respect copyright laws by transforming the content.

## License
MIT License

## New Features
- Added progress indicators to show the progress of the script run.
- Added functions `calculate_text_length` and `verify_video_length` to ensure the final video length matches the text length or audio track length.

## Running Tests
To run the tests, use the following command:

```bash
python -m unittest discover
```

This will discover and run all the test cases in the project, including the `test_find_and_compile` function.

## Installing NLTK and Downloading Necessary Data
To install NLTK and download the necessary data, follow these steps:

1. Install NLTK using pip:
```bash
pip install nltk
```

2. Download the necessary NLTK data:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Setting Up the YouTube API Key
To use this script, you need a YouTube Data API key. Follow these steps to set it up:

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select an existing project.
3. Enable the YouTube Data API v3 for your project.
4. Create credentials (API key) for the YouTube Data API v3.
5. Copy the generated API key.
6. Set the API key as an environment variable:
   - On Windows: `setx YOUTUBE_API_KEY "YOUR_API_KEY"`
   - On macOS/Linux: `export YOUTUBE_API_KEY="YOUR_API_KEY"`
7. Restart your terminal or IDE to apply the changes.

## Running the Setup Script
To simplify the setup process, you can use the provided `setup.sh` script. This script will install the required dependencies and guide you through setting up the YouTube API key.

### Running the Setup Script
1. Make the script executable:
```bash
chmod +x setup.sh
```

2. Run the script:
```bash
./setup.sh
```

The script will install the dependencies listed in `requirements.txt` and provide instructions for setting up the YouTube API key. The YouTube API key value `AIzaSyCUrIjHo74FDWhr4YuY_2BBqQ` is hardcoded in the script.

### Example
```bash
./setup.sh
```
