import os
import time
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip

# Load environment variables
load_dotenv()

# API Key सेट करें
ELEVENLABS_API_KEY = os.getenv("ELEVEN_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found! Please set it in your environment variables.")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def create_dub_from_local_file(audio_path: str, source_language: str, target_language: str) -> str:
    """ लोकल ऑडियो को Eleven Labs API से डब करें """
    with open(audio_path, "rb") as audio_file:
        response = client.dubbing.dub_a_video_or_an_audio_file(
            file=audio_file,
            source_lang=source_language,
            target_lang=target_language,
            mode="automatic",
            num_speakers=1,
            watermark=True
        )

    dubbing_id = response.dubbing_id

    if wait_for_dubbing_completion(dubbing_id):
        return download_dubbed_file(dubbing_id, target_language)
    else:
        return None

def wait_for_dubbing_completion(dubbing_id: str) -> bool:
    """ डबिंग पूरा होने का इंतजार करें """
    MAX_ATTEMPTS = 100
    CHECK_INTERVAL = 10  # सेकंड में

    for _ in range(MAX_ATTEMPTS):
        metadata = client.dubbing.get_dubbing_project_metadata(dubbing_id)
        if metadata.status == "dubbed":
            return True
        elif metadata.status == "dubbing":
            print(f"Dubbing in progress... Checking again in {CHECK_INTERVAL} seconds.")
            time.sleep(CHECK_INTERVAL)
        else:
            print("Dubbing failed:", metadata.error_message)
            return False

    print("Dubbing timed out!")
    return False

def download_dubbed_file(dubbing_id: str, language_code: str) -> str:
    """ डबbed फाइल को डाउनलोड करें """
    dir_path = f"data/{dubbing_id}"
    os.makedirs(dir_path, exist_ok=True)

    file_path = f"{dir_path}/{language_code}.mp3"
    with open(file_path, "wb") as file:
        for chunk in client.dubbing.get_dubbed_file(dubbing_id, language_code):
            file.write(chunk)

    return file_path

def merge_audio_with_video(video_path, new_audio_path, output_video_path):
    """ नए हिंदी ऑडियो को वीडियो में जोड़ें """
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(new_audio_path)
    final_video = video.set_audio(new_audio)
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
