from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json


with open('/home/beyond/Documents/NEW_SESSION/Python/machine learning/chatbot/Extended/Back End/config.json', 'r') as c:
    params = json.load(c) ['params']

# Load API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure the Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Store conversation history
conversation_history = []

# Configure file upload settings
# UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'gif', 'mp4', 'avi', 'mov'}
uploaded_file_content = ''

app.config['UPLOAD_FOLDER'] = params['upload_location']

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')

    if not user_message:
        return jsonify({"reply": "Please provide a message."}), 400

    try:
        # Store user message in the conversation history
        conversation_history.append(f"User: {user_message}")

        # Combine the conversation history to provide context to the model
        conversation_context = "\n".join(conversation_history[-5:])  # Keep only the last 5 exchanges
        response = model.generate_content(conversation_context)

        # Get the bot's response
        gemini_response = response.text  # Extract the text from the response
        # Add the bot's response to the history
        conversation_history.append(f" {gemini_response}")

        return jsonify({"reply": gemini_response})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads and return metadata."""
    global uploaded_file_metadata

    if 'file' not in request.files:
        return jsonify({"error": "No file found in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if allowed_file(file.filename):
        try:
            # Secure file name
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(file_path)

            # Store metadata
            uploaded_file_metadata = {
                "filename": filename,
                "path": file_path,
                "size": os.path.getsize(file_path),  # File size in bytes
                "type": file.content_type,  # MIME type
            }

            return jsonify({
                "message": "File uploaded successfully",
                "metadata": uploaded_file_metadata,
            }), 200

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    else:
        return jsonify({"error": "File type not allowed"}), 400


    # return jsonify({"message": "File uploaded successfully", "path": file_path}), 200


@app.route('/prompt', methods = ['POST'])
def imgprompt():
    global uploaded_file_metadata

    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400

        # Combine user message with file metadata
        if uploaded_file_metadata:
            file_details = (
                f"Uploaded File:\n"
                f"Name: {uploaded_file_metadata['filename']}\n"
                f"Type: {uploaded_file_metadata['type']}\n"
                f"Size: {uploaded_file_metadata['size']} bytes\n"
                f"Path: {uploaded_file_metadata['path']}\n"
            )
            combined_content = f"{file_details}\nUser Prompt:\n{user_message}"
        else:
            combined_content = f"User Prompt:\n{user_message} (No file uploaded yet)"

        # Simulate an AI response
        bot_response = f"Processed Input:\n{combined_content}"

        return jsonify({"reply": bot_response}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5000)
