from models.model import save_chat, get_user_chats

# Guardar mensaje de un usuario
def enviar_mensaje(user_id, texto):
    save_chat(user_id, texto)
    return {"status": "ok", "message": "Mensaje enviado"}

# Obtener historial de mensajes de un usuario
def obtener_mensajes(user_id):
    mensajes = get_user_chats(user_id)
    return mensajes