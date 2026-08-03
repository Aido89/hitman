from django.contrib import admin

from .models import OrderLead


@admin.register(OrderLead)
class OrderLeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "service_label", "total", "contact", "status")
    list_filter = ("status", "service_type")
    list_editable = ("status",)
    search_fields = ("service_label", "contact", "user__email", "user__username")
    readonly_fields = ("created_at", "user", "service_type", "service_label", "total", "breakdown")
