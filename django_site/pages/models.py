from django.db import models

from .gallery import CATEGORIES


class HeroSlide(models.Model):
    """A slide in the homepage hero banner — managed from /admin/ instead of
    being hand-edited in templates/pages/home.html on every content change.
    """
    order = models.PositiveIntegerField(default=0, help_text="Меньше — выше по очереди.")
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='hero/')
    kicker = models.CharField(max_length=80, blank=True, help_text='Маленькая строка сверху, например: // Продакшн')
    title_line1 = models.CharField(max_length=60)
    title_line2 = models.CharField(max_length=60, blank=True)
    title_accent = models.CharField(max_length=60, blank=True, help_text='Последняя строка заголовка — выделяется красным.')
    lead = models.CharField(max_length=300, blank=True)
    stats = models.CharField(max_length=200, blank=True, help_text='Необязательная строка цифр под текстом.')
    cta_label = models.CharField(max_length=60, blank=True)
    cta_url = models.CharField(max_length=300, blank=True, help_text='Например /smeta/ или полный https://…')
    secondary_cta_label = models.CharField(max_length=60, blank=True)
    secondary_cta_url = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title_line1 or f'Слайд #{self.pk}'


class GalleryPhoto(models.Model):
    """A gallery photo uploaded through /admin/.

    pages/gallery.py merges these with the photos dropped straight into
    static/img/gallery/<category>/ — the two ways of adding a photo (upload
    here, or hand a file to whoever can deploy) both keep working.
    """
    CATEGORY_CHOICES = [(c['slug'], c['title']) for c in CATEGORIES]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.caption or f'Фото #{self.pk}'


ICON_CHOICES = [(f'img/icons/{n}.svg', n) for n in (
    'briefcase', 'bulb', 'camera', 'cap', 'globe', 'headphones',
    'layers', 'rocket', 'server', 'sliders', 'target', 'video', 'wrench',
)]


class HomeSection(models.Model):
    """One of the "Направления" cards on the homepage — editable from
    /admin/ instead of the hardcoded HOME_SECTIONS list in pages/data.py.
    """
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=100, choices=ICON_CHOICES)
    title = models.CharField(max_length=150)
    desc = models.CharField(max_length=300, blank=True)
    href = models.CharField(max_length=300, help_text='Путь страницы, например /services/ или /smeta/')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """A client quote in the "Отзывы и доверие" slider on the homepage."""
    order = models.PositiveIntegerField(default=0)
    text = models.TextField()
    name = models.CharField(max_length=150, help_text='Компания или мероприятие')
    role = models.CharField(max_length=150, blank=True, help_text='Контактное лицо / роль')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class Metric(models.Model):
    """One "В цифрах" stat on /services/ — a big number plus its caption."""
    order = models.PositiveIntegerField(default=0)
    number = models.CharField(max_length=20, help_text='Например: 700+')
    desc = models.CharField(max_length=300)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.number


class Case(models.Model):
    """A project write-up on /cases/ — task/what-we-did/result plus small stats and tags."""
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    client = models.CharField(max_length=200, blank=True)
    task = models.TextField()
    done = models.TextField()
    result = models.TextField()
    metrics = models.JSONField(default=list, blank=True, help_text='[["99.9%", "Доступность"], ...]')
    tags = models.JSONField(default=list, blank=True, help_text='["Entra ID", "Intune", ...]')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class RepairWarranty(models.Model):
    """One-line warranty banner shown above the repair price table on /services/.

    Deliberately a single-row model rather than a bare constant: the text is
    real editable content, and the admin already knows this "add one row,
    edit it" pattern from every other model here.
    """
    text = models.CharField(max_length=200, default='1 год гарантии на все виды работ')

    class Meta:
        verbose_name = 'Гарантия (ремонт)'
        verbose_name_plural = 'Гарантия (ремонт)'

    def __str__(self):
        return self.text


class RepairPriceGroup(models.Model):
    """A priced group in the repair table on /services/ (e.g. "Ремонт ноутбука")."""
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=150)
    note = models.CharField(max_length=300, blank=True)
    items = models.JSONField(default=list, help_text='[["Замена матрицы", "от 20 000 ₸"], ...]')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """A post on /blog/ — editable from /admin/ instead of BLOG_POSTS in pages/data.py."""
    order = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=150)
    title = models.CharField(max_length=200)
    excerpt = models.CharField(max_length=300)
    read_time = models.CharField(max_length=20, blank=True, help_text='Например: 10 мин')
    year = models.CharField(max_length=10, blank=True)
    intro = models.TextField()
    body = models.JSONField(
        default=list,
        help_text='Список блоков: [["h2", "Заголовок"], ["p", "Текст"], ["quote", "Цитата"], ...]',
    )
    author = models.CharField(max_length=150, blank=True)
    author_role = models.CharField(max_length=150, blank=True)
    cta = models.CharField(max_length=60, blank=True, help_text='Текст кнопки внизу статьи')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ServiceCard(models.Model):
    """A service on /services/ — title, audience, price, description and the
    tech/work breakdown — editable from /admin/ instead of the SERVICE_CARDS
    list in pages/data.py.
    """
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=100, choices=ICON_CHOICES)
    image = models.CharField(
        max_length=300, blank=True,
        help_text='Путь в static/, например img/gallery/infra/rack--....jpeg. '
                   'Файл должен уже лежать в static/ — это не загрузка, а ссылка на существующее фото.',
    )
    title = models.CharField(max_length=150)
    audience = models.CharField(max_length=150, blank=True)
    price_from = models.CharField(max_length=40, blank=True, help_text='Например: 120 000 ₸. Пусто — покажется «Цена по задаче».')
    desc = models.TextField(blank=True)
    groups = models.JSONField(
        default=list, blank=True,
        help_text='Список групп технологий: [["Название группы", ["тег1", "тег2"]], ...]',
    )
    with_ai = models.BooleanField(default=False, help_text='Показывать кнопку «AI-консультация».')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
