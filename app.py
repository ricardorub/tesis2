from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Configura tu API Key de OpenRouter
OPENROUTER_API_KEY = "123452"
 
MODEL = "qwen/qwen3-30b-a3b:free"

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Llamada a OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",  # Opcional, para estadísticas
        "X-Title": "Mi Chatbot con Qwen",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        bot_reply = data['choices'][0]['message']['content']
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

if __name__ == '__main__':

    app.run(debug=True)
