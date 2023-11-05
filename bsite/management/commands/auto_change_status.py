from django.core.management.base import BaseCommand

from bsite.email import send_order_overdue_email
from bsite.services.bpay_api import (
    # bpay_api_auto_update_order_status,
    bpay_api_settings,
    bpay_api_get_user
)
from config.constants import ORDER_STATUS_NEW, ORDER_STATUS_OVERDUE, SETTINGS_OVERDUE_TIME


class Command(BaseCommand):
    help = 'Update Rates'

    def handle(self, *args, **options):
        overdue_time = bpay_api_settings(SETTINGS_OVERDUE_TIME)['value']
        # orders = bpay_api_auto_update_order_status(ORDER_STATUS_OVERDUE, ORDER_STATUS_NEW, overdue_time)
        # for order in orders:
        #     user = bpay_api_get_user(order['user'])
        #     send_order_overdue_email(user, order)
        # self.stdout.write(self.style.SUCCESS("Done"))
