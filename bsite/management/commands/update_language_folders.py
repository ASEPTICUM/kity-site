from django.core.management.base import BaseCommand
import os
from bsite.services.bpay_api import bpay_api_get_langs
from bsite.utils import list_search
from config.settings import BASE_DIR, LANGUAGE_CODE
import shutil


class Command(BaseCommand):
    help = 'Update Language'

    def handle(self, *args, **options):
        locale_folder = os.path.join(BASE_DIR, 'locale/')
        langs = bpay_api_get_langs()
        for lang in langs:
            lang_folder = locale_folder + lang['language_code']
            if not os.path.exists(lang_folder) and lang['language_code'] != LANGUAGE_CODE:
                os.mkdir(lang_folder)
        for list_lang_folder in os.listdir(locale_folder):
            if not list_search('language_code', list_lang_folder, langs):
                shutil.rmtree(locale_folder + list_lang_folder)

        self.stdout.write(self.style.SUCCESS("Done"))
