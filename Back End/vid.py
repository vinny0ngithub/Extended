import os
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
from dubbing_utils import create_dub_from_local_file, merge_audio_with_video

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVEN_API_KEY")

def extract_audio(video_path, audio_path):
    """ लोकल वीडियो से ऑडियो एक्सट्रैक्ट करें """
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_sle')  # WAV फॉर्मेट में सेव करें

if __name__ == "__main__":
    video_path = "palki.mp4"  # लोकल वीडियो फाइल
    audio_path = "temp_audio.wav"   # एक्सट्रैक्टेड ऑडियो फाइल
    output_video_path = "output_dubbed_video.mp4"

    # ऑडियो निकालें
    extract_audio(video_path, audio_path)

    # हिंदी डबिंग के लिए प्रोसेस करें
    dubbed_audio = create_dub_from_local_file(audio_path, "en", "hi")

    if dubbed_audio:
        print("Dubbing successful! Merging with video...")
        merge_audio_with_video(video_path, dubbed_audio, output_video_path)
        print("Final dubbed video saved at:", output_video_path)
    else:
        print("Dubbing failed.")
