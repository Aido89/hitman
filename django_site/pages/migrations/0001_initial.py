from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, help_text='Меньше — выше по очереди.')),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.ImageField(upload_to='hero/')),
                ('kicker', models.CharField(blank=True, max_length=80, help_text='Маленькая строка сверху, например: // Продакшн')),
                ('title_line1', models.CharField(max_length=60)),
                ('title_line2', models.CharField(blank=True, max_length=60)),
                ('title_accent', models.CharField(blank=True, max_length=60, help_text='Последняя строка заголовка — выделяется красным.')),
                ('lead', models.CharField(blank=True, max_length=300)),
                ('stats', models.CharField(blank=True, max_length=200, help_text='Необязательная строка цифр под текстом.')),
                ('cta_label', models.CharField(blank=True, max_length=60)),
                ('cta_url', models.CharField(blank=True, max_length=300, help_text='Например /smeta/ или полный https://…')),
                ('secondary_cta_label', models.CharField(blank=True, max_length=60)),
                ('secondary_cta_url', models.CharField(blank=True, max_length=300)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='GalleryPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
                ('image', models.ImageField(upload_to='gallery/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
