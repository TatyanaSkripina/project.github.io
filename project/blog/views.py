from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Category, Article, Comment, Profile
from .forms import ArticleForm, LoginForm, RegistrationForm, CommentForm, EditAccountForm, EditProfileForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, logout
from django.contrib import messages


# Create your views here.

# def index(request):
#     categories = Category.objects.all()
#     articles = Article.objects.all()
#     context = {
#         'title': 'Главная страница',
#         'categories': categories,
#         'articles': articles
#     }
#     return render(request, 'blog/index.html', context)

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    extra_context = {
        'title': 'Главная страница'
    }


# def category_view(request, pk):
#     categories = Category.objects.all()
#     articles = Article.objects.filter(category_id=pk)
#     category = Category.objects.get(pk=pk)
#     context = {
#         'title': f'Категория: {category.title}',
#         'categories': categories,
#         'articles': articles
#     }
#     return render(request, 'blog/index.html', context)

class ArticleListByCategory(ArticleListView):
    def get_queryset(self):
        articles = Article.objects.filter(category_id=self.kwargs['pk'])
        return articles

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['title'] = f'Категория: {category.title}'
        return context


# def article_view(request, pk):
#     article = Article.objects.get(pk=pk)
#     context = {
#         'title': f'Статья: {article.title}',
#         'article': article
#     }
#     return render(request, 'blog/article_detail.html', context)

class ArticleDetailView(DetailView):
    model = Article
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        article = Article.objects.get(pk=self.kwargs['pk'])
        article.views += 1
        article.save()
        context['title'] = f'Статья: {article.title}'
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(article=article)
        return context


def main_article_view(request):
    article = Article.objects.all()
    context = {
        'title': f'Основная статья',
        'article': article
    }
    return render(request, 'blog/main_article_detail.html', context)


# def add_article(request):
#     if request.method == 'POST':
#         form = ArticleForm(request.POST, request.FILES)
#         if form.is_valid():
#             article = Article.objects.create(**form.cleaned_data)
#             article.save()
#             return redirect('article',article.pk)
#     else:
#         form = ArticleForm()
#     context = {
#         'form': form,
#         'title': 'Создание статьи'
#     }
#     return render(request, 'blog/add_article.html', context)

class NewArticle(CreateView):
    form_class = ArticleForm
    template_name = 'blog/add_article.html'
    extra_context = {
        'title': 'Создание статьи'
    }

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdate(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/add_article.html'


class ArticleDelete(DeleteView):
    model = Article
    context_object_name = 'article'
    success_url = reverse_lazy('index')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в аккаунт')
                return redirect('index')
            else:
                messages.error(request, 'Не верное имя пользователя или пароль')
                return redirect('index')
        else:
            messages.error(request, 'Не верное имя пользователя или пароль')
            return redirect('index')


def user_logout(request):
    logout(request)
    messages.warning(request, 'Вы вышли из аккаунта')
    return redirect('index')


class SearchResults(ArticleListView):
    def get_queryset(self):
        word = self.request.GET.get('q')
        articles = Article.objects.filter(title__icontains=word)
        return articles


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(user=user)
            profile.save()
            messages.success(request, 'Вы успешно зарегитсрировались. Войдите в аккаунт')
            return redirect('index')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text)
            return redirect('index')


def save_comment(request, pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = Article.objects.get(pk=pk)
        comment.user = request.user
        comment.save()
        messages.success(request, 'Ваш комментарий опубликован')
        return redirect('article', pk)


def profile_view(request, pk):
    profile = Profile.objects.get(user_id=pk)
    articles = Article.objects.filter(author_id=pk)
    most_viewed = articles.order_by('-views')[:1][0]
    recent_articles = articles.order_by('-created_at')[:1][0]
    context = {
        'profile': profile,
        'most_viewed': most_viewed,
        'recent_articles': recent_articles,
        'articles': articles
    }
    return render(request, 'blog/profile.html', context)


def edit_account_view(request):
    if request.method == 'POST':
        form = EditAccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            user = request.user
            return redirect('profile', user.pk)
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
        user = request.user
        return redirect('profile', user.pk)


def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
        user = request.user
        return redirect('profile', user.pk)


def about_us(request):
    article = Article.objects.all()
    context = {
        'title': f'Информация о нас',
        'article': article
    }
    return render(request, 'blog/about_us.html', context)