from models.model import create_user, get_user_by_email
import bcrypt

# Registrar nuevo usuario
def register_user(username, email, password):
    # Verificar si ya existe el email
    user = get_user_by_email(email)
    if user:
        return {"status": "error", "message": "El usuario ya existe"}
    
    create_user(username, email, password)
    return {"status": "ok", "message": "Usuario registrado correctamente"}

# Iniciar sesión
def login_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}

    # Validar contraseña encriptada
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return {"status": "ok", "message": "Inicio de sesión correcto", "user": user}
    else:
        return {"status": "error", "message": "Contraseña incorrecta"}