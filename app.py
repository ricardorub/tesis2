from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import requests
import os
from duckduckgo_search import DDGS
from models.pdf_processor import PDFProcessor
import re

# Importamos la instancia de la base de datos
from models.db import db

# Importamos nuestros controladores con MySQL
from controllers.user_controller import register_user, login_user
from controllers.chat_controller import enviar_mensaje, obtener_mensajes

app = Flask(__name__)

# Clave secreta para la sesión
app.secret_key = 'tu_clave_secreta_segura'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/tesis4_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos con la app
db.init_app(app)

# Configura tu API Key de OpenRouter
OPENROUTER_API_KEY = "TU_API_KEY_DE_OPENROUTER"
MODEL = "qwen/qwen3-30b-a3b:free"

# Inicializa el procesador de PDF
PDF_PROCESSOR = PDFProcessor("tesis.pdf")


# ============================
# FUNCIONES DE APOYO
# ============================
def search_web(query, max_results=3):
    """Busca en DuckDuckGo y devuelve snippets relevantes."""
    try:
        with DDGS() as ddgs:
            query_enhanced = f"{query} site:.edu OR site:.org OR site:.gob.mx OR site:.gov"
            results = ddgs.text(query_enhanced, max_results=max_results)
            snippets = [r['body'] for r in results if r.get('body')]
            return "\n\n".join(snippets) if snippets else ""
    except Exception as e:
        print(f"⚠️ Error buscando en web: {e}")
        return ""


def is_pdf_sufficient(pdf_chunks, user_query):
    """Decide si el PDF tiene suficiente información."""
    if not pdf_chunks:
        return False

    words = re.findall(r'\b[a-zA-Z]{3,}\b', user_query.lower())
    keywords = set(words[:5])  # Máximo 5 palabras clave

    found = 0
    keywords_to_check = list(keywords)

    for chunk in pdf_chunks:
        chunk_lower = chunk.lower()
        for kw in keywords_to_check:
            if kw in chunk_lower:
                found += 1
                keywords.discard(kw)
                if found >= 2:
                    return True
    return False


# ============================
# RUTAS DE AUTENTICACIÓN
# ============================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtenemos datos del formulario (no JSON)
        username = request.form.get('firstName') + " " + request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # Validación básica
        if password != confirm_password:
            return render_template('register.html', error="Las contraseñas no coinciden.")

        result = register_user(username, email, password)
        if result['status'] == 'ok':
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error=result['message'])

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtenemos del formulario (no JSON)
        usuario = request.form.get('usuario')  # puede ser email o username, según tu lógica
        password = request.form.get('password')

        result = login_user(usuario, password)
        if result['status'] == 'ok':
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            return redirect(url_for('chat_page'))
        else:
            return render_template('login.html', error=result['message'])

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))


# ============================
# RUTAS DE LA APP
# ============================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat_page():
    if 'user_id' not in session:
        flash('Por favor, inicia sesión para acceder al chat.', 'warning')
        return redirect(url_for('index'))
    mensajes = obtener_mensajes(session['user_id'])
    return render_template('chat.html', mensajes=mensajes)


@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "No autenticado"}), 401

    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Guardar el mensaje del usuario en MySQL
    enviar_mensaje(session['user_id'], user_message)

    # 🔍 Paso 1: Recuperar fragmentos del PDF
    relevant_chunks = PDF_PROCESSOR.retrieve_relevant_chunks(user_message, k=3)
    context_pdf = "\n\n".join(relevant_chunks)

    # 🚦 Paso 2: Decidir si usar solo PDF o también Web
    if is_pdf_sufficient(relevant_chunks, user_message):
        system_prompt = (
            "Eres un asistente de tesis virtual llamado 'Sofia'. "
            "Responde solo con información del PDF.\n\n"
            "=== CONTEXTO PDF ===\n"
            f"{context_pdf}\n"
        )
        source_label = "PDF"
    else:
        context_web = search_web(user_message, max_results=3)
        system_prompt = (
            "Eres un asistente de tesis virtual llamado 'Sofia'. "
            "Usa primero la información del PDF y luego, si es necesario, la de la web.\n\n"
            "=== CONTEXTO PDF ===\n"
            f"{context_pdf}\n"
            "=== CONTEXTO WEB ===\n"
            f"{context_web}\n"
        )
        source_label = "PDF + Web"

    # 🚀 Llamada a OpenRouter — ¡CORREGIDO: quitamos espacio al final de la URL!
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Mi Chatbot con Qwen",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",  # ← ESPACIO ELIMINADO
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        bot_reply = data['choices'][0]['message']['content']

        print(f"🧠 Respuesta generada usando: {source_label}")

        # Guardar respuesta del bot
        enviar_mensaje(session['user_id'], f"[SOFIA]: {bot_reply}")

        return jsonify({
            "reply": bot_reply,
            "source": source_label
        })

    except Exception as e:
        print(f"❌ Error en la llamada a OpenRouter: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500


# ============================
# MAIN
# ============================
if __name__ == '__main__':
    print("🚀 Iniciando app... cargando PDF...")
    app.run(debug=True)