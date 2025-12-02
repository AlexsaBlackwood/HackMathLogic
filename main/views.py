from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from main.forms import ThemeForm, SubThemeForm
from main.models import *


# Create your views here.

def index_page(request):
    return render(request, "index.html")


class ThemesList(ListView):
    model = Theme
    template_name = 'themes/list.html'


class ThemesView(DetailView):
    model = Theme
    template_name = 'themes/view.html'
    pk_url_kwarg = 'id'


class ThemeAddView(CreateView):
    model = Theme
    fields = ["title"]
    template_name = 'themes/add.html'


class ThemeEditView (UpdateView):
    model = Theme
    fields = ["title"]
    template_name = 'themes/edit.html'
    pk_url_kwarg = 'id'


class ThemeDeleteView (DeleteView):
    model = Theme
    template_name = 'themes/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy("themes_list")


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
