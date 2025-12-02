from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.urls import reverse

from main.forms import ThemeForm, SubThemeForm
from main.models import *


# Create your views here.

def index_page(request):
    return render(request, "index.html")


class ThemesList(ListView):
    model = Theme
    template_name = 'themes/list.html'


def theme_view_page(request, id):
    theme = get_object_or_404(Theme, id=id)
    subthemes = SubTheme.objects.all()
    articles = Article.objects.all()
    return render(request, "themes/view.html", {"theme": theme, "subthemes": subthemes, "articles": articles})


def theme_add_page(request):
    if request.method == "GET":
        form = ThemeForm()
        return render(request, "themes/add.html", {"form": form})
    form = ThemeForm(request.POST)
    if form.is_valid():
        new_theme = Theme(title=form.cleaned_data['title'])
        new_theme.save()
        return redirect(reverse("theme_view", kwargs={"id": new_theme.id}))
    else:
        return render(request, "themes/add.html", {"form": form})


def theme_edit_page(request, id):
    theme = get_object_or_404(Theme, id=id)
    if request.method == "GET":
        form = ThemeForm(initial={"title": theme.title})
        return render(request, "themes/edit.html", {"form": form, "theme": theme})
    form = ThemeForm(request.POST)
    if form.is_valid():
        theme.title = form.cleaned_data['title']
        theme.save()
        return redirect(reverse("theme_view", kwargs={"id": theme.id}))
    else:
        return render(request, "themes/edit.html", {"form": form})


def theme_delete_page(request, id):
    if request.method == "GET":
        return redirect(reverse('theme_edit', kwargs={"id": id}))
    theme = get_object_or_404(Theme, id=id)
    theme.delete()
    return redirect(reverse('themes_list'))


def subtheme_view_page(request, t_id, st_id):
    theme = get_object_or_404(Theme, id=t_id)
    subtheme = get_object_or_404(SubTheme, id=st_id)
    return render(request, "subthemes/view.html", {"theme": theme, "subtheme": subtheme})


def subtheme_edit_page(request, t_id, st_id):
    theme = get_object_or_404(Theme, id=t_id)
    subtheme = get_object_or_404(SubTheme, id=st_id)
    article = subtheme.articles.first()
    if request.method == "GET":
        form = SubThemeForm(initial={"title": subtheme.title, "text": article.text})
        return render(request, "subthemes/edit.html", {"form": form, "theme": theme, "subtheme": subtheme})
    form = SubThemeForm(request.POST)
    if form.is_valid():
        subtheme.title = form.cleaned_data['title']
        article.text = form.cleaned_data['text']
        subtheme.save()
        article.save()
        return redirect(reverse("subtheme_view", kwargs={"t_id": theme.id, "st_id": subtheme.id}))
    else:
        return render(request, "subthemes/edit.html", {"form": form, "theme": theme, "subtheme": subtheme})


def subtheme_add_page(request, t_id):
    theme = get_object_or_404(Theme, id=t_id)
    if request.method == "GET":
        form = SubThemeForm()
        return render(request, "subthemes/add.html", {"form": form, "theme": theme})
    form = SubThemeForm(request.POST)
    if form.is_valid():
        new_subtheme = SubTheme(title=form.cleaned_data['title'])
        new_subtheme.theme = theme
        new_subtheme.save()
        new_article = Article(text=form.cleaned_data['text'])
        new_article.subtheme = new_subtheme
        new_article.save()
        return redirect(reverse("subtheme_view", kwargs={"t_id": theme.id, "st_id": new_subtheme.id}))
    else:
        return render(request, "subthemes/add.html", {"form": form})


def subtheme_delete_page(request, t_id, st_id):
    if request.method == "GET":
        return redirect(reverse('subtheme_edit', kwargs={"t_id": t_id, "st_id": st_id}))

    subtheme = get_object_or_404(SubTheme, id=st_id)
    article = subtheme.articles.first()
    article.delete()
    subtheme.delete()
    return redirect(reverse('theme_view', kwargs={"id": t_id}))
