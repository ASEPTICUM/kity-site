from typing import Union, Type, Tuple
from bsite.utils import bpay_decrypt, get_order_template_by_status
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from bsite.forms import (
    LoginForm,
    RegisterForm,
    RequestForm,
    RecoverPasswordForm,
    EditProfileForm,
    ExchangeConfirmPayForm,
    RecoverPasswordConfirmForm,
    PaymentsExchangeForm,
    ExternalToExternalExchangeForm,
    BalanceToExternalExchangeForm,
    ExternalToBalanceExchangeForm,
)

from django.http.request import HttpRequest
from django.views.decorators.http import require_GET
from django.http import HttpResponse, Http404
from django.views import View
from django.utils.translation import gettext_lazy as _, get_language
from django.http import HttpResponseForbidden

from bsite.services.bpay_api import *
from bsite.utils import get_ip_address, list_search, convert_to_preferred_format

from config.constants import (
    ORDER_STATUS_NEW,
    ORDER_STATUS_PAID,
    SETTINGS_OVERDUE_TIME,
    ORDER_STATUS_DONE,
    ORDER_TYPE_EXTERNAL_TO_BALANCE,
    ORDER_TYPE_BALANCE_TO_EXTERNAL,
    ORDER_TYPE_EXTERNAL_TO_EXTERNAL
)


import logging

logger = logging.getLogger(__name__)


def get_auth_token_by_request(request: HttpRequest):
    return request.session.get("user_token")


def get_user_from_request(request: HttpRequest):
    token = get_auth_token_by_request(request)
    if token:
        user = bpay_api_auth_user_me(token)
        if user.get("id"):
            return user
    return None


def _create_anonymous_user(email: str) -> Tuple[bool, Dict]:
    response = bpay_api_create_anonymous_user(email)
    if response.status_code != 201:
        return False, response.json()
    return True, response.json()


class BaseExchangeView(View):
    template_name = None
    order_type = None
    form_class: Union[Type[ExternalToBalanceExchangeForm], Type[BalanceToExternalExchangeForm]]

    def render(
            self,
            request,
            form: ExternalToBalanceExchangeForm,
            exchange_data,
            **extra
    ) -> HttpResponse:
        return render(request, self.template_name, {
            'form': form,
            'exchange_options': exchange_data['exchange_options'],
            'order_types': exchange_data["order_types"],
            **extra
        })

    def get_exchange_form(self, request: HttpRequest) \
            -> Union[ExternalToBalanceExchangeForm, BalanceToExternalExchangeForm]:
        # Strange shit, Django is not setting initial if data is passed and not
        # parsing well the request POST data if form data is initialized with something more than the request POST
        if request.method == "POST":
            return self.form_class(request.POST)

        user = get_user_from_request(request)
        email = ""
        if user is not None:
            email = user["email"]

        return self.form_class(initial={"order_type": self.order_type, "email": email})

    def get(self, request: HttpRequest):
        exchange_data = prepare_exchange_data()
        form = self.get_exchange_form(request)
        user = get_user_from_request(request)
        extra = {}
        if user:
            form.email = user["email"]
            extra["wallets"] = bpay_api_get_wallets_for_user(get_auth_token_by_request(request))

        return self.render(request, form, exchange_data, **extra)

    def post(self, request: HttpRequest):
        exchange_data = prepare_exchange_data()

        user = get_user_from_request(request)
        token = get_auth_token_by_request(request)
        form = self.get_exchange_form(request)

        if not form.is_valid():
            return self.render(request, form, exchange_data)

        if not user:
            success, result = _create_anonymous_user(form.data.get("email"))
            if not success:
                for field, error in result.items():
                    form.add_error(None, error)
                return self.render(request, form, exchange_data)

            token = request.session['user_token'] = result['key']
            user = get_user_from_request(request)

        statuses = bpay_api_get_statuses(token)
        order_type = form.data.get("order_type")
        order_type_id = list_search("machine_name", order_type, exchange_data["order_types"])["id"]
        exchange_from = form.data.get("exchange_from")
        exchange_to = form.data.get("exchange_to")

        order_creation_data = {
            "token": token,
            "user_id": user.get("id"),
            "order_type_id": order_type_id,
            "sum_from": form.data.get('sum_from'),
            "sum_to": form.data.get('sum_to'),
            "from_currency": exchange_from,
            "to_currency": exchange_to,
            "rate": form.data.get('rate'),
        }

        if self.order_type == ORDER_TYPE_EXTERNAL_TO_BALANCE:
            status = list_search("machine_name", ORDER_STATUS_NEW, statuses)
        elif self.order_type == ORDER_TYPE_BALANCE_TO_EXTERNAL:
            status = list_search("machine_name", ORDER_STATUS_PAID, statuses)
            order_creation_data["exchange_to_account"] = form.data.get("exchange_account")
        else:
            status = list_search("machine_name", ORDER_STATUS_NEW, statuses)
            order_creation_data["exchange_to_account"] = form.data.get("exchange_to_account")

        order_creation_data["status"] = status["id"]

        try:

            order = bpay_api_add_order(**order_creation_data)
        except APIException as e:
            for field, error in e.args[0].items():
                form.add_error(None, error)
            return self.render(request, form, exchange_data,
                               wallets=bpay_api_get_wallets_for_user(get_auth_token_by_request(request))
                               )

        str_id = bpay_encrypt(order['id'])
        # send_order_create_email(user, order, request)
        return redirect('exchange', str_id)


class MainExchangeView(BaseExchangeView):
    template_name = 'bsite/pages/index.html'
    order_type = ORDER_TYPE_EXTERNAL_TO_EXTERNAL
    form_class = ExternalToExternalExchangeForm


class TopUpBalanceView(BaseExchangeView):
    template_name = 'bsite/pages/exchanges/top_up_balance.html'
    order_type = ORDER_TYPE_EXTERNAL_TO_BALANCE
    form_class = ExternalToBalanceExchangeForm


class WithdrawalView(BaseExchangeView):
    template_name = 'bsite/pages/exchanges/withdrawal_balance.html'
    order_type = ORDER_TYPE_BALANCE_TO_EXTERNAL
    form_class = BalanceToExternalExchangeForm


def exchange(request, str_id):
    token = request.session.get("user_token")
    if not token:
        messages.error(request, _("Вы должны быть зарегистрированы для просмотра информации о заказе"))
        return redirect(reverse_lazy("login"))

    id = bpay_decrypt(str_id)
    order = bpay_api_order_load(token, id)
    order_types = bpay_api_get_order_types()
    order["order_type"] = list_search("id", order["order_type"], order_types)["machine_name"]
    if order['status']['machine_name'] == ORDER_STATUS_NEW:
        form = ExchangeConfirmPayForm({'id': id})

        curr_dt = int(round(datetime.now().timestamp()))
        order_open_date_timestamp = get_order_created_time(order)
        overdue_time = bpay_api_settings(SETTINGS_OVERDUE_TIME)['value']
        overdue_time_sec = int(overdue_time) * 60
        time_left = curr_dt - order_open_date_timestamp

        if overdue_time_sec - time_left < 0:
            change_order_status(token, id, ORDER_STATUS_OVERDUE)
            return redirect('exchange', str_id)
        overdue_time_m_s = convert_to_preferred_format(overdue_time_sec - time_left)

        if request.method == 'POST':
            form = ExchangeConfirmPayForm(request.POST)
            if form.is_valid():
                change_order_status(token, id, ORDER_STATUS_PAID)
                return redirect('exchange', str_id)
        return render(request, 'bsite/pages/exchange/wait_payment.html', {
            'order': order,
            'form': form,
            'overdue_time': overdue_time_m_s,
            'overdue_time_sec': overdue_time_sec - time_left,
        })

    else:
        template = get_order_template_by_status(order['status']['machine_name'])
        return render(request, template, {'order': order})


def user_login(request):
    form = LoginForm()
    if 'user_token' in request.session:
        return redirect('profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid(): #and request.recaptcha_is_valid
            login_request = bpay_api_auth_token_login(request.POST['mail'], request.POST['password'])
            request.session['user_token'] = login_request['auth_token']
            bpay_api_auth_user_me_update(request.session['user_token'], {'ip': get_ip_address(request)})
            return redirect('profile')

    return render(request, 'bsite/pages/login.html', {'form': form})


def user_register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid(): #and request.recaptcha_is_valid
            response = bpay_api_add_user(request.POST['email'], request.POST['password1'])
            if response.status_code != 201:
                error = json.loads(response.text)
                form.add_error(None, error)
            else:
                return redirect('register_confirm')

    return render(request, 'bsite/pages/register.html', {'form': form})


def user_register_confirm(request):
    return render(request, 'bsite/pages/register_confirm.html')


def user_profile(request):
    if 'user_token' in request.session:
        token = request.session['user_token']
        user = bpay_api_auth_user_me(token)
        if 'email' not in user:
            return redirect('logout')

        wallets = bpay_api_get_wallets_for_user(token)
        form = EditProfileForm({'mail': user['email']}, user=user)
        if request.method == 'POST':
            form = EditProfileForm(request.POST, user=user)
            if form.is_valid():
                user_profile_save(request)

        orders = bpay_api_get_user_orders(token, user['id'])
        page = request.GET.get('page', 1)
        paginator = Paginator(orders, 5)
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        result_orders = prepare_orders_data(token, orders)
        return render(request, 'bsite/pages/profile/base_profile.html', {
            'user': user,
            'form': form,
            'orders': result_orders,
            'wallets': wallets,
            'paginator': orders
        })
    else:
        return redirect('login')


def user_logout(request):
    if 'user_token' in request.session:
        bpay_api_auth_token_logout(request.session['user_token'])
        del request.session['user_token']
    return redirect('login')


def questions(request):
    questions = bpay_api_get_often_questions()
    return render(request, 'bsite/pages/questions.html', {'questions': questions})


def about_project(request):
    language = get_language()
    about_project_data = bpay_api_get_aboutproject_data(language)
    features = map(str.strip, about_project_data['features'].split('\n'))
    about_project_data['features'] = ''.join(['<h1>' + feature + '</h1>' for feature in features if feature])
    return render(request, 'bsite/pages/about_project.html', {"aboutproject": about_project_data})


def request_view(request):
    form = RequestForm(request.POST)
    token = request.session.get("user_token")
    if not token:
        form.add_error(None, _("Вы должны быть зарегистрированы чтобы оставлять отзывы"))
        return render(request, 'bsite/pages/request.html', {'form': form})

    user = bpay_api_auth_user_me(token)
    if 'email' in user:
        form = RequestForm({'mail': user['email']})

    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid(): #and request.recaptcha_is_valid
            bpay_api_add_feedback(token, request.POST['mail'], request.POST['text'])
            messages.success(request, _("Ваше сообщение отправлено!"))

    return render(request, 'bsite/pages/request.html', {'form': form})


def recover_password(request):
    form = RecoverPasswordForm()
    if request.method == 'POST':
        form = RecoverPasswordForm(request.POST)
        if form.is_valid(): #and request.recaptcha_is_valid
            bpay_api_auth_reset_password(request.POST['mail'])
            messages.success(request, _('Ссылка для восстановления пароля отправлена на ваш почтовый ящик!'))
    return render(request, 'bsite/pages/recover_password.html', {'form': form})


def password_reset_confirm(request, **kwargs):
    form = RecoverPasswordConfirmForm()
    if request.method == 'POST':
        form = RecoverPasswordConfirmForm(request.POST)
        if form.is_valid():
            bpay_api_auth_reset_password_confirm(kwargs.get('uid'), kwargs.get('token'), request.POST['password1'])
            messages.success(request, _('Ваш пароль успешно изменен!'))
            return redirect('login')
    return render(request, 'bsite/pages/recover_password_confirm.html', {'form': form})


def user_activate(request, **kwargs):
    bpay_api_auth_activate_user(kwargs.get('uid'), kwargs.get('token'))
    messages.success(request, _('Ваша учетная запись успешно активированна!'))
    return redirect('login')


def reviews(request):
    reviews = bpay_api_get_reviews()
    return render(request, 'bsite/pages/reviews.html', {'reviews': reviews})


def tos(request):
    return render(request, 'bsite/pages/tos.html')


def user_tg_confirm(request, str):
    json_string = bpay_decrypt(str)
    params = json.loads(json_string)
    user = bpay_api_get_user_by_email(params['email'])
    if user:
        if user['telegram_id']:
            raise Http404
        else:
            json_data = {
                'telegram_id': params['telegram_id'],
                'ip': get_ip_address(request),
            }
            bpay_api_auth_user_update(user['id'], json_data)
            return render(request, 'bsite/pages/confirmed.html')


def page(request, title):
    page = bpay_api_get_webpage(title)
    language = get_language()
    if language in page['translations'] and title != page['translations'][language]['title']:
        return redirect('page', page['translations'][language]['title'])
    return render(request, 'bsite/pages/webpage.html', {'page': page})


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# -----------------------For OtherOrder-----------------------#
def documentation(request):
    return render(request, 'bsite/pages/documentation.html')


def other_index(request, str_id):
    token = request.session.get("user_token")
    if not token:
        return HttpResponseForbidden(_("Вы должны быть авторизованы чтобы просматривать платежи"))
    id = bpay_decrypt(str_id)
    payment = bpay_api_get_payment(token, id)
    form = PaymentsExchangeForm()
    if request.method == 'POST':
        form = PaymentsExchangeForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = generate_password(8)
            user = bpay_api_get_user_by_email(email) or bpay_api_add_user(email, password)
            if not isinstance(user, dict):
                if user.status_code != 201:
                    error = json.loads(user.text)
                    if 'email' in error:
                        form.add_error(None, error['email'])
                        return render(request, 'bsite/pages/payments_index.html', {
                            'form': form,
                        })
                else:
                    user = json.loads(user.text)

            from_account = request.POST['exchange_from_account']
            to_account = payment.get('exchange_to_account')
            from_account = bpay_api_add_requisite(token, user['id'], from_account)['account'] or from_account
            to_account = bpay_api_add_requisite(token, user['id'], to_account)['account'] or to_account

            bpay_api_update_payment(token, id, {'exchange_from_account': from_account,
                                                'exchange_to_account': to_account,
                                                'user': user['id']})
            # send_order_create_email(user, order, request)
            return redirect('other_exchange', str_id)
    return render(request, 'bsite/pages/payments_index.html', {
        'form': form,
        'confirm_id': str_id,
        'payment': payment,
    })


def other_exchange(request, str_id):
    token = request.session.get("user_token")
    if not token:
        return HttpResponseForbidden(_("Вы должны быть зарегистрированы чтобы просматривать платежи"))

    id = bpay_decrypt(str_id)
    payment = bpay_api_payment_load(token, id)
    if payment['status']['machine_name'] == ORDER_STATUS_NEW:
        form = ExchangeConfirmPayForm({'id': id})

        curr_dt = int(round(datetime.now().timestamp()))
        order_open_date_timestamp = get_order_created_time(payment)
        overdue_time = bpay_api_settings(SETTINGS_OVERDUE_TIME)['value']
        overdue_time_sec = int(overdue_time) * 60
        time_left = curr_dt - order_open_date_timestamp

        if overdue_time_sec - time_left < 0:
            change_payment_status(token, id, ORDER_STATUS_OVERDUE)
            return redirect('other_exchange', str_id)
        overdue_time_m_s = convert_to_preferred_format(overdue_time_sec - time_left)

        if request.method == 'POST':
            form = ExchangeConfirmPayForm(request.POST)
            if form.is_valid():
                change_payment_status(token, id, ORDER_STATUS_PAID)
                return redirect('other_exchange', str_id)
        return render(request, 'bsite/pages/exchange/other_wait_payment.html', {
            'order': payment,
            'form': form,
            'overdue_time_m_s': overdue_time_m_s,
            'overdue_time_sec': overdue_time_sec - time_left,
        }
                      )

    else:
        if payment['status']['machine_name'] == ORDER_STATUS_DONE:
            return redirect(payment['redirect_url'])
        template = get_order_template_by_status(payment['status']['machine_name'])
        return render(request, template, {'order': payment})


def email_confirmed_page(request):
    return render(request, "bsite/pages/confirmed.html")

def amlkqc(request):
    return render(request, 'bsite/pages/amlkqc.html')