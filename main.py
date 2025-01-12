import youtube_dl
import cv2
import numpy as np
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import argparse
import requests
import os
from tqdm import tqdm

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
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise Exception("YouTube API key is missing.")
    
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
        raise Exception(f"Invalid YouTube API key: {api_key}")
    
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
        cap = cv2.VideoCapture('temp_video.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start * fps)
        end_frame = int(end * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))
        
        for i in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        cap.release()
        out.release()
        return output_file
    except Exception as e:
        print(f"Error processing video clip: {e}")
        return None

def find_matching_clips(text):
    sentences = text.split('.')
    clips = []
    
    for sentence in tqdm(sentences, desc="Processing sentences"):
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
            words = sentence.split()
            for word in words:
                video_ids = search_youtube(word)
                if not video_ids:
                    continue
                for video_id in video_ids:
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        increment_quota(10)
                        
                        for segment in transcript:
                            if word.lower() in segment['text'].lower():
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
                if any(clip.get('file') for clip in clips if not clip.get('fallback')):
                    break
            else:
                clips.append({'fallback': True, 'phrase': sentence})
    
    return clips

def calculate_text_length(text):
    words_per_minute = 150  # Average reading speed
    words = text.split()
    num_words = len(words)
    return num_words / words_per_minute * 60  # Length in seconds

def compile_video(clips, output_file, audio_file=None):
    final_clips = []
    
    for clip in tqdm(clips, desc="Compiling clips"):
        if not clip.get('fallback'):
            cap = cv2.VideoCapture(clip['file'])
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            
            cap.release()
            out.release()
            final_clips.append(output_file)
        else:
            blank_clip = np.zeros((720, 1280, 3), np.uint8)
            blank_clip.fill(0)
            final_clips.append(blank_clip)
    
    if not final_clips:
        print("No clips to compile.")
        return
    
    try:
        height, width, layers = final_clips[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        final_video = cv2.VideoWriter(output_file, fourcc, 30, (width, height))
        
        for clip in final_clips:
            if isinstance(clip, str):
                cap = cv2.VideoCapture(clip)
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    final_video.write(frame)
                cap.release()
            else:
                for _ in range(int(2 * 30)):  # 2 seconds of blank clip
                    final_video.write(clip)
        
        final_video.release()
        
        if audio_file and os.path.exists(audio_file):
            os.system(f"ffmpeg -i {output_file} -i {audio_file} -c:v copy -c:a aac -strict experimental {output_file}")
        
        text_length = calculate_text_length(" ".join([clip['phrase'] for clip in clips if clip.get('fallback')]))
        cap = cv2.VideoCapture(output_file)
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        if video_length < text_length:
            padding_clip = np.zeros((720, 1280, 3), np.uint8)
            padding_clip.fill(0)
            padding_duration = int((text_length - video_length) * 30)
            final_video = cv2.VideoWriter(output_file, fourcc, 30, (width, height))
            cap = cv2.VideoCapture(output_file)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                final_video.write(frame)
            cap.release()
            for _ in range(padding_duration):
                final_video.write(padding_clip)
            final_video.release()
        
        print(f"Final video saved as {output_file}")
    except Exception as e:
        print(f"Error compiling final video: {e}")

def verify_video_length(video_file, text_length, audio_length=None):
    cap = cv2.VideoCapture(video_file)
    video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if audio_length:
        if abs(video_length - audio_length) > 5:
            print(f"Warning: Video length ({video_length}s) does not match audio length ({audio_length}s).")
    else:
        if abs(video_length - text_length) > 5:
            print(f"Warning: Video length ({video_length}s) does not match text length ({text_length}s).")

def read_text_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r') as file:
        return file.read()

def find_and_compile(text_path, output_file, audio_file=None):
    text = read_text_from_file(text_path)
    clips = find_matching_clips(text)
    compile_video(clips, output_file, audio_file)
    text_length = calculate_text_length(text)
    audio_length = None
    if audio_file:
        cap = cv2.VideoCapture(audio_file)
        audio_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()
    verify_video_length(output_file, text_length, audio_length)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video montage from text.")
    parser.add_argument("text_path", help="Path to the input text file.")
    parser.add_argument("output_file", help="Path to the output video file.")
    parser.add_argument("--audio_file", help="Optional path to an audio file to replace all video audio.", default=None)
    args = parser.parse_args()
    
    find_and_compile(args.text_path, args.output_file, args.audio_file)
