from django.contrib import admin
from .models import Category, Platform, Film, PromoCode

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "icon", "order", "is_active", "films_count")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "slug", "icon", "description")
        }),
        ("Настройки", {
            "fields": ("order", "is_active")
        }),
    )

    def films_count(self, obj):
        """Отображает количество фильмов в категории"""
        return obj.get_films_count()
    films_count.short_description = "Фильмов"

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "featured")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("category", "platforms", "featured")
    search_fields = ("title", "short_description", "description")

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount_type',
        'discount_value',
        'is_active',
        'valid_from',
        'valid_to',
        'used_count',
    )
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)