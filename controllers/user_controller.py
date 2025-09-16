from models.db import db
from models.model import User

def register_user(username, email, password):
    try:
        if User.query.filter_by(email=email).first():
            return {'status': 'error', 'message': 'El correo electrónico ya está registrado.'}

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {'status': 'ok'}
    except Exception as e:
        db.session.rollback()
        print(f"Error en register_user: {e}")
        return {'status': 'error', 'message': 'Error al registrar el usuario.'}

def login_user(email, password):
    try:
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            return {'status': 'ok', 'user': user_data}
        else:
            return {'status': 'error', 'message': 'Correo electrónico o contraseña incorrectos.'}
    except Exception as e:
        print(f"Error en login_user: {e}")
        return {'status': 'error', 'message': 'Error al iniciar sesión.'}