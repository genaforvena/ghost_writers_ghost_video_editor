
import youtube_dl
import moviepy.editor as mp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import argparse
import requests
import os

# Keep track of API usage
api_usage = 0
quota_limit = 10000  # Example limit

def check_quota():
    global api_usage
    if api_usage >= quota_limit:
        print("Quota limit reached. Try again tomorrow.")
        return False
    return True

def increment_quota(units):
    global api_usage
    api_usage += units

def search_youtube(query, max_results=5):
    if not check_quota():
        return []
    
    api_key = 'YOUR_API_KEY'
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key
    }
    
    response = requests.get(search_url, params=params)
    increment_quota(100)  # Each search request costs 100 units
    
    if response.status_code != 200:
        print(f"Error fetching search results: {response.text}")
        return []
    
    results = response.json().get('items', [])
    video_ids = [item['id']['videoId'] for item in results]
    return video_ids

def download_clip(video_id, start, end, output_file):
    if not check_quota():
        return None
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'temp_video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        increment_quota(1)
    except Exception as e:
        print(f"Error downloading video {video_id}: {e}")
        return None
    
    try:
        video = mp.VideoFileClip('temp_video.mp4').subclip(start, end)
        video.write_videofile(output_file, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        return output_file
    except Exception as e:
        print(f"Error processing video clip: {e}")
        return None

def find_matching_clips(text):
    sentences = text.split('.')
    clips = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        video_ids = search_youtube(sentence)
        if not video_ids:
            print(f"No videos found for phrase: '{sentence}'. Using fallback.")
            clips.append({'fallback': True, 'phrase': sentence})
            continue
        
        for video_id in video_ids:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                increment_quota(10)
                
                for segment in transcript:
                    if sentence.lower() in segment['text'].lower():
                        start = segment['start']
                        end = start + segment['duration']
                        clip_file = f'clip_{video_id}.mp4'
                        downloaded = download_clip(video_id, start, end, clip_file)
                        if downloaded:
                            clips.append({'file': downloaded, 'fallback': False})
                            break
                else:
                    continue
                break
            except TranscriptsDisabled:
                continue
            except Exception:
                continue
        
        if not any(clip.get('file') for clip in clips if not clip.get('fallback')):
            clips.append({'fallback': True, 'phrase': sentence})
    
    return clips

def compile_video(clips, output_file, audio_file=None):
    final_clips = []
    
    for clip in clips:
        if not clip.get('fallback'):
            final_clips.append(mp.VideoFileClip(clip['file']))
        else:
            blank_clip = mp.ColorClip(size=(1280, 720), color=(0, 0, 0), duration=2)
            final_clips.append(blank_clip)
    
    if not final_clips:
        print("No clips to compile.")
        return
    
    try:
        final_video = mp.concatenate_videoclips(final_clips, method='compose')
        if audio_file and os.path.exists(audio_file):
            final_audio = mp.AudioFileClip(audio_file)
            final_video = final_video.set_audio(final_audio)
        final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')
        print(f"Final video saved as {output_file}")
    except Exception as e:
        print(f"Error compiling final video: {e}")

def read_text_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        return file.read()

def find_and_compile(text_path, output_file, audio_file=None):
    text = read_text_from_file(text_path)
    clips = find_matching_clips(text)
    compile_video(clips, output_file, audio_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video montage from text.")
    parser.add_argument("text_path", help="Path to the input text file.")
    parser.add_argument("output_file", help="Path to the output video file.")
    parser.add_argument("--audio_file", help="Optional path to an audio file to replace all video audio.", default=None)
    args = parser.parse_args()
    
    find_and_compile(args.text_path, args.output_file, args.audio_file)
