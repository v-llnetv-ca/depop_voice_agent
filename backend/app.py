from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agent import process_message, text_to_speech

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_file('../frontend/index.html')

@app.route("/api/message", methods=["POST"])
def handle_message():
    """
    Main endpoint. Receives user message and optional perspective,
    runs the full agent loop, returns classification, reasoning,
    response text, and whether clarification is needed.
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]
    perspective = data.get("perspective", None)

    result = process_message(user_message, perspective)

    return jsonify(result)


@app.route("/api/speak", methods=["POST"])
def handle_speak():
    """
    TTS endpoint. Receives text, calls ElevenLabs,
    returns the audio file directly to the frontend.
    """
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"]
    audio_path = text_to_speech(text)

    if not audio_path:
        return jsonify({"error": "TTS failed"}), 500

    return send_file(audio_path, mimetype="audio/mpeg")


@app.route("/api/health", methods=["GET"])
def health():
    """
    Health check endpoint. Confirms the server is running.
    """
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)