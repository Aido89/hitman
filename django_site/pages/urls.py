from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("skills/", views.skills, name="skills"),
    path("cases/", views.cases, name="cases"),
    path("gallery/", views.gallery_page, name="gallery"),
    path("formats/", views.formats, name="formats"),
    path("blog/", views.blog_index, name="blog_index"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
]
