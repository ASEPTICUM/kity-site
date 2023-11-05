from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import get_language
import locale
from bsite.services.bpay_api import bpay_api_get_langs
from bsite.services.language import bpay_api_get_langs_list
from bsite.utils import list_search
from django.conf import settings


class LocaleMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        lang = None 
        langs = bpay_api_get_langs()

        if langs:
            lang = list_search('language_code', get_language(), langs)
        
        if lang and 'locale' in lang:
            locale_code = lang['locale']
        else:
            locale_code = 'en_US.UTF-8'
        locale.setlocale(locale.LC_TIME, locale_code)
        return None



