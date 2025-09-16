from models.db import db
from models.model import Message

def enviar_mensaje(user_id, content):
    try:
        new_message = Message(user_id=user_id, content=content)
        db.session.add(new_message)
        db.session.commit()
        return {'status': 'ok'}
    except Exception as e:
        db.session.rollback()
        print(f"Error en enviar_mensaje: {e}")
        return {'status': 'error', 'message': 'Error al enviar el mensaje.'}


def obtener_mensajes(user_id):
    try:
        messages = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.asc()).all()
        return messages
    except Exception as e:
        print(f"Error en obtener_mensajes: {e}")
        return []