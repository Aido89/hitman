from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve as serve_static

from pages.sitemaps import SITEMAPS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('accounts/', include('accounts.urls')),
    path('smeta/', include('orders.urls')),
    path('training/', include('training.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('', include('pages.urls')),
    # ponytail: no nginx/CDN in front of this deployment (see k8s/deployment.yaml),
    # so Django serves MEDIA itself in prod too — whitenoise only covers STATIC.
    # Fine at this traffic level; move to nginx/S3 if uploads get heavy.
    re_path(r'^media/(?P<path>.*)$', serve_static, {'document_root': settings.MEDIA_ROOT}),
]
