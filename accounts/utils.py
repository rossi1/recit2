from datetime import timedelta, datetime

from django.conf import settings
from django.core.signing import TimestampSigner
from django.core.signing import BadSignature , SignatureExpired
from django.utils.crypto import get_random_string

from rest_framework.validators import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


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


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }