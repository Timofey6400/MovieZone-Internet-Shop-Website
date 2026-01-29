from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Case, When
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Film, Category, PromoCode
from .forms import UserRegisterForm, UserLoginForm, SearchForm

def cart_view(request):
    cart = request.session.get('cart', {})
    # cart is mapping slug->quantity
    films = Film.objects.filter(slug__in=cart.keys())
    # attach quantity to each film object for template
    films_with_qty = []
    for f in films:
        qty = cart.get(f.slug, 0)
        films_with_qty.append((f, qty))
    total = sum(f.price * qty for f, qty in films_with_qty)
    return render(request, 'films/cart.html', {'items': films_with_qty, 'total': total})

def cart_add(request, slug):
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    cart = request.session.get('cart', {})
    cart[slug] = cart.get(slug, 0) + 1
    request.session['cart'] = cart
    messages.success(request, 'Товар добавлен в корзину')
    return redirect(next_url)

def cart_remove(request, slug):
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    cart = request.session.get('cart', {})
    if slug in cart:
        del cart[slug]
        request.session['cart'] = cart
        messages.success(request, 'Товар удален из корзины')
    return redirect(next_url)

def index(request):
    form = SearchForm(request.GET)
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    featured_only = request.GET.get("featured", "") == "on"

    films = Film.objects.filter()

    # Поиск по тексту
    if query:
            films = films.filter(
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(description__icontains=query)
            ).order_by(
                Case(
                    When(title__icontains=query, then=0),
                    default=1
                )
            )
    # Фильтр по категории
    if category_slug:
        films = films.filter(category__slug=category_slug)
    
    # Фильтр по цене
    if min_price:
        try:
            films = films.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            films = films.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Фильтр по рекомендуемым
    if featured_only:
        films = films.filter(featured=True)
    
    films = films.order_by('-featured', '-created_at')[:50]
    categories = Category.objects.filter(is_active=True)
    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug, is_active=True).first()
    total_films_count = Film.objects.count()
    
    return render(request, "films/index.html", {
        "films": films, 
        "categories": categories, 
        "query": query,
        "selected_category": selected_category,
        "total_films_count": total_films_count,
        "search_form": form,
        "min_price": min_price,
        "max_price": max_price,
        "featured_only": featured_only
    })

def film_detail(request, slug):
    film = get_object_or_404(Film, slug=slug)

    final_price = film.price
    promo_error = None
    promo_code_value = ""

    if request.method == "POST":
        promo_code_value = request.POST.get("promo_code")

        try:
            promo = PromoCode.objects.get(code__iexact=promo_code_value)

            if promo.is_valid():
                final_price = film.get_price_with_promo(promo)
            else:
                promo_error = "Промокод недействителен"

        except PromoCode.DoesNotExist:
            promo_error = "Промокод не найден"

    return render(request, "films/film_detail.html", {
        "film": film,
        "final_price": final_price,
        "promo_error": promo_error,
        "promo_code_value": promo_code_value,
    })

# Простая реализация "избранного" через сессию
def favorites_toggle(request, slug):
    favs = request.session.get("favorites", [])
    if slug in favs:
        favs.remove(slug)
    else:
        favs.append(slug)
    request.session["favorites"] = favs
    # redirect обратно на страницу откуда пришли или на деталь
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)

def favorites_list(request):
    favs = request.session.get("favorites", [])
    films = Film.objects.filter(slug__in=favs)
    return render(request, "films/favorites.html", {"films": films})

def community(request):
    """Страница сообщества"""
    return render(request, "films/community.html")

def library(request):
    """Страница библиотеки фильмов пользователя"""
    # Получаем фильмы из сессии (можно расширить для реальной библиотеки)
    library_slugs = request.session.get("library", [])
    films = Film.objects.filter(slug__in=library_slugs)
    return render(request, "films/library.html", {"films": films})

def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            login(request, user)
            return redirect('films:index')
    else:
        form = UserRegisterForm()
    return render(request, 'films/register.html', {'form': form})

def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'films/login.html', {'form': form})

@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('films:index')

def search(request):
    """Расширенный поиск"""
    form = SearchForm(request.GET)
    films = Film.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('q', '')
        category_slug = form.cleaned_data.get('category', '')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        featured_only = form.cleaned_data.get('featured', False)
        
        if query:
            films = films.filter(
                Q(title__icontains=query) | 
                Q(short_description__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category_slug:
            films = films.filter(category__slug=category_slug)
        
        if min_price:
            films = films.filter(price__gte=min_price)
        if max_price:
            films = films.filter(price__lte=max_price)
        
        if featured_only:
            films = films.filter(featured=True)
    
    films = films.order_by('-featured', '-created_at')[:100]
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'films/search.html', {
        'form': form,
        'films': films,
        'categories': categories
    })