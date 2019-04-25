import jwt
from datetime import timedelta, datetime

from django.conf import settings
from django.core.signing import TimestampSigner
from django.core.signing import BadSignature , SignatureExpired
from django.utils.crypto import get_random_string

from rest_framework.validators import ValidationError



def password_reset_code():
    code = get_random_string(length=7)
    return code

def sign_token():
    token = TimestampSigner(salt='extra')
    return token


def generate_safe_token(email):
    signer = sign_token().sign(email)
    return signer

def validate_code(code):
    try:
        safe_token = sign_token().unsign(code, max_age=5400)
        
    except (BadSignature, SignatureExpired):
            raise ValidationError('Code Expired')
    else:
        tokenize = safe_token
        return tokenize


def encode_user_payload(user):
        if isinstance(user, str):
                payload = {
                        'user': user ,
                        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_DELTA_MINTUES)}
        else:
                payload = {
                        'user': user.email ,
                        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_EXP_DELTA_MINTUES)}
        jwt_token = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
        return jwt_token.decode('utf-8')