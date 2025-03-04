import os
import secrets
from PIL import Image
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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (320, 320)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    width, height = i.size

    side_length = min(width, height)

    left = (width - side_length) // 2
    top = (height - side_length) // 2
    right = left + side_length
    bottom = top + side_length

    i = i.crop((left, top, right, bottom))

    i.save(picture_path)

    return picture_fn