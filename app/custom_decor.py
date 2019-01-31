from flask import request, redirect, url_for
from functools import wraps
from config import Config


def whitelisted(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Real-Ip') and request.headers.get('X-Real-Ip') not in Config.ALLOWED_IPS:
            print('redirecting non-whitelisted ip')
            return redirect(url_for('login', next=request.url))
        elif request.headers.get('Host') and request.headers.get('Host') not in Config.ALLOWED_IPS:
            print('redirecting non-whitelisted ip')
            return redirect(url_for('login', next=request.url))
        print('allowed IP {}'.format(request.headers.get('Host', 'X-Real-Ip')))
        return f(*args, **kwargs)
    return decorated_function
