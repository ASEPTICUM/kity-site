from requests.exceptions import ConnectionError
from django.utils.translation import gettext_lazy as _
from bsite.services.bpay_api import bpay_api_get_langs


def bpay_api_get_langs_list():
    try:
        langs = bpay_api_get_langs()
    except ConnectionError:
        return None     
    if not langs:
        return None
    data = []
    for lang in langs:
        data.append((lang['language_code'], _(lang['name'])))
    return data
