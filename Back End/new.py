from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
import google.generativeai as genai
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import json
from flask_cors import CORS
from PIL import Image
import subprocess
from elevenlabs import generate, save

# Initialize Flask app
app = Flask(__name__)

CORS(app)

with open('/home/beyond/Documents/NEW_SESSION/Python/machine learning/chatbot/Extended/Back End/config.json', 'r') as c:
    params = json.load(c) ['params']

# UPLOAD_FOLDER = params['upload_location']
UPLOAD_FOLDER = os.path.join(app.root_path, params['upload_location'])
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# Configure the Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")


# Store conversation history
conversation_history = []

def dub_video(video_path, text, language='hindi'):
    try:
        # Generate audio
        audio = generate(
            api_key=ELEVEN_API_KEY,
            text=text,
            voice="Rachel" if language == 'english' else "EXAVITQu4vr4xnSDxMaL",
            model="eleven_multilingual_v2"
        )
        
        # Save audio
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dub_audio.mp3')
        save(audio, audio_path)
        
        # Merge with FFmpeg
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dubbed_video.mp4')
        subprocess.run([
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_path
        ], check=True)
        
        return output_path
        
    except Exception as e:
        raise e

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def hello():
    return render_template('Mukhda.html')

@app.route('/chat', methods=['POST'])
def chat():
    
    if request.method == 'POST':
        # message = request.form.get('message')
        user_message = request.form.get('message', '')
        file = request.files.get('file') 

    if not user_message and not file:
        return jsonify({"reply": "Please provide a message or upload a file."}), 400
    
    if user_message and file:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.root_path, UPLOAD_FOLDER, filename)
            file.save(filepath)
            print(f"File '{filename}' saved to '{filepath}'") 

            # Determine file type and preprocess (basic example)
            if filename.lower().endswith(('.jpg', '.jpeg', 'webp', 'heic', 'heif', '.png', '.gif')):
                file_type = "image"
                img = Image.open(filepath)
                conversation_history.append(f"User: {user_message,img} (with file: {img})")
                conversation_context = "\n".join(conversation_history)
                response = model.generate_content([user_message, img])
                gemini_response = response.text
                conversation_history.append(f"{gemini_response}")
                return jsonify({"reply": gemini_response})
            if filename.lower().endswith(('mp4', 'mpeg', 'mov', 'avi', 'x-flv', 'mpg', 'webm', 'wmv', '3gpp')):
                try:
                    video_file = genai.upload_file(path=filepath)
                    response = model.generate_content([user_message, video_file])
                    gemini_response = response.text
                    
                    if 'dub' in user_message.lower() or 'translate' in user_message.lower():
                        dubbed_path = dub_video(filepath, gemini_response)
                        return jsonify({
                            "reply": gemini_response,
                            "dubbed_video": url_for('uploaded_file', filename=os.path.basename(dubbed_path), _external=True)
                        })
                        
                    # Original return
                    return jsonify({"reply": gemini_response})

                except Exception as e:
                    return jsonify({"reply": f"Error: {str(e)}"}), 500
                
            if filename.lower().endswith(('.wav', '.mp3', 'flac', 'aiff', 'aac', 'ogg')):
                file_type = "audio"
                audio_file = genai.upload_file(filepath)
                conversation_history.append(f"User: {user_message,audio_file} (with file: {audio_file})")
                conversation_context = "\n".join(conversation_history)
                response = model.generate_content([user_message, audio_file])
                gemini_response = response.text
                conversation_history.append(f"{gemini_response}")
                return jsonify({"reply": gemini_response})
            if filename.lower().endswith(('.pdf')):
                file_type = "PDF"
                pdf_file = genai.upload_file(filepath)
                conversation_history.append(f"User: {user_message,pdf_file} (with file: {pdf_file})")
                conversation_context = "\n".join(conversation_history)
                response = model.generate_content([user_message, pdf_file])
                gemini_response = response.text
                conversation_history.append(f"{gemini_response}")
                return jsonify({"reply": gemini_response})
            if filename.lower().endswith(('.docx')):
                file_type = "Document"
            else:
                file_type = "other" 
    
    
    if user_message and not file:

        try:
            # Store user message in the conversation history
            conversation_history.append(f"User: {user_message}")

            # Combine the conversation history to provide context to the model
            conversation_context = "\n".join(conversation_history)  # Keep only the last 5 exchanges
            response = model.generate_content(conversation_context)

            # Get the bot's response
            gemini_response = response.text  # Extract the text from the response
            # Add the bot's response to the history
            conversation_history.append(f" {gemini_response}")

            return jsonify({"reply": gemini_response})

        except Exception as e:
            return jsonify({"reply": f"Error: {str(e)}"}), 500
    



if __name__ == '__main__':
    app.run(debug=True, port=5000)
