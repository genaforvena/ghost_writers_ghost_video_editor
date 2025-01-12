#!/bin/bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Guide the user through setting up the YouTube API key
echo "To use this script, you need a YouTube Data API key."
echo "Follow these steps to set it up:"
echo "1. Go to the Google Cloud Console: https://console.cloud.google.com/"
echo "2. Create a new project or select an existing project."
echo "3. Enable the YouTube Data API v3 for your project."
echo "4. Create credentials (API key) for the YouTube Data API v3."
echo "5. Copy the generated API key."
echo "6. Set the API key as an environment variable:"
echo "   On Windows: setx YOUTUBE_API_KEY \"YOUR_API_KEY\""
echo "   On macOS/Linux: export YOUTUBE_API_KEY=\"YOUR_API_KEY\""
echo "7. Restart your terminal or IDE to apply the changes."

# Hardcode the YouTube API key value
export YOUTUBE_API_KEY="AIzaSyCUrIjHo74FDWhr4YuY_2BBqQ"

echo "Setup complete. You can now run the script."
