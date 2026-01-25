from django.db import models
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal


class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percent', 'Процент'),
        ('fixed', 'Фиксированная сумма'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    films = models.ManyToManyField(
        'Film',
        blank=True,
        related_name='promo_codes'
    )

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def __str__(self):
        return self.code

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

    def get_price_with_promo(self, promo: PromoCode | None = None):
        if not promo:
            return self.price

        if not promo.is_valid():
            return self.price

        if promo.films.exists() and self not in promo.films.all():
            return self.price

        if promo.discount_type == 'percent':
            discount = self.price * Decimal(promo.discount_value) / 100
        else:
            discount = Decimal(promo.discount_value)

        return max(self.price - discount, 0)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('films:film_detail', args=[self.slug])
