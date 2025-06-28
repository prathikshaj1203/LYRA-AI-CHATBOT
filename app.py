from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-1.5-flash")
app = Flask(__name__)
MEMORY_FILE = "chat_memory.json"
MAX_HISTORY = 1500

def load_history():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f)


@app.route("/")
def home():
    return render_template("index.html", title="Lyra AI")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    try:
        history = load_history()
        chat = model.start_chat(history=history)
        response = chat.send_message(question)
        reply = response.text.strip()

        history.append({"role": "user", "parts": [question]})
        history.append({"role": "model", "parts": [reply]})
        save_history(history)

        if len(reply) > 2000:
            reply = reply[:2000] + "\n\n[Response trimmed]"

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {str(e)}"})

@app.route("/reset")
def reset():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    return "Chat reset"

if __name__ == "__main__":
    app.run(debug=True)
