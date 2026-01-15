from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=50, blank=True, default="🎮", verbose_name="Иконка")
    order = models.IntegerField(default=0, verbose_name="Порядок сортировки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_films_count(self):
        """Возвращает количество фильмов в категории"""
        return self.films.count()

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Film(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, related_name='films', on_delete=models.SET_NULL, null=True, blank=True)
    platforms = models.ManyToManyField(Platform, blank=True)
    release_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    image = models.URLField(blank=True)  # упрощённо: URL обложки
    image_file = models.ImageField(upload_to='film_images/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('films:film_detail', args=[self.slug])
