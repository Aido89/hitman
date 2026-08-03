import json

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import OrderLead
from .notifications import notify_new_lead

SERVICE_LABELS = {
    "it-infra": "Аудит и настройка IT-инфраструктуры",
    "streaming": "Онлайн-трансляция / Студийная съемка",
    "training": "Обучение и тренинги",
    "consulting": "Консалтинг / AI-разработка",
    "videography": "Видеография и фотосъемка",
    "repair": "Ремонт и обслуживание техники",
    "webdev": "Создание сайтов и сервисов",
}

# An open POST endpoint that writes rows is a spam target. These limits stop
# casual bots without getting in a real customer's way — nobody legitimately
# files six quotes an hour.
RATE_LIMIT_PER_HOUR = 5
RATE_LIMIT_WINDOW = 60 * 60


def _client_ip(request):
    """Real client IP behind the nginx ingress."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _rate_limited(request):
    """True when this client has already filed too many leads recently.

    Backed by the default local-memory cache, so with several replicas the
    effective limit is per-pod rather than global. That is fine for the goal
    here (stopping drive-by bots); a determined attacker needs a real shared
    cache, which is a bigger change than this problem warrants today.
    """
    if request.user.is_authenticated:
        return False  # a known account is accountable; don't throttle it

    key = f'lead-rate:{_client_ip(request)}'
    count = cache.get(key, 0)
    if count >= RATE_LIMIT_PER_HOUR:
        return True
    cache.set(key, count + 1, RATE_LIMIT_WINDOW)
    return False


def constructor(request):
    """Open to everyone: a visitor must be able to see a price before being
    asked for anything. Login is a convenience (order history), not a gate."""
    return render(request, "orders/constructor.html", {"service_labels": SERVICE_LABELS})


@require_POST
def submit_lead(request):
    try:
        payload = json.loads(request.body)
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "error": "invalid payload"}, status=400)

    # Bots fill in every field they find; humans never see this one.
    if payload.get("website"):
        return JsonResponse({"ok": True, "id": None})

    contact = (payload.get("contact") or "").strip()
    if len(contact) < 5:
        return JsonResponse(
            {"ok": False, "error": "Укажите контакт, чтобы мы могли ответить."},
            status=400,
        )

    if _rate_limited(request):
        return JsonResponse(
            {"ok": False, "error": "Слишком много заявок подряд. Напишите нам в WhatsApp."},
            status=429,
        )

    try:
        lead = OrderLead.objects.create(
            user=request.user if request.user.is_authenticated else None,
            service_type=payload.get("serviceType", ""),
            service_label=payload.get("serviceLabel", ""),
            total=int(payload.get("total") or 0),
            breakdown=payload.get("breakdown") or [],
            contact=contact,
        )
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "error": "invalid payload"}, status=400)

    # Fire-and-forget: never lets a notification failure fail the lead.
    notify_new_lead(lead, request)
    return JsonResponse({"ok": True, "id": lead.pk})


@login_required
def my_orders(request):
    """Stays gated — this is the customer's own data."""
    leads = request.user.orders.all()
    return render(request, "orders/my_orders.html", {"leads": leads})
