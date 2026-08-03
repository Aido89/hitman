"""Photo and video gallery.

Photos are discovered from the filesystem rather than listed in code: drop a
file into `static/img/gallery/<category>/` and it shows up. That keeps adding
work photos a non-developer task — no code edit, no deploy of a data file.

Captions are optional. A file named `boxing-ring--Финал чемпионата.jpg` renders
with that caption; without the `--` part the filename is just an alt hint and
no caption is shown. Anything unnamed still displays — a photo without a
caption is far better than a photo nobody uploaded because naming felt fiddly.

Videos stay declared in code (VIDEOS below): they live on YouTube, so there is
no file to discover.
"""

from pathlib import Path

from django.conf import settings
from django.templatetags.static import static as static_url

GALLERY_ROOT = Path(settings.BASE_DIR) / 'static' / 'img' / 'gallery'

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp', '.avif'}

# Order here is the order categories appear in the filter bar.
CATEGORIES = [
    {'slug': 'streaming', 'title': 'Трансляции', 'service': 'Видеостриминг и студийная съемка'},
    {'slug': 'events', 'title': 'Мероприятия', 'service': 'Видеостриминг и студийная съемка'},
    {'slug': 'podcast', 'title': 'Студия и подкасты', 'service': 'Видеостриминг и студийная съемка'},
    {'slug': 'infra', 'title': 'IT-инфраструктура', 'service': 'IT-инфраструктура и кибербезопасность'},
    {'slug': 'training', 'title': 'Обучение', 'service': 'Обучение и тренинги (цифровые навыки, ИИ)'},
    {'slug': 'photo', 'title': 'Фото и видеосъёмка', 'service': 'Видеостриминг и студийная съемка'},
]

# Files dropped straight into the gallery root instead of a category folder.
# Without this they'd be silently invisible — the worst possible outcome for
# someone who just uploaded 60 photos and sees an empty page.
UNSORTED = {'slug': '', 'title': 'Разное', 'service': ''}

CATEGORY_BY_SLUG = {c['slug']: c for c in CATEGORIES}
CATEGORY_BY_SLUG[''] = UNSORTED

# YouTube videos. `youtube_id` is the part after v= in the watch URL.
VIDEOS = [
    # {'youtube_id': 'XXXXXXXXXXX', 'title': 'Финал чемпионата',
    #  'category': 'streaming', 'caption': 'Многокамерная трансляция'},
]


def _caption_from_filename(stem):
    """`boxing-ring--Финал чемпионата` -> ('Финал чемпионата', 'boxing ring')."""
    if '--' in stem:
        slug, caption = stem.split('--', 1)
        return caption.strip(), slug.replace('-', ' ').strip()
    return '', stem.replace('-', ' ').strip()


def photos(category=None):
    """Every photo, newest first, optionally filtered by category.

    Two sources, merged: files dropped straight into static/img/gallery/ (no
    code, no deploy — see the module docstring) and GalleryPhoto rows added
    through /admin/. `src` is a ready-to-use URL for both, so templates never
    need to know which source a photo came from.
    """
    if category is not None:
        slugs = [category]
    else:
        slugs = [c['slug'] for c in CATEGORIES] + ['']
    found = []

    for slug in slugs:
        folder = GALLERY_ROOT / slug if slug else GALLERY_ROOT
        if not folder.is_dir():
            continue
        for path in folder.iterdir():
            # Skip macOS AppleDouble turds and any non-image.
            if path.name.startswith('._') or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            caption, alt = _caption_from_filename(path.stem)
            rel = f'img/gallery/{slug}/{path.name}' if slug else f'img/gallery/{path.name}'
            found.append({
                'src': static_url(rel),
                'caption': caption,
                'alt': caption or alt,
                'category': slug,
                'category_title': CATEGORY_BY_SLUG[slug]['title'],
                'mtime': path.stat().st_mtime,
            })

    from .models import GalleryPhoto  # local import: models.py imports CATEGORIES from here
    db_qs = GalleryPhoto.objects.all()
    if category is not None:
        db_qs = db_qs.filter(category=category)
    for p in db_qs:
        found.append({
            'src': p.image.url,
            'caption': p.caption,
            'alt': p.caption or p.get_category_display(),
            'category': p.category,
            'category_title': CATEGORY_BY_SLUG[p.category]['title'],
            'mtime': p.created_at.timestamp(),
        })

    found.sort(key=lambda item: item['mtime'], reverse=True)
    return found


def videos(category=None):
    if category:
        return [v for v in VIDEOS if v.get('category') == category]
    return list(VIDEOS)


def used_categories():
    """Only categories that actually have something — no empty filter tabs.

    The count rides along on each category: Django templates can't look a dict
    up by a variable key without a custom filter, and a filter would be a lot
    of machinery for one number.
    """
    per = counts()
    cats = [dict(c, count=per[c['slug']]) for c in CATEGORIES if per.get(c['slug'])]
    if per.get(''):
        cats.append(dict(UNSORTED, count=per['']))
    return cats


def counts():
    per = {}
    for p in photos():
        per[p['category']] = per.get(p['category'], 0) + 1
    for v in VIDEOS:
        slug = v.get('category')
        per[slug] = per.get(slug, 0) + 1
    return per
