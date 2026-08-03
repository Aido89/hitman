from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def login_view(request):
    """Dedicated login page: Google (Keycloak OIDC) as the primary path,
    plus a classic email/password form for staff accounts."""
    # Only same-site paths are honoured — an absolute URL here would be an
    # open redirect straight off the login page.
    next_url = request.GET.get('next') or ''
    if not next_url.startswith('/') or next_url.startswith('//'):
        next_url = ''

    if request.user.is_authenticated:
        return redirect(next_url or '/')

    error = None
    if request.method == 'POST':
        ident = request.POST.get('login', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=ident, password=password)
        if user is None and '@' in ident:
            # Staff accounts may have username != email — allow email login too.
            match = User.objects.filter(email__iexact=ident).first()
            if match:
                user = authenticate(request, username=match.username, password=password)
        if user is not None:
            django_login(request, user)
            return redirect(next_url or '/')
        error = 'Неверный email/логин или пароль.'

    return render(request, 'accounts/login.html', {'error': error, 'next_url': next_url})


def logout_view(request):
    """Log out of Django and, for OIDC sessions, end the Keycloak SSO
    session too — otherwise the person would still have an active
    Keycloak SSO session and could get silently signed back in.

    Keycloak's end_session_endpoint requires id_token_hint, which only
    exists for users who actually logged in via OIDC (not e.g. a plain
    Django admin login), so we only redirect there when we have one.
    """
    id_token = request.session.get('oidc_id_token')
    django_logout(request)

    if not id_token:
        return redirect(settings.LOGOUT_REDIRECT_URL)

    post_logout_uri = request.build_absolute_uri('/')
    params = {
        'post_logout_redirect_uri': post_logout_uri,
        'id_token_hint': id_token,
    }
    return redirect(f'{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urlencode(params)}')
