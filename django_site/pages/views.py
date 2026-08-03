from django.http import Http404
from django.shortcuts import redirect, render

from . import data, gallery
from .models import (
    BlogPost, Case, HeroSlide, HomeSection, Metric,
    RepairPriceGroup, RepairWarranty, ServiceCard, Testimonial,
)


def home(request):
    return render(request, "pages/home.html", {
        "sections": HomeSection.objects.all(),
        "contacts": data.CONTACTS,
        "testimonials": Testimonial.objects.all(),
        "hero_slides": HeroSlide.objects.filter(is_active=True),
    })


def about(request):
    return render(request, "pages/about.html", {"about": data.ABOUT})


def services(request):
    """One page for everything we sell.

    Previously this was three pages — «Направления», «Услуги» и «Навыки» —
    describing the same six services in different words. A visitor could not
    tell them apart, because there was nothing to tell apart.
    """
    warranty = RepairWarranty.objects.first()
    return render(request, "pages/services.html", {
        "cards": ServiceCard.objects.all(),
        "metrics": Metric.objects.all(),
        "repair_warranty": warranty.text if warranty else '',
        "repair_groups": RepairPriceGroup.objects.all(),
        "gallery_preview": gallery.photos()[:6],
        "gallery_total": len(gallery.photos()) + len(gallery.videos()),
    })


def skills(request):
    # Merged into /services/. Redirect rather than 404: the URL is in the
    # sitemap, may be bookmarked, and carries whatever ranking it earned.
    return redirect("pages:services", permanent=True)


def formats(request):
    return redirect("pages:services", permanent=True)


def gallery_page(request):
    """Photo/video gallery with category filtering.

    Filtering happens server-side so a filtered view is a shareable URL
    (/gallery/?c=streaming) and works without JS.
    """
    active = request.GET.get('c') or ''
    cats = gallery.used_categories()
    valid = {c['slug'] for c in cats}
    if active not in valid:
        active = ''

    return render(request, "pages/gallery.html", {
        "categories": cats,
        "active": active,
        "photos": gallery.photos(active or None),
        "videos": gallery.videos(active or None),
        "counts": gallery.counts(),
        "total": len(gallery.photos()) + len(gallery.videos()),
    })


def cases(request):
    return render(request, "pages/cases.html", {"cases": Case.objects.all()})


def blog_index(request):
    return render(request, "pages/blog_index.html", {"posts": BlogPost.objects.all()})


def blog_detail(request, slug):
    post = BlogPost.objects.filter(slug=slug).first()
    if not post:
        raise Http404("Post not found")
    return render(request, "pages/blog_detail.html", {"post": post})
