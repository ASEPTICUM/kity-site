from typing import Dict, Optional
import json
from datetime import datetime
from decimal import Decimal
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from config.constants import ORDER_STATUS_CANCEL, ORDER_STATUS_DONE, ORDER_STATUS_PAID, ORDER_STATUS_NEW, \
    ORDER_STATUS_OVERDUE, ORDER_ORIGIN_MANUAL_FROM_SITE
from bsite.services.requests_api import RequestsApi
from bsite.utils import list_search, bpay_encrypt, render_decimal

from bsite.utils import generate_password, timed_cache

from django.conf import settings
from config.constants import PRIVATE_API_USER_EMAIL, PRIVATE_API_USER_PASSWORD


class APIException(Exception):
    pass


def bpay_api_get_request(token=''):
    if not token:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
    else:
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": "Token " + token
                   }
        print(settings.BPAY_API_URL)
    return RequestsApi(settings.BPAY_API_URL, headers=headers)


@timed_cache
def get_bpay_api_private_headers():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    request = bpay_api_get_request()
    response = request.post(
        f"/auth/token/login",
        json={
            "email": PRIVATE_API_USER_EMAIL,
            "password": PRIVATE_API_USER_PASSWORD
        },
        headers=headers
    )
    headers["Authorization"] = f"Token {response.json().get('auth_token')}"
    return headers


def create_private_request():
    private_headers = get_bpay_api_private_headers()
    return RequestsApi(settings.BPAY_API_URL, headers=private_headers)


def bpay_api_get_webpages():
    api_request = bpay_api_get_request()
    r = api_request.get("/webpages/")
    json_r = json.loads(r.text)
    return json_r


def bpay_api_get_webpage(title):
    api_request = bpay_api_get_request()
    r = api_request.get(f"/webpages/{title}")
    json_r = json.loads(r.text)
    return json_r


def bpay_api_get_aboutproject_data(language: str) -> Dict[str, str]:
    response = bpay_api_get_request().get("/aboutproject/")
    data = json.loads(response.text)
    if not data:
        return []
    translations = data[0]["translations"]
    return translations.get(language) or translations[settings.DEFAULT_LANGUAGE]


def bpay_api_auth_token_login(email, password):
    api_request = bpay_api_get_request()
    params = {
        "email": email,
        "password": password,
    }
    r = api_request.post("/auth/token/login/", json=params)

    json_r = json.loads(r.text)
    return json_r


def bpay_api_auth_reset_password(email):
    api_request = bpay_api_get_request()
    params = {
        "email": email,
    }
    api_request.post("/auth/users/reset_password/", json=params)


def bpay_api_auth_reset_password_confirm(uid, token, new_password):
    api_request = bpay_api_get_request()
    params = {
        "uid": uid,
        "token": token,
        "new_password": new_password,
    }
    api_request.post("/auth/users/reset_password_confirm/", json=params)


def bpay_api_auth_activate_user(uid, token):
    api_request = bpay_api_get_request()
    api_request.get(f"/auth/activate/{uid}/{token}")


def bpay_api_auth_token_logout(token):
    api_request = bpay_api_get_request(token)
    api_request.post("/auth/token/logout/")


def bpay_api_auth_user_me(token):
    api_request = bpay_api_get_request(token)
    r = api_request.get("/auth/users/me/")
    json_r = json.loads(r.text)
    return json_r


def bpay_api_get_user_by_email(email):
    api_request = bpay_api_get_request()
    response = api_request.get(f"/auth/users_email/{email}")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_auth_user_update(user_id, json_data):
    api_request = bpay_api_get_request()
    r = api_request.patch(f"/auth/users/{user_id}/", json=json_data)
    json_r = json.loads(r.text)
    return json_r


def bpay_api_auth_user_me_update(token, json_data):
    api_request = bpay_api_get_request(token)
    r = api_request.patch("/auth/users/me/", json=json_data)
    json_r = json.loads(r.text)
    return json_r


def bpay_api_auth_user_set_email(token, email, password):
    api_request = bpay_api_get_request(token)
    json_data = {
        'new_email': email,
        'current_password': password,
    }
    api_request.post("/auth/users/set_email/", json=json_data)


def bpay_api_auth_user_set_password(token, new_password, current_password):
    api_request = bpay_api_get_request(token)
    json_data = {
        'new_password': new_password,
        'current_password': current_password,
    }
    api_request.post("/auth/users/set_password/", json=json_data)


def bpay_api_add_user(email, password):
    api_request = bpay_api_get_request()
    json_data = {
        'telegram_id': 0,
        'email': email,
        'password': password,
        're_password': password,
        'ip': 0
    }

    return api_request.post("/auth/users/", json=json_data)


def bpay_api_create_anonymous_user(email):
    api_request = create_private_request()

    password = generate_password(8)
    data = {
        "email": email,
        "password": password,
        "re_password": password,
        "telegram_id": 0,
        "ip": 0
    }
    return api_request.post("/private/create_user_from_bot/", json=data)



def bpay_api_get_user(uid):
    api_request = bpay_api_get_request()
    response = api_request.get(f"/auth/users/{uid}")
    return json.loads(response.text)


# def bpay_api_get_or_create_user_by_email(email, password):
#     api_request = bpay_api_get_request()
#     json_data = {'email': email, 'password': password}
#     response = api_request.get("/user_by_email/", json=json_data)
#     return json.loads(response.text)


def bpay_api_get_order(token, order_id):
    api_request = bpay_api_get_request(token)
    response = api_request.get(f"/orders/{order_id}/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_payment(token, payment_id):
    api_request = bpay_api_get_request(token)
    response = api_request.get(f"/payments/{payment_id}/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


# Not used?
def bpay_api_put_payment(token, payment_id, json_data):
    api_request = bpay_api_get_request(token)
    response = api_request.put(f"/payments/{payment_id}", json=json_data)
    if response.status_code == 200:
        return response.json()


def bpay_api_add_order(
        token: str,
        user_id: int,
        order_type_id: int,
        sum_from: Decimal,
        sum_to: Decimal,
        rate: Decimal,
        from_currency,
        to_currency,
        status,
        exchange_from_account: str = None,
        exchange_to_account: str = None,
):
    order_origins = bpay_api_get_order_origins()
    order_origin_id = list_search("machine_name", ORDER_ORIGIN_MANUAL_FROM_SITE, order_origins)["id"]

    api_request = bpay_api_get_request(token)
    json_data = {
        "user": user_id,
        "order_type": order_type_id,
        "order_pay_amount": str(sum_from),
        "order_receivable_amount": str(sum_to),
        "exchange_from_currency": from_currency,
        "exchange_to_currency": to_currency,
        "exchange_from_account": exchange_from_account,
        "exchange_to_account": exchange_to_account,
        "value_currency": str(rate),
        "order_status": status,
        "order_origin": order_origin_id
    }

    response = api_request.post("/orders/", json=json_data)
    if response.status_code != 201:
        raise APIException(response.json())
    return response.json()


# Not used?
def bpay_api_get_requisites(token):
    api_request = bpay_api_get_request(token)
    response = api_request.get("/requisites/")
    return response.json()


def bpay_api_get_requisite(id):
    api_request = bpay_api_get_request()
    response = api_request.get(f"/requisites/{id}")
    return response.json()


def bpay_api_get_requisites_by_user(token, user_id):
    api_request = bpay_api_get_request(token)
    response = api_request.get(f"/requisites/by_user/{user_id}")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_wallets_for_user(token):
    api_request = bpay_api_get_request(token)
    response = api_request.get("/wallet/")
    return response.json()


def bpay_api_add_requisite(token, user_id, account):
    api_request = bpay_api_get_request(token)
    json_data = {
        'user': user_id,
        'account': account
    }
    response = api_request.post("/requisites/", json=json_data)
    if response.status_code == 201 or response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_currency(currency_id):
    api_request = bpay_api_get_request()
    response = api_request.get(f"/currencies/{currency_id}/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_currencies():
    api_request = bpay_api_get_request()
    response = api_request.get("/currencies/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


# Must be private
# But not used in urls
def bpay_api_update_exchange_currencies(id, json_data):
    api_request = bpay_api_get_request()
    return api_request.patch(f"/exchange_currencies/{id}/", json=json_data)


def bpay_api_get_langs():
    api_request = bpay_api_get_request()
    response = api_request.get("/languages/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_status(token, status_id):
    api_request = bpay_api_get_request(token)
    response = api_request.get(f"/statuses/{status_id}/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_statuses(token):
    api_request = bpay_api_get_request(token)
    response = api_request.get("/statuses/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_seo():
    api_request = bpay_api_get_request()
    response = api_request.get("/pages/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_user_orders(token, uid):
    api_request = bpay_api_get_request(token)
    response = api_request.get(f"/orders/all/{uid}/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_exchange_currency_by_currencies(cur_from_id: int, cur_to: int) -> Optional[Dict]:
    exchange_currencies = bpay_api_get_exchange_currencies()
    for exchange_currency in exchange_currencies:
        if exchange_currency["exchange_from"] == cur_from_id and exchange_currency["exchange_to"] == cur_to:
            return exchange_currency


def bpay_api_order_load(token, order_id):
    order = bpay_api_get_order(token, order_id)

    order['from_currency'] = bpay_api_get_currency(order['exchange_from_currency'])
    order['to_currency'] = bpay_api_get_currency(order['exchange_to_currency'])
    order['status'] = bpay_api_get_status(token, order['order_status'])

    exchange_currency = bpay_api_get_exchange_currency_by_currencies(
        order['exchange_from_currency'], order['exchange_to_currency']
    )

    rate_with_commission = Decimal(
        order['value_currency']) * (
            Decimal("1") - (Decimal(exchange_currency["commission"]) / Decimal("100")
        )
    )
    order['rate_from_str'] = '1 ' + order['from_currency']['symbol']
    order['rate_to_str'] = render_decimal(rate_with_commission) + ' ' + order["to_currency"]["symbol"]
    return order


def bpay_api_payment_load(token, payment_id):
    payment = bpay_api_get_payment(token, payment_id)
    currencies = bpay_api_get_currencies()
    statuses = bpay_api_get_statuses(token)
    payment['from_currency'] = list_search('symbol', payment['exchange_from_currency'], currencies)
    payment['to_currency'] = list_search('symbol', payment['exchange_to_currency'], currencies)
    payment['status'] = list_search('machine_name', payment['order_status'], statuses)
    if payment['from_currency']['symbol'] == 'RUB':
        payment['rate_from_str'] = str(payment['value_currency']) + ' RUB'
        payment['rate_to_str'] = '1 ' + payment['to_currency']['symbol']

    else:
        payment['rate_from_str'] = '1 ' + payment['from_currency']['symbol']
        payment['rate_to_str'] = str(payment['value_currency']) + ' RUB'
    return payment


def bpay_api_update_order(token, order_id, json_data):
    api_request = bpay_api_get_request(token)
    response = api_request.patch(f"/orders/{order_id}/", json=json_data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_update_payment(token, payment_id, json_data):
    api_request = bpay_api_get_request(token)
    response = api_request.patch(f"/payments/{payment_id}/", json=json_data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


# def bpay_api_auto_update_order_status(status, old_status, minutes):
#     api_request = bpay_api_get_request()
#     json_data = {
#         'status': status,
#         'old_status': old_status,
#         'minutes': minutes,
#     }
#     response = api_request.post("/change_statuses/", json=json_data)
#     if response.status_code == 200:
#         return json.loads(response.text)
#     else:
#         return None


def bpay_api_get_often_questions():
    api_request = bpay_api_get_request()
    response = api_request.get("/often_questions/")
    return json.loads(response.text)


def bpay_api_get_reviews():
    api_request = bpay_api_get_request()
    response = api_request.get("/reviews/")
    return json.loads(response.text)


def bpay_api_add_feedback(token, email, text):
    api_request = bpay_api_get_request(token)
    json_data = {
        'email': email,
        'text': text,
    }

    response = api_request.post("/feedbacks/", json=json_data)
    if response.status_code == 201:
        return json.loads(response.text)
    else:
        return None


def bpay_api_settings(name=''):
    api_request = bpay_api_get_request()
    json_data = {}
    if name:
        json_data = {
            'machine_name': name,
        }
    response = api_request.get("/settings/", json=json_data)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_exchange_categories():
    api_request = bpay_api_get_request()
    response = api_request.get("/exchange_category/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_exchange_currencies():
    api_request = bpay_api_get_request()
    response = api_request.get("/exchange_currencies/")
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def bpay_api_get_exchange_currency(currency_id):
    api_request = bpay_api_get_request()
    response = api_request.get("/exchange_currencies/" + str(currency_id) + '/')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def prepare_orders_data(token, orders):
    result_orders = []
    currencies = bpay_api_get_currencies()
    statuses = bpay_api_get_statuses(token)
    for order in orders:
        currency_from = list_search('id', order['exchange_from_currency'], currencies)
        currency_to = list_search('id', order['exchange_to_currency'], currencies)
        if currency_from['symbol'] != 'RUB':
            from_rate = 1
            to_rate = order['value_currency']
        else:
            to_rate = 1
            from_rate = order['value_currency']

        status = list_search('id', order['order_status'], statuses)
        if status['machine_name'] == ORDER_STATUS_NEW:
            status_class = 'madeRequest__status--wait'
        elif status['machine_name'] == ORDER_STATUS_PAID:
            status_class = 'madeRequest__status--wait'
        elif status['machine_name'] == ORDER_STATUS_DONE:
            status_class = 'madeRequest__status--success'
        elif status['machine_name'] == ORDER_STATUS_OVERDUE:
            status_class = 'madeRequest__status--error'
        elif status['machine_name'] == ORDER_STATUS_CANCEL:
            status_class = 'madeRequest__status--error'

        order_id = bpay_encrypt(order['id'])
        result_orders.append({
            'order_id': order_id,
            'order': order,
            'status': status,
            'status_class': status_class,
            'currency_from': currency_from,
            'currency_to': currency_to,
            'from_rate_symbol': currency_from['symbol'],
            'from_rate': from_rate,
            'to_rate_symbol': currency_to['symbol'],
            'to_rate': to_rate,
        }
        )
    return result_orders


def bpay_api_get_order_types():
    api_request = bpay_api_get_request()
    response = api_request.get("/order_types/")
    if response.status_code == 200:
        return response.json()


def bpay_api_get_order_origins():
    api_request = bpay_api_get_request()
    response = api_request.get("/order_origins/")
    if response.status_code == 200:
        return response.json()


def prepare_exchange_data():
    exchange_currencies = bpay_api_get_exchange_currencies()
    order_types = bpay_api_get_order_types()
    currencies = bpay_api_get_currencies()

    exchange_options = []
    for exchange_currency in exchange_currencies:
        exchange_currency['exchange_from_obj'] = list_search('id', exchange_currency['exchange_from'], currencies)
        exchange_currency['exchange_to_obj'] = list_search('id', exchange_currency['exchange_to'], currencies)

        exchange_options.append(exchange_currency)

    params = {
        "exchange_options": exchange_options,
        'order_types': order_types,
    }

    return params


def user_profile_save(request):
    if 'user_token' in request.session:
        token = request.session['user_token']
        user = bpay_api_auth_user_me(token)
        messages.success(request, _("Данные успешно изменены!"))
        if request.POST['mail'] != user['email']:
            bpay_api_auth_user_set_email(token, request.POST['mail'], request.POST['oldpassword'])
        if request.POST['password1']:
            bpay_api_auth_user_set_password(token, request.POST['password1'], request.POST['oldpassword'])


def get_order_created_time(order):
    order_open_date = datetime.strptime(order['order_open_date'], '%Y-%m-%dT%H:%M:%S.%f%z')
    order_open_date_timestamp = int(round(order_open_date.timestamp()))
    return order_open_date_timestamp


def change_order_status(token, order_id, status):
    statuses = bpay_api_get_statuses(token)
    new_status = list_search('machine_name', status, statuses)
    bpay_api_update_order(token, order_id, {'order_status': new_status['id']})


def change_payment_status(token, payment_id, status):
    statuses = bpay_api_get_statuses(token)
    new_status = list_search('machine_name', status, statuses)
    bpay_api_update_payment(token, payment_id, {'order_status': new_status['id']})

