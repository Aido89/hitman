from django.db import models


class CourseModule(models.Model):
    """One module of the Google Workspace course — editable from /admin/
    instead of the MODULES list in training/data.py.

    `module_id` (not the DB pk) is the id training.js and MATERIALS_MODULE_IDS
    in training/data.py key off — keeping it explicit means reordering rows
    in admin never shifts which module a saved id points to.
    """
    module_id = models.PositiveIntegerField(unique=True)
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=10, blank=True, help_text='Эмодзи, например 📋')
    title_ru = models.CharField(max_length=200)
    title_kk = models.CharField(max_length=200, blank=True)
    content_ru = models.JSONField(
        default=dict,
        help_text='{"goal":"..","interactive":"..","case":"..","assignment":"..",'
                   '"practice":["..",".."],"video":"..","quiz":{"q":"..","options":["..",".."],"correct":0}}',
    )
    content_kk = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['order', 'module_id']

    def __str__(self):
        return self.title_ru
