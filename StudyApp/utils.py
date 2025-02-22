from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt="password-reset")

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(token, salt="password-reset", max_age=expiration)
        return email
    except:
        return None