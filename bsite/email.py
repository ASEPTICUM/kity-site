from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from bsite.utils import bpay_encrypt
from config.settings import EMAIL_HOST_USER


def send_order_create_email(user, order, request):
    from_email = EMAIL_HOST_USER
    str_id = bpay_encrypt(order['id'])
    subject = _('Статус заявки № %(id)s') % {'id': str(order['id'])}
    message = _('Ваша заявка ID %(id)s') % {'id': str(order['id'])} + '\n'
    message += _('Постоянная ссылка для отслеживания статуса заявки:') + '\n'
    message += request.build_absolute_uri(reverse('exchange', args=(str_id,)))
    send_mail(subject, message, from_email, [user['email']])


def send_order_overdue_email(user, order):
    from_email = EMAIL_HOST_USER
    subject = _('Статус заявки № %(id)s') % {'id': str(order['id'])}
    message = _('Ваша заявка ID %(id)s') % {'id': str(order['id'])} + '\n'
    message += _('Вы создали заявку, но платёж к нам пока не поступил, ' \
                 'либо находится на проверке у платёжной системы или банка. ' \
                 'Заявка временно перемещена в удалённые. ' \
                 'Если оплата прошла то обратитесь к службе поддержки сайта, ' \
                 'напишите номер Вашей заявки и предоставьте квитанцию об ' \
                 'успешной оплате.')

    send_mail(subject, message, from_email, [user['email']])
