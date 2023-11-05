from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, get_language
from datetime import datetime
from django.urls import translate_url as django_translate_url, reverse
from bsite.services.bpay_api import bpay_api_get_webpages, bpay_api_get_webpage, bpay_api_settings, bpay_api_get_seo
from bsite.utils import list_search

from config.constants import (
    SETTINGS_INFO_FOOTER_BLOCK_PAGE,
    SETTINGS_CONTACT_FOOTER_BLOCK_PAGE,
    MANAGER_TELEGRAM_LINK
)

register = template.Library()


@register.inclusion_tag('bsite/tags/error_message.html')
def error_message(message):
    return {"message": message}


@register.inclusion_tag('bsite/tags/success_message.html')
def success_message(message):
    return {"message": message}


@register.inclusion_tag('bsite/tags/currency_icon.html')
def currency_icon(currency):
    return {"currency": currency}


@register.simple_tag
def header_menu():
    menu = []

    menu.append({'link': reverse("about_project"), 'name': _('О проекте')})
    menu.append({'link': reverse('index'), 'name': _('Обмен')})
    webpages = bpay_api_get_webpages()
    for webpage in webpages:
        if webpage['footer_or_header'] == 'header':
            title = trans_field(webpage['translations'], 'title')
            link = reverse('page', args=[title])
            menu.append({'link': link, 'name': title})
    menu.append({'link': reverse('reviews'), 'name': _('Отзывы')})
    menu.append({'link': reverse('questions'), 'name': _('Частые вопросы')})
    menu.append({'link': MANAGER_TELEGRAM_LINK, 'name': _('Поддержка')})

    return menu


@register.simple_tag
def footer_menu():
    menu = []
    webpages = bpay_api_get_webpages()
    contact_page_name = bpay_api_settings(SETTINGS_CONTACT_FOOTER_BLOCK_PAGE)['value']
    info_page_name = bpay_api_settings(SETTINGS_INFO_FOOTER_BLOCK_PAGE)['value']
    for webpage in webpages:
        if webpage['footer_or_header'] == 'footer' \
                and webpage['translations']['ru']['title'] != contact_page_name \
                and webpage['translations']['ru']['title'] != info_page_name:
            title = trans_field(webpage['translations'], 'title')
            link = reverse('page', args=[title])
            menu.append({'link': link, 'name': title})
    menu.append({'link': reverse('reviews'), 'name': _('Обратная связь')})

    return menu


@register.simple_tag
def footer_info_block():
    try:
        page_name = bpay_api_settings(SETTINGS_INFO_FOOTER_BLOCK_PAGE)['value']
        webpage = bpay_api_get_webpage(page_name)
        content = trans_field(webpage['translations'], 'content')
    except:
        content = ''
    return content


@register.simple_tag
def footer_contact_block():
    try:
        page_name = bpay_api_settings(SETTINGS_CONTACT_FOOTER_BLOCK_PAGE)['value']
        webpage = bpay_api_get_webpage(page_name)
        content = trans_field(webpage['translations'], 'content')
    except:
        content = ''
    return content


@register.simple_tag
def strdate_change_format(str, old_format, new_format):
    return datetime.strptime(str, old_format).strftime(new_format)


@register.simple_tag(takes_context=True)
def translate_url(context, lang_code):
    path = context.get('request').get_full_path()
    return django_translate_url(path, lang_code)


@register.simple_tag(takes_context=True)
def title(context, type='', title=''):
    path = context.get('request').get_full_path()
    seo = bpay_api_get_seo()
    params = list_search('url', path, seo)

    if params:
        return params['title']

    elif title and type == 'custom':
        return _(title) + ' - BPAY'

    return 'BPAY'


@register.simple_tag(takes_context=True)
def description(context):
    path = context.get('request').get_full_path()
    seo = bpay_api_get_seo()
    params = list_search('url', path, seo)
    if params:
        return mark_safe('<meta name="description" content="' + params['description'] + '">')
    return ''

@register.filter
def trans_field(obj, field):
    language = get_language()
    fields = obj.get(language, 'ru')
    if field in fields:
        return fields.get(field)
    else:
        return obj.get('ru').get(field)
