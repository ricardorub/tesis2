# views/chat_view.py
from flask import request, render_template, jsonify
from models.chat_model import ChatModel

def setup_routes(app):
    @app.route("/")
    def index():
        return render_template("chat.html")

    @app.route("/chat", methods=["POST"])
    def chat():
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "Mensaje vacío"}), 400

        result = ChatModel.send_message(user_message)
        return jsonify(result)