from django.conf import settings
from django.db import models


class OrderLead(models.Model):
    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новая"),
        (STATUS_IN_PROGRESS, "В работе"),
        (STATUS_CLOSED, "Закрыта"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    service_type = models.CharField(max_length=32)
    service_label = models.CharField(max_length=200)
    total = models.PositiveIntegerField(default=0)
    breakdown = models.JSONField(default=list, blank=True)
    contact = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.service_label} — {self.total}₸ ({self.get_status_display()})"
