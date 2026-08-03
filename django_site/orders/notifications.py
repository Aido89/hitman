"""Out-of-band notifications for new order leads.

A lead that only lands in the database is a lead nobody knows about until
someone opens /admin/. These helpers push it to Telegram and/or email the
moment it arrives.

Two hard rules:

1. **Never break the lead.** The customer's submission must succeed even if
   Telegram is down, the token is wrong, or SMTP times out. Every failure is
   swallowed and logged — the row is already committed by the time we run.
2. **Never block the response.** Delivery runs on a background thread, so the
   customer isn't kept waiting on a third-party API.
"""

import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

_TELEGRAM_API = 'https://api.telegram.org/bot{token}/sendMessage'


def _format_lead(lead, admin_url=None):
    """Human-readable summary shared by every channel."""
    lines = [
        '🔔 НОВАЯ ЗАЯВКА — Hitman IT',
        '',
        f'Услуга: {lead.service_label or lead.service_type}',
        f'Сумма: {lead.total:,} ₸'.replace(',', ' '),
    ]

    if lead.contact:
        lines.append(f'Контакт: {lead.contact}')
    if getattr(lead, 'user', None):
        who = lead.user.email or lead.user.get_username()
        lines.append(f'Аккаунт: {who}')

    if lead.breakdown:
        lines.append('')
        lines.append('Состав:')
        lines.extend(f'  · {item}' for item in lead.breakdown)

    lines.append('')
    lines.append(f'Время: {lead.created_at:%d.%m.%Y %H:%M}')
    if admin_url:
        lines.append(admin_url)

    return '\n'.join(lines)


def _send_telegram(text):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not (token and chat_id):
        return False

    # Imported lazily: requests is already a transitive dependency of
    # mozilla-django-oidc, but keeping the import here means a missing
    # package degrades to "no telegram" instead of breaking startup.
    import requests

    response = requests.post(
        _TELEGRAM_API.format(token=token),
        json={'chat_id': chat_id, 'text': text, 'disable_web_page_preview': True},
        timeout=10,
    )
    response.raise_for_status()
    return True


def _send_email(text, lead):
    recipient = getattr(settings, 'LEAD_NOTIFY_EMAIL', '')
    if not recipient:
        return False

    send_mail(
        subject=f'Заявка: {lead.service_label or lead.service_type} — {lead.total:,} ₸'.replace(',', ' '),
        message=text,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        recipient_list=[recipient],
        fail_silently=False,
    )
    return True


def _deliver(lead, admin_url):
    text = _format_lead(lead, admin_url)

    for channel, sender in (('telegram', lambda: _send_telegram(text)),
                            ('email', lambda: _send_email(text, lead))):
        try:
            if sender():
                logger.info('Lead #%s notified via %s', lead.pk, channel)
        except Exception:
            # A dead channel must not stop the other one, and must never
            # surface to the customer — their lead is already saved.
            logger.exception('Lead #%s: %s notification failed', lead.pk, channel)


def notify_new_lead(lead, request=None):
    """Fire notifications for a freshly created lead. Returns immediately."""
    admin_url = None
    if request is not None:
        try:
            path = reverse('admin:orders_orderlead_change', args=[lead.pk])
            admin_url = request.build_absolute_uri(path)
        except Exception:
            logger.debug('Could not build admin URL for lead #%s', lead.pk)

    if not (getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
            or getattr(settings, 'LEAD_NOTIFY_EMAIL', '')):
        logger.info('Lead #%s saved; no notification channel configured', lead.pk)
        return

    threading.Thread(
        target=_deliver, args=(lead, admin_url), daemon=True,
        name=f'lead-notify-{lead.pk}',
    ).start()
