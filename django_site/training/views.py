import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import data
from .models import CourseModule


def modules_json():
    modules = [
        {
            'id': m.module_id,
            'icon': m.icon,
            'title': {'ru': m.title_ru, 'kk': m.title_kk},
            'content': {'ru': m.content_ru, 'kk': m.content_kk},
        }
        for m in CourseModule.objects.all()
    ]
    return json.dumps(modules, ensure_ascii=False)


@login_required
def course(request):
    return render(request, "training/course.html", {
        "modules_json": modules_json(),
        "bonus_ideas_json": json.dumps(data.BONUS_IDEAS, ensure_ascii=False),
        "materials_ids_json": json.dumps(data.MATERIALS_MODULE_IDS),
        "materials_video": data.MATERIALS_VIDEO,
    })
