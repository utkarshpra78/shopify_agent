# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import run_agent

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for local dev

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")
    store_url = data.get("store_url")
    chat_history = data.get("chat_history", [])

    if not question:
        return jsonify({"error": "Missing question"}), 400

    # Call the agent
    response = run_agent(question, store_url, chat_history)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)