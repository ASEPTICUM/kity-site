from typing import Callable
import base64
import logging
import secrets
import string
import traceback
from decimal import Decimal
from cryptography.fernet import Fernet
from config.constants import ORDER_STATUS_OVERDUE, ORDER_STATUS_CANCEL, ORDER_STATUS_DONE, ORDER_STATUS_PAID, \
    ENCRYPT_KEY
import time


def timed_cache(func: Callable) -> Callable:
    last_update_time = time.time()
    result = None

    def _wrapper():
        nonlocal last_update_time, result
        curr_date = time.time()
        if curr_date - last_update_time > 3600 or result is None:
            result = func()

        return result

    return _wrapper


def get_ip_address(request):
    user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip_address:
        ip = user_ip_address.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def list_search(key, value, list):
    return next(filter(lambda d: d.get(key) == value, list), None)


def convert_to_preferred_format(sec):
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    min = sec // 60
    sec %= 60
    return {'hour': hour, 'min': min, 'sec': sec}


def generate_password(len):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(len))
    return password


def bpay_encrypt(txt):
    try:
        txt = str(txt)
        fernet_key = Fernet(ENCRYPT_KEY)
        encrypted_text = fernet_key.encrypt(txt.encode('UTF-8'))
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("UTF-8")
        return encrypted_text
    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def bpay_decrypt(txt):
    try:
        txt = base64.urlsafe_b64decode(txt)
        fernet_key = Fernet(ENCRYPT_KEY)
        decoded_text = fernet_key.decrypt(txt).decode("UTF-8")
        return decoded_text
    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def get_order_template_by_status(status):
    if status == ORDER_STATUS_PAID:
        return 'bsite/pages/exchange/in_process.html'
    elif status == ORDER_STATUS_DONE:
        return 'bsite/pages/exchange/done.html'
    elif status == ORDER_STATUS_CANCEL:
        return 'bsite/pages/exchange/cancel.html'
    elif status == ORDER_STATUS_OVERDUE:
        return 'bsite/pages/exchange/cancel.html'


def render_decimal(number: Decimal) -> str:
    result = f"{number:.8f}".rstrip("0")
    if result.endswith("."):
        return result.replace(".", "")
    return result
