# Video Montage Generator

This Python project generates a video montage by extracting clips from YouTube videos based on input text. Optionally, it allows replacing all audio in the final video with a custom audio file.

## Features
- Parses input text from a file and searches for matching YouTube videos.
- Extracts video clips using text timestamps from YouTube transcripts.
- Compiles all clips into a final video.
- Optionally replaces all audio in the final video with a custom audio file.

## Requirements
- Python 3.7 or higher

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Dependencies
- `youtube_dl` or `yt_dlp` (for downloading YouTube videos)
- `moviepy` (for video editing)
- `youtube_transcript_api` (for fetching YouTube transcripts)
- `requests` (for interacting with the YouTube API)
- `argparse` (standard library, for command-line interface)

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

## Configuration
- Replace `YOUR_API_KEY` in the script with a valid YouTube Data API key to enable video searches.

## Notes
- Ensure that `youtube_dl` or `yt_dlp` is installed and working.
- The YouTube Data API has daily quota limits. Plan your usage accordingly.

## License
MIT License
