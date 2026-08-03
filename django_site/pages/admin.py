from django.contrib import admin
from django.utils.html import format_html

from .models import (
    BlogPost, Case, GalleryPhoto, HeroSlide, HomeSection, Metric,
    RepairPriceGroup, RepairWarranty, ServiceCard, Testimonial,
)


def thumb(obj, field='image', height=48):
    file = getattr(obj, field)
    if not file:
        return '—'
    return format_html('<img src="{}" style="height:{}px;border:1px solid #333">', file.url, height)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title_line1', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    ordering = ('order',)

    @admin.display(description='Фото')
    def preview(self, obj):
        return thumb(obj)


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ('preview', 'caption', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('caption',)
    ordering = ('-created_at',)

    @admin.display(description='Фото')
    def preview(self, obj):
        return thumb(obj)


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'href', 'order')
    list_editable = ('href', 'order')
    ordering = ('order',)


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_from', 'audience', 'order')
    list_editable = ('price_from', 'order')
    ordering = ('order',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    ordering = ('order',)


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('desc', 'number', 'order')
    list_editable = ('number', 'order')
    ordering = ('order',)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'order')
    list_editable = ('order',)
    ordering = ('order',)


@admin.register(RepairWarranty)
class RepairWarrantyAdmin(admin.ModelAdmin):
    list_display = ('text',)


@admin.register(RepairPriceGroup)
class RepairPriceGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'note', 'order')
    list_editable = ('order',)
    ordering = ('order',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'year', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'category')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)
