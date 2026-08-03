from django.contrib import admin

from .models import CourseModule


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('module_id', 'title_ru', 'order')
    list_editable = ('order',)
    search_fields = ('title_ru', 'title_kk')
    ordering = ('order',)
