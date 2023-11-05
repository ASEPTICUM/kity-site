from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from bsite.services.bpay_api import bpay_api_auth_token_login, bpay_api_get_exchange_currency, bpay_api_get_currency

from django.utils.translation import get_language

from decimal import Decimal


class LoginForm(forms.Form):
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))

    def clean(self):
        cleaned_data = super().clean()
        mail = cleaned_data.get("mail")
        password = cleaned_data.get("password")
        login_request = bpay_api_auth_token_login(mail, password)
        if 'non_field_errors' in login_request:
            raise ValidationError(login_request['non_field_errors'])


class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError(_('Пароли не совпадают'))


class EditProfileForm(forms.Form):
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}), required=False)
    oldpassword = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def clean(self):
        user = self.user
        cleaned_data = super().clean()
        mail = cleaned_data.get("mail")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        oldpassword = cleaned_data.get("oldpassword")
        if password1 or password2:
            if password1 != password2:
                raise ValidationError(_('Пароли не совпадают'))
            login_request = bpay_api_auth_token_login(user['email'], oldpassword)
            if 'non_field_errors' in login_request:
                raise ValidationError(_("Старый пароль неверен!"))
        if mail != user['email']:
            login_request = bpay_api_auth_token_login(user['email'], oldpassword)
            if 'non_field_errors' in login_request:
                raise ValidationError(_("Старый пароль неверен!"))


class RegisterConfirm(forms.Form):
    mail = forms.EmailField(widget=forms.HiddenInput())


class RequestForm(forms.Form):
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'field', 'rows': '5', 'cols': '1'}))


class RecoverPasswordForm(forms.Form):
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))


class RecoverPasswordConfirmForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'field'}))

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError(_('Пароли не совпадают'))


class BaseExchangeForm(forms.Form):
    sum_from = forms.CharField(widget=forms.NumberInput(attrs={'step': 'any', 'min': 0.002}))
    sum_to = forms.CharField(widget=forms.NumberInput(attrs={'step': 'any', 'min': 0.002}))
    exchange_from = forms.IntegerField(widget=forms.HiddenInput())
    exchange_to = forms.IntegerField(widget=forms.HiddenInput())
    rate = forms.CharField(widget=forms.HiddenInput())
    order_type = forms.CharField(widget=forms.HiddenInput())


class ExternalToExternalExchangeForm(BaseExchangeForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'field'}))
    exchange_to_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'field'}))


class BalanceToExternalExchangeForm(BaseExchangeForm):
    exchange_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'field'}))


class ExternalToBalanceExchangeForm(BaseExchangeForm):
    pass


class ExchangeConfirmPayForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())


class PaymentsExchangeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'field'}))
    exchange_from_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'field'}))


