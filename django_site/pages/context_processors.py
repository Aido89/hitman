from django.conf import settings

from . import data


def site_settings(request):
    """Expose the handful of settings templates legitimately need.

    Deliberately an allow-list: never hand the whole settings object to
    templates, or one stray `{{ settings.SECRET_KEY }}` leaks it.
    """
    return {
        'YANDEX_METRIKA_ID': settings.YANDEX_METRIKA_ID,
        'PLAUSIBLE_DOMAIN': settings.PLAUSIBLE_DOMAIN,
        'site_url': settings.SITE_URL,
        'social_links': [c for c in data.CONTACTS if not c['href'].startswith('mailto:')],
    }
