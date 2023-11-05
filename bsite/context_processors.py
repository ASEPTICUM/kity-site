from bsite.services.bpay_api import bpay_api_settings
from config.constants import SETTINGS_TGBOT_LINK, GOOGLE_RECAPTCHA_SITE_KEY


def bpay_context_processor(request):
    user_token = request.session.get('user_token', '')
    tg_bot_link = bpay_api_settings(SETTINGS_TGBOT_LINK)['value']
    recaptcha_site_key = bpay_api_settings(GOOGLE_RECAPTCHA_SITE_KEY)['value']
    return {
            'user_token': user_token,
            'tg_bot_link': tg_bot_link,
            'recaptcha_site_key': recaptcha_site_key,
        }
