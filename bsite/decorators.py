from django.contrib import messages
import requests
from django.utils.translation import gettext_lazy as _
from bsite.services.bpay_api import bpay_api_auth_user_me, bpay_api_settings
from config.constants import GOOGLE_RECAPTCHA_SECRET_KEY


def check_recaptcha(function):
    def wrap(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        secret = bpay_api_settings(GOOGLE_RECAPTCHA_SECRET_KEY)['value']
        if 'user_token' in request.session:
            token = request.session['user_token']
            user = bpay_api_auth_user_me(token)
            if 'email' in user:
                request.recaptcha_is_valid = True
                return function(request, *args, **kwargs)
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': secret,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                messages.error(request, _('Неверная reCAPTCHA. Пожалуйста, попробуйте еще раз.'))
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap