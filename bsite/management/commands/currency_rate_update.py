import json
import requests
from django.core.management.base import BaseCommand
import time
from bsite.services.bpay_api import bpay_api_get_currencies, bpay_api_get_exchange_currencies, \
    bpay_api_update_exchange_currencies
from bsite.utils import list_search
from config.constants import BINANCE_API_URL
from datetime import datetime


class Command(BaseCommand):
    help = 'Update Rates'

    def handle(self, *args, **options):
        currencies = bpay_api_get_currencies()
        exchange_currencies = bpay_api_get_exchange_currencies()
        for exchange_currency in exchange_currencies:
            exchange_from = list_search('id', exchange_currency['exchange_from'], currencies)
            exchange_to = list_search('id', exchange_currency['exchange_to'], currencies)
            response = json.loads(requests.get(
                BINANCE_API_URL + '?symbol=' + exchange_from['symbol'] + exchange_to[
                    'symbol']).text)
            if 'code' in response:
                time.sleep(1)
                response = json.loads(requests.get(
                    BINANCE_API_URL + '?symbol=' + exchange_to['symbol'] + exchange_from[
                        'symbol']).text)
            now = datetime.now()

            json_data = {
                'value_currency': int(float(response['price'])),
                'created_at': now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            }
            bpay_api_update_exchange_currencies(exchange_currency['id'], json_data)
            time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Done"))
